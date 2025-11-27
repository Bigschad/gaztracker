import { useNavigate, Link } from 'react-router-dom';
import { useMutation, useQuery } from '@tanstack/react-query';
import { useForm, Controller } from 'react-hook-form';
import { depotService, partnerService } from '../../services/api';
import { Card, CardHeader, CardTitle, CardContent, Button, Input } from '../../components/common';
import { ArrowLeft } from 'lucide-react';
import { DepotCreate } from '../../types';

const CreateDepotPage = () => {
  const navigate = useNavigate();

  // Fetch partners (grossistes and revendeurs) for dropdown
  const { data: partnersData } = useQuery({
    queryKey: ['partners', 'for-depots'],
    queryFn: () => partnerService.list({
      page: 1,
      page_size: 100,
      is_active: true,
    }),
  });

  const partners = partnersData?.items || [];

  const { register, handleSubmit, formState: { errors }, control } = useForm<DepotCreate>({
    defaultValues: {
      is_active: true,
      is_main_depot: false,
    },
  });

  const createMutation = useMutation({
    mutationFn: (data: DepotCreate) => depotService.create(data),
    onSuccess: (data) => {
      navigate(`/depots/${data.id}`);
    },
  });

  const onSubmit = (data: DepotCreate) => {
    createMutation.mutate(data);
  };

  return (
    <div className="w-full">
      <div className="mb-6">
        <Link to="/depots">
          <Button variant="ghost" size="sm">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Retour
          </Button>
        </Link>
        <h1 className="text-3xl font-bold mt-4">Créer un nouveau dépôt</h1>
      </div>

      <form onSubmit={handleSubmit(onSubmit)}>
        <Card className="w-full">
          <CardHeader>
            <CardTitle>Informations du dépôt</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium mb-1">Nom *</label>
                <Input
                  error={errors.name?.message}
                  {...register('name', { required: 'Le nom est requis' })}
                  placeholder="Nom du dépôt"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Code</label>
                <Input
                  error={errors.code?.message}
                  {...register('code')}
                  placeholder="Code unique du dépôt"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Partenaire (Grossiste/Revendeur) *</label>
                <Controller
                  name="partner_id"
                  control={control}
                  rules={{ required: 'Le partenaire est requis' }}
                  render={({ field }) => (
                    <select
                      {...field}
                      value={field.value || ''}
                      onChange={(e) => field.onChange(e.target.value === '' ? undefined : e.target.value)}
                      className="w-full px-3 py-2 border rounded-lg"
                    >
                      <option value="">Sélectionner un partenaire</option>
                      {partners.map((partner) => (
                        <option key={partner.id} value={partner.id}>
                          {partner.name} ({partner.type})
                        </option>
                      ))}
                    </select>
                  )}
                />
                {errors.partner_id && (
                  <p className="mt-1 text-sm text-red-600">{errors.partner_id.message}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Adresse</label>
                <Input
                  error={errors.address?.message}
                  {...register('address')}
                  placeholder="Adresse"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Ville</label>
                  <Input
                    error={errors.city?.message}
                    {...register('city')}
                    placeholder="Ville"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-1">Code postal</label>
                  <Input
                    error={errors.postal_code?.message}
                    {...register('postal_code')}
                    placeholder="Code postal"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Latitude</label>
                  <Input
                    type="number"
                    step="any"
                    error={errors.latitude?.message}
                    {...register('latitude', {
                      valueAsNumber: true,
                      min: { value: -90, message: 'Latitude doit être entre -90 et 90' },
                      max: { value: 90, message: 'Latitude doit être entre -90 et 90' },
                    })}
                    placeholder="Latitude GPS"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-1">Longitude</label>
                  <Input
                    type="number"
                    step="any"
                    error={errors.longitude?.message}
                    {...register('longitude', {
                      valueAsNumber: true,
                      min: { value: -180, message: 'Longitude doit être entre -180 et 180' },
                      max: { value: 180, message: 'Longitude doit être entre -180 et 180' },
                    })}
                    placeholder="Longitude GPS"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Nom du contact</label>
                  <Input
                    error={errors.contact_name?.message}
                    {...register('contact_name')}
                    placeholder="Nom du contact"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-1">Téléphone du contact</label>
                  <Input
                    error={errors.contact_phone?.message}
                    {...register('contact_phone')}
                    placeholder="Téléphone"
                  />
                </div>
              </div>

              <div className="grid grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Capacité B28</label>
                  <Input
                    type="number"
                    error={errors.capacity_b28?.message}
                    {...register('capacity_b28', { valueAsNumber: true, min: 0 })}
                    placeholder="Capacité B28"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-1">Capacité B12</label>
                  <Input
                    type="number"
                    error={errors.capacity_b12?.message}
                    {...register('capacity_b12', { valueAsNumber: true, min: 0 })}
                    placeholder="Capacité B12"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-1">Capacité B6</label>
                  <Input
                    type="number"
                    error={errors.capacity_b6?.message}
                    {...register('capacity_b6', { valueAsNumber: true, min: 0 })}
                    placeholder="Capacité B6"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Notes</label>
                <textarea
                  {...register('notes')}
                  className="w-full px-3 py-2 border rounded-lg"
                  rows={4}
                  placeholder="Notes supplémentaires"
                />
              </div>

              <div className="flex items-center space-x-6">
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    {...register('is_active')}
                    className="mr-2"
                    defaultChecked
                  />
                  <label className="text-sm font-medium">Actif</label>
                </div>

                <div className="flex items-center">
                  <input
                    type="checkbox"
                    {...register('is_main_depot')}
                    className="mr-2"
                  />
                  <label className="text-sm font-medium">Dépôt principal</label>
                </div>
              </div>

              <div className="flex justify-end space-x-4">
                <Link to="/depots">
                  <Button type="button" variant="outline">Annuler</Button>
                </Link>
                <Button type="submit" disabled={createMutation.isPending}>
                  {createMutation.isPending ? 'Création...' : 'Créer'}
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </form>
    </div>
  );
};

export default CreateDepotPage;

