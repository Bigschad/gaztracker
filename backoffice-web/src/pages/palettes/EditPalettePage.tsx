import { useNavigate, Link, useParams } from 'react-router-dom';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useForm, Controller } from 'react-hook-form';
import { useEffect, useMemo } from 'react';
import { zodResolver } from '@hookform/resolvers/zod';
import { paletteService, rfidTagService, centreRemplisseurService } from '../../services/api';
import { Card, CardHeader, CardTitle, CardContent, Button, Input } from '../../components/common';
import { ArrowLeft } from 'lucide-react';
import { paletteUpdateSchema, PaletteUpdateFormData } from '../../utils/validators';

const EditPalettePage = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  // Fetch palette data
  const { data: palette, isLoading: isLoadingPalette } = useQuery({
    queryKey: ['palette', id],
    queryFn: () => paletteService.getById(id!),
    enabled: !!id,
  });

  // Fetch available RFID tags (NOT_ASSIGNED and active) + current tag if assigned
  const { data: rfidTagsData } = useQuery({
    queryKey: ['rfid-tags', 'available', id],
    queryFn: async () => {
      const availableTags = await rfidTagService.list({
        status: 'NOT_ASSIGNED' as any,
        is_active: true,
        page: 1,
        page_size: 100,
      });
      
      // If palette has a tag, include it in the list
      if (palette?.rfid_tag) {
        const currentTag = {
          id: palette.rfid_tag.id,
          tag_number: palette.rfid_tag.tag_number,
          label: `${palette.rfid_tag.tag_number} (actuel)`,
          status: palette.rfid_tag.status,
          is_active: palette.rfid_tag.is_active,
        };
        return {
          ...availableTags,
          items: [currentTag, ...(availableTags.items || [])],
        };
      }
      
      return availableTags;
    },
    enabled: !!palette,
  });

  // Fetch centres remplisseurs
  const { data: centres } = useQuery({
    queryKey: ['centres-remplisseurs', 'palette-form'],
    queryFn: () => centreRemplisseurService.list({ limit: 100, is_active: true }),
    enabled: true,
  });

  const { register, handleSubmit, control, formState: { errors }, reset } = useForm<PaletteUpdateFormData>({
    resolver: zodResolver(paletteUpdateSchema),
  });

  // Reset form when palette data is loaded
  useEffect(() => {
    if (palette) {
      reset({
        palette_type: palette.type as 'B6' | 'B12' | 'B28',
        condition: palette.condition as 'NEUVE' | 'RECONDITIONNEE' | undefined,
        capacity: palette.capacity || undefined,
        manufacturing_date: palette.manufacturing_date ? palette.manufacturing_date.split('T')[0] : undefined,
        rfid_tag_id: palette.rfid_tag_id || undefined,
        current_centre_remplisseur_id: palette.current_centre_remplisseur_id || undefined,
        notes: palette.notes || undefined,
      });
    }
  }, [palette, reset]);

  const updateMutation = useMutation({
    mutationFn: (data: PaletteUpdateFormData) => {
      // Transform form data to API payload
      const payload: any = {};
      
      if (data.palette_type) {
        payload.type = data.palette_type;
      }
      
      // Include condition if provided
      if (data.condition) {
        payload.condition = data.condition;
      }
      
      // Only include fields that have actual values (not empty strings)
      if (data.capacity !== undefined && data.capacity !== null && data.capacity > 0) {
        payload.capacity = data.capacity;
      }
      if (data.manufacturing_date && data.manufacturing_date.trim()) {
        payload.manufacturing_date = data.manufacturing_date.trim();
      }
      if (data.rfid_tag_id !== undefined) {
        if (data.rfid_tag_id && data.rfid_tag_id.trim() && data.rfid_tag_id.trim() !== '') {
          payload.rfid_tag_id = data.rfid_tag_id.trim();
        } else {
          // If empty string, set to null to unassign
          payload.rfid_tag_id = null;
        }
      }
      // Handle centre remplisseur selection
      if (data.current_centre_remplisseur_id !== undefined) {
        if (data.current_centre_remplisseur_id && data.current_centre_remplisseur_id.trim() && data.current_centre_remplisseur_id.trim() !== '') {
          payload.current_centre_remplisseur_id = data.current_centre_remplisseur_id.trim();
        } else {
          payload.current_centre_remplisseur_id = null;
        }
      }
      if (data.notes !== undefined) {
        payload.notes = data.notes && data.notes.trim() ? data.notes.trim() : null;
      }
      
      return paletteService.update(id!, payload);
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['palettes'] });
      queryClient.invalidateQueries({ queryKey: ['palette', id] });
      navigate(`/palettes/${data.id}`);
    },
    onError: (error: any) => {
      console.error('Error updating palette:', error);
      const errorMessage = error.response?.data?.detail || error.message || 'Erreur lors de la modification de la palette';
      alert(errorMessage);
    },
  });

  const onSubmit = (data: PaletteUpdateFormData) => {
    updateMutation.mutate(data);
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

  if (isLoadingPalette) {
    return <div className="p-8 text-center">Chargement...</div>;
  }

  if (!palette) {
    return <div className="p-8 text-center">Palette non trouvée</div>;
  }

  return (
    <div className="w-full">
      <div className="mb-6">
        <Link to={`/palettes/${id}`}>
          <Button variant="ghost" size="sm">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Retour
          </Button>
        </Link>
        <h1 className="text-3xl font-bold mt-4">
          Modifier la palette {palette.reference_code || palette.serial_number || palette.id}
        </h1>
      </div>

      <form onSubmit={handleSubmit(onSubmit)}>
        <Card className="w-full">
          <CardHeader>
            <CardTitle>Informations de la palette</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-6">
              {/* Première ligne : Identifiant palette (lecture seule) et Type de palette */}
              <div className="grid grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium mb-1">Identifiant palette (code de référence)</label>
                  <Input
                    value={palette.reference_code || palette.serial_number || '-'}
                    disabled
                    className="bg-gray-100 text-gray-700 cursor-not-allowed opacity-75"
                  />
                  <p className="mt-1 text-xs text-muted-foreground">
                    Code en lecture seule
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
                  >
                    <option value="">Sélectionner une condition</option>
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
                <Button type="submit" isLoading={updateMutation.isPending}>
                  Enregistrer les modifications
                </Button>
                <Link to={`/palettes/${id}`}>
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

export default EditPalettePage;
