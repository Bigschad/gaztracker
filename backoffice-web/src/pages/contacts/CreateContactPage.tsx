import { useNavigate, Link, useSearchParams } from 'react-router-dom';
import { useMutation, useQuery } from '@tanstack/react-query';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { contactService, partnerService } from '../../services/api';
import { Card, CardHeader, CardTitle, CardContent, Button, Input, Select } from '../../components/common';
import { ArrowLeft } from 'lucide-react';
import { contactCreateSchema, ContactCreateFormData } from '../../utils/validators';

const CreateContactPage = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const defaultPartnerId = searchParams.get('partner_id') || '';

  const { data: partnersData } = useQuery({
    queryKey: ['partners', 'all'],
    queryFn: () => partnerService.list({ page: 1, page_size: 100 }),
  });


  const { register, handleSubmit, control, formState: { errors } } = useForm<ContactCreateFormData>({
    resolver: zodResolver(contactCreateSchema),
    defaultValues: {
      partner_id: defaultPartnerId,
      is_primary: false,
    },
  });

  const createMutation = useMutation({
    mutationFn: (data: ContactCreateFormData) => contactService.create(data),
    onSuccess: (data) => {
      navigate(`/contacts/${data.id}`);
    },
  });

  const onSubmit = (data: ContactCreateFormData) => {
    createMutation.mutate(data);
  };

  return (
    <div className="w-full">
      <div className="mb-6">
        <Link to="/contacts">
          <Button variant="ghost" size="sm">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Retour
          </Button>
        </Link>
        <h1 className="text-3xl font-bold mt-4">Créer un nouveau contact</h1>
      </div>

      <form onSubmit={handleSubmit(onSubmit)}>
        <Card className="w-full">
          <CardHeader>
            <CardTitle>Informations du contact</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium mb-1">Partenaire *</label>
                <Controller
                  name="partner_id"
                  control={control}
                  render={({ field }) => (
                    <Select
                      {...field}
                      options={[
                        { value: '', label: 'Sélectionner un partenaire' },
                        ...(partnersData?.items || []).map((p) => ({
                          value: p.id,
                          label: p.name,
                        })),
                      ]}
                    />
                  )}
                />
                {errors.partner_id && (
                  <p className="mt-1 text-sm text-destructive">{errors.partner_id.message}</p>
                )}
              </div>

              <div className="grid grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium mb-1">Prénom *</label>
                  <Input
                    error={errors.first_name?.message}
                    {...register('first_name')}
                    placeholder="Prénom"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Nom *</label>
                  <Input
                    error={errors.last_name?.message}
                    {...register('last_name')}
                    placeholder="Nom"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Poste</label>
                <Input
                  error={errors.position?.message}
                  {...register('position')}
                  placeholder="Poste"
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
                    {...register('is_primary')}
                    className="rounded"
                  />
                  <span className="text-sm font-medium">Contact principal</span>
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
                  Créer le contact
                </Button>
                <Link to="/contacts">
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

export default CreateContactPage;

