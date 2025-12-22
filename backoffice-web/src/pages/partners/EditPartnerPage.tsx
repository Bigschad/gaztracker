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
import { useAuth } from '../../hooks/useAuth';
import { UserRole } from '../../types/user';

const EditPartnerPage = () => {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();
  const { user } = useAuth();

  const { data: partner, isLoading } = useQuery({
    queryKey: ['partner', id],
    queryFn: () => partnerService.getById(id!),
    enabled: !!id,
  });

  const { register, handleSubmit, control, watch, setValue, formState: { errors }, reset } = useForm<PartnerUpdateFormData>({
    resolver: zodResolver(partnerUpdateSchema),
  });

  // Watch the type field to show/hide groupe selection
  const selectedType = watch('type');

  // Get active group from user (for ADMIN, company_name stores groupe_id)
  const getActiveGroupeId = () => {
    if (!user?.company_name) return null;
    
    // Check if company_name is a valid UUID (groupe_id)
    const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
    if (uuidRegex.test(user.company_name)) {
      return user.company_name;
    }
    
    // For ADMIN, always use company_name as groupe_id
    if (user.role === UserRole.ADMIN) {
      return user.company_name;
    }
    
    return null;
  };

  const activeGroupeIdFromUser = getActiveGroupeId();

  // Fetch all active groupes (for ADMIN if no groupe_id is detected)
  const { data: groupesData } = useQuery({
    queryKey: ['groupes', 'active'],
    queryFn: () => groupeService.list({ limit: 100, is_active: true }),
    enabled: user?.role === UserRole.ADMIN && activeGroupeIdFromUser === 'FETCH_FIRST_ACTIVE',
  });

  // Determine the actual active groupe ID
  const activeGroupeId = activeGroupeIdFromUser === 'FETCH_FIRST_ACTIVE' 
    ? (groupesData && groupesData.length > 0 ? groupesData[0].id : null)
    : activeGroupeIdFromUser;

  // Fetch active groupes for DISTRIBUTEUR type
  const { data: groupes, isLoading: isLoadingGroupes } = useQuery({
    queryKey: ['groupes', 'active'],
    queryFn: () => groupeService.list({ limit: 100, is_active: true }),
    enabled: selectedType === PartnerType.DISTRIBUTEUR || partner?.type === PartnerType.DISTRIBUTEUR,
  });

  // Reset form when partner data is loaded
  useEffect(() => {
    if (partner) {
      reset({
        name: partner.name,
        type: partner.type,
        groupe_id: partner.groupe_id || (partner.type === PartnerType.DISTRIBUTEUR && activeGroupeId ? activeGroupeId : undefined),
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
  }, [partner, reset, activeGroupeId]);

  const updateMutation = useMutation({
    mutationFn: (data: PartnerUpdateFormData) => {
      // Build payload with proper type casting
      const payload: any = {
        ...data,
        type: data.type ? (data.type as PartnerType) : undefined,
      };
      
      // Handle groupe_id: include it if provided, or set to null if explicitly cleared
      if (data.groupe_id !== undefined) {
        if (data.groupe_id && data.groupe_id.trim() !== '') {
          payload.groupe_id = data.groupe_id.trim();
        } else {
          // Empty string means clear the groupe_id
          payload.groupe_id = null;
        }
      }
      // If groupe_id is not in data, don't include it (partial update)
      
      console.log('Updating partner with payload:', payload);
      return partnerService.update(id!, payload);
    },
    onSuccess: () => {
      navigate(`/partners/${id}`);
      window.location.reload();
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
                        { value: PartnerType.DISTRIBUTEUR, label: 'Distributeur' },
                        { value: PartnerType.TRANSPORTEUR, label: 'Transporteur' },
                        { value: PartnerType.AUTRE, label: 'Autre' },
                      ]}
                      onChange={(e) => {
                        field.onChange(e.target.value as PartnerType);
                        // Reset groupe_id when type changes
                        if (e.target.value !== PartnerType.DISTRIBUTEUR) {
                          setValue('groupe_id', undefined);
                        } else if (!watch('groupe_id') && activeGroupeId) {
                          // Auto-fill with active groupe if available
                          setValue('groupe_id', activeGroupeId);
                        }
                      }}
                    />
                  )}
                />
                {errors.type && (
                  <p className="mt-1 text-sm text-destructive">{errors.type.message}</p>
                )}
              </div>

              {(selectedType === PartnerType.DISTRIBUTEUR || partner?.type === PartnerType.DISTRIBUTEUR) && (
                <div>
                  <label className="block text-sm font-medium mb-1">
                    Groupe {partner?.type === PartnerType.DISTRIBUTEUR ? '*' : ''}
                  </label>
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
                        {activeGroupeId && !field.value && (
                          <p className="mt-1 text-sm text-blue-600">
                            💡 Votre groupe actif ({groupes?.find(g => g.id === activeGroupeId)?.name || 'Groupe actif'}) peut être sélectionné automatiquement.
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

