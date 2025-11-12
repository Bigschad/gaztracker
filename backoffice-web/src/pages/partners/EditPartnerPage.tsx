import { useEffect } from 'react';
import { useNavigate, Link, useParams } from 'react-router-dom';
import { useMutation, useQuery } from '@tanstack/react-query';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { partnerService } from '../../services/api';
import { Card, CardHeader, CardTitle, CardContent, Button, Input, Select } from '../../components/common';
import { ArrowLeft } from 'lucide-react';
import { partnerUpdateSchema, PartnerUpdateFormData } from '../../utils/validators';
import { PartnerType } from '../../types';

const EditPartnerPage = () => {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();

  const { data: partner, isLoading } = useQuery({
    queryKey: ['partner', id],
    queryFn: () => partnerService.getById(id!),
    enabled: !!id,
  });

  const { register, handleSubmit, control, formState: { errors }, reset } = useForm<PartnerUpdateFormData>({
    resolver: zodResolver(partnerUpdateSchema),
  });

  // Reset form when partner data is loaded
  useEffect(() => {
    if (partner) {
      reset({
        name: partner.name,
        type: partner.type,
        address: partner.address || '',
        city: partner.city || '',
        postal_code: partner.postal_code || '',
        country: partner.country || 'France',
        email: partner.email || '',
        phone: partner.phone || '',
        is_active: partner.is_active,
        notes: partner.notes || '',
      });
    }
  }, [partner, reset]);

  const updateMutation = useMutation({
    mutationFn: (data: PartnerUpdateFormData) => {
      // Ensure type is properly cast to PartnerType if present
      const payload = {
        ...data,
        type: data.type ? (data.type as PartnerType) : undefined,
      };
      return partnerService.update(id!, payload as any);
    },
    onSuccess: () => {
      navigate(`/partners/${id}`);
    },
  });

  const onSubmit = (data: PartnerUpdateFormData) => {
    updateMutation.mutate(data);
  };

  if (isLoading) {
    return <div className="p-8 text-center">Chargement...</div>;
  }

  if (!partner) {
    return <div className="p-8 text-center text-red-600">Partenaire introuvable</div>;
  }

  return (
    <div className="w-full">
      <div className="mb-6">
        <Link to={`/partners/${id}`}>
          <Button variant="ghost" size="sm">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Retour
          </Button>
        </Link>
        <h1 className="text-3xl font-bold mt-4">Modifier le partenaire</h1>
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
                        { value: PartnerType.FOURNISSEUR, label: 'Fournisseur' },
                        { value: PartnerType.TRANSPORTEUR, label: 'Transporteur' },
                        { value: PartnerType.AUTRE, label: 'Autre' },
                      ]}
                      onChange={(e) => {
                        field.onChange(e.target.value as PartnerType);
                      }}
                    />
                  )}
                />
                {errors.type && (
                  <p className="mt-1 text-sm text-destructive">{errors.type.message}</p>
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
                <Link to={`/partners/${id}`}>
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

export default EditPartnerPage;

