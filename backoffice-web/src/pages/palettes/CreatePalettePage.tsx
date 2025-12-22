import { useNavigate, Link } from 'react-router-dom';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useForm, Controller } from 'react-hook-form';
import { useEffect, useMemo } from 'react';
import { zodResolver } from '@hookform/resolvers/zod';
import { paletteService, rfidTagService, centreRemplisseurService } from '../../services/api';
import { Card, CardHeader, CardTitle, CardContent, Button, Input } from '../../components/common';
import { ArrowLeft } from 'lucide-react';
import { paletteCreateSchema, PaletteCreateFormData } from '../../utils/validators';
import { useAuth } from '../../hooks/useAuth';
import { UserRole } from '../../types/user';

const CreatePalettePage = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { user } = useAuth();

  // Fetch next available code - enabled immediately when component mounts
  const { data: nextCodeData, isLoading: isLoadingCode } = useQuery({
    queryKey: ['palettes', 'next-code'],
    queryFn: () => paletteService.getNextCode(),
    enabled: true, // Always fetch on mount
  });

  const nextCode = nextCodeData?.code || '';

  // Fetch available RFID tags (NOT_ASSIGNED and active)
  const { data: rfidTagsData } = useQuery({
    queryKey: ['rfid-tags', 'available'],
    queryFn: () => rfidTagService.list({
      status: 'NOT_ASSIGNED' as any,
      is_active: true,
      page: 1,
      page_size: 100,
    }),
  });

  // Fetch centres remplisseurs
  const { data: centres } = useQuery({
    queryKey: ['centres-remplisseurs', 'palette-form'],
    queryFn: () => centreRemplisseurService.list({ limit: 100, is_active: true }),
    enabled: true,
  });

  // Determine default centre remplisseur based on user's company
  const defaultCentreId = useMemo(() => {
    if (!user?.company_name || !centres) return '';
    
    // For OPERATEUR_USINE and RESPONSABLE_LOGISTIQUE: look for matching centre
    if (user.role === UserRole.OPERATEUR_USINE || user.role === UserRole.RESPONSABLE_LOGISTIQUE) {
      const matchingCentre = centres.find(c => c.id === user.company_name);
      if (matchingCentre) return matchingCentre.id;
    }
    
    // For ADMIN: if company_name is a centre ID, use it
    const matchingCentre = centres.find(c => c.id === user.company_name);
    if (matchingCentre) return matchingCentre.id;
    
    return '';
  }, [user, centres]);

  const { register, handleSubmit, control, formState: { errors }, setValue, watch } = useForm<PaletteCreateFormData>({
    resolver: zodResolver(paletteCreateSchema),
    defaultValues: {
      reference_code: '', // Will be set when code is loaded
      current_centre_remplisseur_id: defaultCentreId || undefined,
    },
  });

  // Set the auto-generated code when it's loaded
  useEffect(() => {
    if (nextCode) {
      setValue('reference_code', nextCode, { shouldValidate: false });
    }
  }, [nextCode, setValue]);

  // Set default centre remplisseur when data is loaded and user is available
  useEffect(() => {
    if (defaultCentreId) {
      const currentValue = watch('current_centre_remplisseur_id');
      if (!currentValue) {
        setValue('current_centre_remplisseur_id', defaultCentreId, { shouldValidate: false });
      }
    }
  }, [defaultCentreId, setValue, watch]);

  const createMutation = useMutation({
    mutationFn: (data: PaletteCreateFormData) => {
      // Transform form data to API payload
      const payload: any = {
        type: data.palette_type,
      };
      
      // Include condition if provided
      if (data.condition) {
        payload.condition = data.condition;
      }
      
      // Only include fields that have actual values (not empty strings)
      if (data.reference_code && data.reference_code.trim()) {
        payload.reference_code = data.reference_code.trim();
      }
      if (data.capacity && data.capacity > 0) {
        payload.capacity = data.capacity;
      }
      if (data.manufacturing_date && data.manufacturing_date.trim()) {
        payload.manufacturing_date = data.manufacturing_date.trim();
      }
      if (data.rfid_tag_id && data.rfid_tag_id.trim() && data.rfid_tag_id.trim() !== '') {
        payload.rfid_tag_id = data.rfid_tag_id.trim();
      }
      // Handle centre remplisseur selection - required field
      if (data.current_centre_remplisseur_id && data.current_centre_remplisseur_id.trim() && data.current_centre_remplisseur_id.trim() !== '') {
        payload.current_centre_remplisseur_id = data.current_centre_remplisseur_id.trim();
      }
      // Handle partner selection (optional)
      if (data.current_partner_id && data.current_partner_id.trim() && data.current_partner_id.trim() !== '') {
        payload.current_partner_id = data.current_partner_id.trim();
      }
      if (data.notes && data.notes.trim()) {
        payload.notes = data.notes.trim();
      }
      
      return paletteService.create(payload);
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['palettes'] });
      navigate(`/palettes/${data.id}`);
    },
    onError: (error: any) => {
      console.error('Error creating palette:', error);
      const errorMessage = error.response?.data?.detail || error.message || 'Erreur lors de la création de la palette';
      alert(errorMessage);
    },
  });

  const onSubmit = (data: PaletteCreateFormData) => {
    createMutation.mutate(data);
  };

  const availableTags = rfidTagsData?.items || [];

  // Build list of centres remplisseurs
  const centreOptions = useMemo(() => {
    if (!centres) return [];
    
    return centres.map(centre => ({
      value: centre.id,
      label: `${centre.name} (${centre.code})`,
    })).sort((a, b) => a.label.localeCompare(b.label));
  }, [centres]);

  return (
    <div className="w-full">
      <div className="mb-6">
        <Link to="/palettes">
          <Button variant="ghost" size="sm">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Retour
          </Button>
        </Link>
        <h1 className="text-3xl font-bold mt-4">Créer une nouvelle palette</h1>
      </div>

      <form onSubmit={handleSubmit(onSubmit)}>
        <Card className="w-full">
          <CardHeader>
            <CardTitle>Informations de la palette</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-6">
              {/* Première ligne : Identifiant palette (à gauche) et Type de palette (à droite) */}
              <div className="grid grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium mb-1">Identifiant palette (code de référence)</label>
                  <Controller
                    name="reference_code"
                    control={control}
                    render={({ field }) => (
                      <Input
                        {...field}
                        value={nextCode || field.value || ''}
                        disabled
                        error={errors.reference_code?.message}
                        className="bg-gray-100 text-gray-700 cursor-not-allowed opacity-75"
                        placeholder={isLoadingCode ? "Génération en cours..." : "Génération automatique..."}
                      />
                    )}
                  />
                  <p className="mt-1 text-xs text-muted-foreground">
                    {isLoadingCode ? "Génération du code en cours..." : "Code généré automatiquement"}
                  </p>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Type de palette</label>
                  <select
                    {...register('palette_type')}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="B6">B6 (6kg)</option>
                    <option value="B12">B12 (12kg)</option>
                    <option value="B28">B28 (28kg)</option>
                  </select>
                  {errors.palette_type && (
                    <p className="mt-1 text-sm text-destructive">{errors.palette_type.message}</p>
                  )}
                </div>
              </div>

              {/* Deuxième ligne : Condition (à gauche) et Capacité (à droite) */}
              <div className="grid grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium mb-1">Condition</label>
                  <select
                    {...register('condition')}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    defaultValue="NEUVE"
                  >
                    <option value="NEUVE">Neuve</option>
                    <option value="RECONDITIONNEE">Reconditionnée</option>
                  </select>
                  {errors.condition && (
                    <p className="mt-1 text-sm text-destructive">{errors.condition.message}</p>
                  )}
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Capacité (Nombre de bouteilles possible)</label>
                  <Input
                    type="number"
                    error={errors.capacity?.message}
                    {...register('capacity', { valueAsNumber: true })}
                    placeholder="Capacité"
                  />
                </div>
              </div>

              {/* Troisième ligne : Date de fabrication */}
              <div>
                <label className="block text-sm font-medium mb-1">Date de fabrication</label>
                <Input
                  type="date"
                  error={errors.manufacturing_date?.message}
                  {...register('manufacturing_date')}
                />
              </div>

              {/* Quatrième ligne : Tag RFID (à gauche) et Localisation (à droite) */}
              <div className="grid grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium mb-1">Tag RFID</label>
                  <Controller
                    name="rfid_tag_id"
                    control={control}
                    render={({ field }) => (
                      <select
                        {...field}
                        value={field.value || ''}
                        onChange={(e) => field.onChange(e.target.value === '' ? undefined : e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      >
                        <option value="">Aucun tag RFID</option>
                        {availableTags.map((tag) => (
                          <option key={tag.id} value={tag.id}>
                            {tag.label || tag.tag_number}
                          </option>
                        ))}
                      </select>
                    )}
                  />
                  {errors.rfid_tag_id && (
                    <p className="mt-1 text-sm text-destructive">{errors.rfid_tag_id.message}</p>
                  )}
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Localisation (Centres de Remplissage)</label>
                  <Controller
                    name="current_centre_remplisseur_id"
                    control={control}
                    defaultValue={defaultCentreId || undefined}
                    render={({ field }) => (
                      <select
                        {...field}
                        value={field.value || ''}
                        onChange={(e) => field.onChange(e.target.value === '' ? undefined : e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      >
                        <option value="">Sélectionner un centre de remplissage</option>
                        {centreOptions.map((option) => (
                          <option key={option.value} value={option.value}>
                            {option.label}
                          </option>
                        ))}
                      </select>
                    )}
                  />
                  {errors.current_centre_remplisseur_id && (
                    <p className="mt-1 text-sm text-destructive">{errors.current_centre_remplisseur_id.message}</p>
                  )}
                  {defaultCentreId && (
                    <p className="mt-1 text-xs text-muted-foreground">
                      Par défaut : centre de remplissage de l'utilisateur connecté
                    </p>
                  )}
                </div>
              </div>

              {/* Notes */}
              <div>
                <label className="block text-sm font-medium mb-1">Notes (optionnel)</label>
                <textarea
                  {...register('notes')}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                  rows={3}
                  placeholder="Notes additionnelles"
                />
              </div>

              <div className="flex space-x-3 pt-4">
                <Button type="submit" isLoading={createMutation.isPending}>
                  Créer la palette
                </Button>
                <Link to="/palettes">
                  <Button type="button" variant="outline">
                    Annuler
                  </Button>
                </Link>
              </div>
            </div>
          </CardContent>
        </Card>
      </form>
    </div>
  );
};

export default CreatePalettePage;
