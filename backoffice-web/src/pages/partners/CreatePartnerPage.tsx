import { useNavigate, Link } from 'react-router-dom';
import { useMutation, useQuery } from '@tanstack/react-query';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { partnerService, groupeService } from '../../services/api';
import { Card, CardHeader, CardTitle, CardContent, Button, Input, Select } from '../../components/common';
import { ArrowLeft } from 'lucide-react';
import { partnerCreateSchema, PartnerCreateFormData } from '../../utils/validators';
import { PartnerType } from '../../types';

const CreatePartnerPage = () => {
  const navigate = useNavigate();

  const { register, handleSubmit, control, watch, setValue, formState: { errors } } = useForm<PartnerCreateFormData>({
    resolver: zodResolver(partnerCreateSchema),
    defaultValues: {
      country: 'France',
      is_active: true,
      type: undefined,
      groupe_id: undefined,
    },
  });

  // Watch the type field to show/hide groupe selection
  const selectedType = watch('type');

  // Fetch active groupes for DISTRIBUTEUR type
  const { data: groupes, isLoading: isLoadingGroupes } = useQuery({
    queryKey: ['groupes', 'active'],
    queryFn: () => groupeService.list({ limit: 100, is_active: true }),
    enabled: selectedType === PartnerType.DISTRIBUTEUR,
  });

  const createMutation = useMutation({
    mutationFn: (data: PartnerCreateFormData) => {
      // Ensure type is properly cast to PartnerType
      const payload: any = {
        ...data,
        type: data.type as PartnerType,
      };
      // Include groupe_id only if it's provided and not empty
      if (data.groupe_id && data.groupe_id.trim() !== '') {
        payload.groupe_id = data.groupe_id;
      }
      return partnerService.create(payload);
    },
    onSuccess: (data) => {
      navigate(`/partners/${data.id}`);
      window.location.reload();
    },
  });

  const onSubmit = (data: PartnerCreateFormData) => {
    createMutation.mutate(data);
  };

  return (
    <div className="w-full">
      <div className="mb-6">
        <Link to="/partners">
          <Button variant="ghost" size="sm">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Retour
          </Button>
        </Link>
        <h1 className="text-3xl font-bold mt-4">Créer un nouveau partenaire</h1>
      </div>

      <form onSubmit={handleSubmit(onSubmit)}>
        <Card className="w-full">
          <CardHeader>
            <CardTitle>Informations du partenaire</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium mb-1">Nom *</label>
                <Input
                  error={errors.name?.message}
                  {...register('name')}
                  placeholder="Nom du partenaire"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Type *</label>
                <Controller
                  name="type"
                  control={control}
                  render={({ field }) => (
                    <Select
                      value={field.value || ''}
                      options={[
                        { value: '', label: 'Sélectionner un type' },
                        { value: PartnerType.GROSSISTE, label: 'Grossiste' },
                        { value: PartnerType.DISTRIBUTEUR, label: 'Distributeur' },
                        { value: PartnerType.TRANSPORTEUR, label: 'Transporteur' },
                        { value: PartnerType.AUTRE, label: 'Autre' },
                      ]}
                      onChange={(e) => {
                        field.onChange(e.target.value as PartnerType);
                        // Reset groupe_id when type changes
                        if (e.target.value !== PartnerType.DISTRIBUTEUR) {
                          setValue('groupe_id', undefined);
                        }
                      }}
                    />
                  )}
                />
                {errors.type && (
                  <p className="mt-1 text-sm text-destructive">{errors.type.message}</p>
                )}
              </div>

              {selectedType === PartnerType.DISTRIBUTEUR && (
                <div>
                  <label className="block text-sm font-medium mb-1">Groupe *</label>
                  <Controller
                    name="groupe_id"
                    control={control}
                    rules={{ required: 'Le groupe est requis pour les distributeurs' }}
                    render={({ field }) => (
                      <>
                        <Select
                          value={field.value || ''}
                          options={[
                            { value: '', label: isLoadingGroupes ? 'Chargement...' : 'Sélectionner un groupe' },
                            ...(groupes?.map((groupe) => ({
                              value: groupe.id,
                              label: groupe.name,
                            })) || []),
                          ]}
                          onChange={(e) => {
                            const value = e.target.value;
                            field.onChange(value && value.trim() !== '' ? value : undefined);
                          }}
                          disabled={isLoadingGroupes}
                        />
                        {isLoadingGroupes && (
                          <p className="mt-1 text-sm text-muted-foreground">
                            Chargement des groupes...
                          </p>
                        )}
                        {!isLoadingGroupes && (!groupes || groupes.length === 0) && (
                          <p className="mt-1 text-sm text-amber-600">
                            Aucun groupe actif disponible. Veuillez créer un groupe d'abord.
                          </p>
                        )}
                      </>
                    )}
                  />
                  {errors.groupe_id && (
                    <p className="mt-1 text-sm text-destructive">{errors.groupe_id.message}</p>
                  )}
                </div>
              )}

              <div>
                <label className="block text-sm font-medium mb-1">Adresse</label>
                <Input
                  error={errors.address?.message}
                  {...register('address')}
                  placeholder="Adresse"
                />
              </div>

              <div className="grid grid-cols-2 gap-6">
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

              <div>
                <label className="block text-sm font-medium mb-1">Pays</label>
                <Input
                  error={errors.country?.message}
                  {...register('country')}
                  placeholder="Pays"
                />
              </div>

              <div className="grid grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium mb-1">Email</label>
                  <Input
                    type="email"
                    error={errors.email?.message}
                    {...register('email')}
                    placeholder="Email"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Téléphone</label>
                  <Input
                    type="tel"
                    error={errors.phone?.message}
                    {...register('phone')}
                    placeholder="Téléphone"
                  />
                </div>
              </div>

              <div>
                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    {...register('is_active')}
                    className="rounded"
                  />
                  <span className="text-sm font-medium">Actif</span>
                </label>
              </div>

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
                  Créer le partenaire
                </Button>
                <Link to="/partners">
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

export default CreatePartnerPage;

