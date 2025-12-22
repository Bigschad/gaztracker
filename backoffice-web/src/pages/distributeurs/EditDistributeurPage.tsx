import { useEffect } from 'react';
import { useNavigate, Link, useParams } from 'react-router-dom';
import { useMutation, useQuery } from '@tanstack/react-query';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { partnerService, groupeService } from '../../services/api';
import { Card, CardHeader, CardTitle, CardContent, Button, Input, Select } from '../../components/common';
import { ArrowLeft } from 'lucide-react';
import { partnerUpdateSchema, PartnerUpdateFormData } from '../../utils/validators';
import { PartnerType } from '../../types';

const EditDistributeurPage = () => {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();

  const { data: distributeur, isLoading } = useQuery({
    queryKey: ['distributeur', id],
    queryFn: () => partnerService.getById(id!),
    enabled: !!id,
  });

  const { register, handleSubmit, control, formState: { errors }, reset } = useForm<PartnerUpdateFormData>({
    resolver: zodResolver(partnerUpdateSchema),
  });

  // Fetch active groupes
  const { data: groupes, isLoading: isLoadingGroupes } = useQuery({
    queryKey: ['groupes', 'active'],
    queryFn: () => groupeService.list({ limit: 100, is_active: true }),
  });

  // Reset form when distributeur data is loaded
  useEffect(() => {
    if (distributeur) {
      if (distributeur.type !== PartnerType.DISTRIBUTEUR) {
        // Redirect if not a distributeur
        navigate('/distributeurs');
        return;
      }
      reset({
        name: distributeur.name,
        type: PartnerType.DISTRIBUTEUR,
        groupe_id: distributeur.groupe_id || undefined,
        address: distributeur.address || '',
        city: distributeur.city || '',
        postal_code: distributeur.postal_code || '',
        country: distributeur.country || 'France',
        email: distributeur.email || '',
        phone: distributeur.phone || '',
        is_active: distributeur.is_active,
        notes: distributeur.notes || '',
      });
    }
  }, [distributeur, reset, navigate]);

  const updateMutation = useMutation({
    mutationFn: (data: PartnerUpdateFormData) => {
      const payload: any = {
        ...data,
        type: PartnerType.DISTRIBUTEUR,
      };
      if (data.groupe_id !== undefined) {
        if (data.groupe_id && data.groupe_id.trim() !== '') {
          payload.groupe_id = data.groupe_id.trim();
        } else {
          payload.groupe_id = null;
        }
      }
      return partnerService.update(id!, payload);
    },
    onSuccess: () => {
      navigate(`/distributeurs/${id}`);
      window.location.reload();
    },
  });

  const onSubmit = (data: PartnerUpdateFormData) => {
    updateMutation.mutate(data);
  };

  if (isLoading) {
    return <div className="p-8 text-center">Chargement...</div>;
  }

  if (!distributeur) {
    return <div className="p-8 text-center text-red-600">Distributeur introuvable</div>;
  }

  if (distributeur.type !== PartnerType.DISTRIBUTEUR) {
    return <div className="p-8 text-center text-red-600">Ce partenaire n'est pas un distributeur</div>;
  }

  return (
    <div className="w-full">
      <div className="mb-6">
        <Link to={`/distributeurs/${id}`}>
          <Button variant="ghost" size="sm">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Retour
          </Button>
        </Link>
        <h1 className="text-3xl font-bold mt-4">Modifier le distributeur</h1>
      </div>

      <form onSubmit={handleSubmit(onSubmit)}>
        <Card className="w-full">
          <CardHeader>
            <CardTitle>Informations du distributeur</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium mb-1">Nom *</label>
                <Input
                  error={errors.name?.message}
                  {...register('name')}
                  placeholder="Nom du distributeur"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Groupe *</label>
                <Controller
                  name="groupe_id"
                  control={control}
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
                <Button type="submit" isLoading={updateMutation.isPending}>
                  Enregistrer les modifications
                </Button>
                <Link to={`/distributeurs/${id}`}>
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

export default EditDistributeurPage;

