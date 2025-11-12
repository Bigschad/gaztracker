import { useNavigate, Link } from 'react-router-dom';
import { useMutation, useQuery } from '@tanstack/react-query';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { paletteService, rfidTagService, partnerService } from '../../services/api';
import { Card, CardHeader, CardTitle, CardContent, Button, Input } from '../../components/common';
import { ArrowLeft } from 'lucide-react';
import { paletteCreateSchema, PaletteCreateFormData } from '../../utils/validators';

const CreatePalettePage = () => {
  const navigate = useNavigate();

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

  // Fetch partners (grossistes)
  const { data: partnersData } = useQuery({
    queryKey: ['partners', 'grossistes'],
    queryFn: () => partnerService.list({
      type: 'GROSSISTE' as any,
      is_active: true,
      page: 1,
      page_size: 100,
    }),
  });

  const { register, handleSubmit, control, formState: { errors } } = useForm<PaletteCreateFormData>({
    resolver: zodResolver(paletteCreateSchema),
  });

  const createMutation = useMutation({
    mutationFn: (data: PaletteCreateFormData) => {
      // Transform form data to API payload
      const payload: any = {
        type: data.palette_type,
      };
      if (data.reference_code && data.reference_code.trim()) {
        payload.reference_code = data.reference_code.trim();
      }
      if (data.capacity) {
        payload.capacity = data.capacity;
      }
      if (data.manufacturing_date && data.manufacturing_date.trim()) {
        payload.manufacturing_date = data.manufacturing_date.trim();
      }
      if (data.rfid_tag_id && data.rfid_tag_id.trim()) {
        payload.rfid_tag_id = data.rfid_tag_id.trim();
      }
      if (data.current_partner_id && data.current_partner_id.trim()) {
        payload.current_partner_id = data.current_partner_id.trim();
      }
      if (data.notes && data.notes.trim()) {
        payload.notes = data.notes.trim();
      }
      return paletteService.create(payload);
    },
    onSuccess: (data) => {
      navigate(`/palettes/${data.id}`);
    },
  });

  const onSubmit = (data: PaletteCreateFormData) => {
    createMutation.mutate(data);
  };

  const availableTags = rfidTagsData?.items || [];
  const grossistes = partnersData?.items || [];

  // Debug logs
  if (rfidTagsData) {
    console.log('RFID Tags Response:', rfidTagsData);
    console.log('Available Tags:', availableTags);
  }
  if (partnersData) {
    console.log('Partners Response:', partnersData);
    console.log('Grossistes:', grossistes);
  }

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
                  <Input
                    error={errors.reference_code?.message}
                    {...register('reference_code')}
                    placeholder="Code de référence"
                  />
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

              {/* Deuxième ligne : Capacité (à gauche) et Date de fabrication (à droite) */}
              <div className="grid grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium mb-1">Capacité (Nombre de bouteilles possible)</label>
                  <Input
                    type="number"
                    error={errors.capacity?.message}
                    {...register('capacity', { valueAsNumber: true })}
                    placeholder="Capacité"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Date de fabrication</label>
                  <Input
                    type="date"
                    error={errors.manufacturing_date?.message}
                    {...register('manufacturing_date')}
                  />
                </div>
              </div>

              {/* Troisième ligne : Tag RFID (à gauche) et Localisation (à droite) */}
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
                  <label className="block text-sm font-medium mb-1">Localisation (Liste des grossistes)</label>
                  <Controller
                    name="current_partner_id"
                    control={control}
                    render={({ field }) => (
                      <select
                        {...field}
                        value={field.value || ''}
                        onChange={(e) => field.onChange(e.target.value === '' ? undefined : e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      >
                        <option value="">Aucun grossiste</option>
                        {grossistes.map((partner) => (
                          <option key={partner.id} value={partner.id}>
                            {partner.name}
                          </option>
                        ))}
                      </select>
                    )}
                  />
                  {errors.current_partner_id && (
                    <p className="mt-1 text-sm text-destructive">{errors.current_partner_id.message}</p>
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
