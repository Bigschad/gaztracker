import { useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useMutation, useQuery } from '@tanstack/react-query';
import { useForm, Controller } from 'react-hook-form';
import { centreRemplisseurService, partnerService } from '../../services/api';
import { Card, CardHeader, CardTitle, CardContent, Button, Input } from '../../components/common';
import { ArrowLeft } from 'lucide-react';
import { CentreRemplisseurCreate } from '../../types';
import { useToast } from '../../hooks/useToast';
import { getErrorDetails } from '../../utils/errorMessages';

const CreateCentreRemplisseurPage = () => {
  const navigate = useNavigate();
  const { showToast, ToastContainer } = useToast();

  // Fetch next available code
  const { data: nextCodeData } = useQuery({
    queryKey: ['centres-remplisseurs', 'next-code'],
    queryFn: () => centreRemplisseurService.getNextCode(),
  });

  const nextCode = nextCodeData?.code || '';

  // Fetch partners of type DISTRIBUTEUR
  const { data: partnersData } = useQuery({
    queryKey: ['partners', 'DISTRIBUTEUR', 'centres-remplisseurs'],
    queryFn: () => partnerService.list({
      page: 1,
      page_size: 100,
      type: 'DISTRIBUTEUR',
      is_active: true,
    }),
  });

  // Filter to ensure only DISTRIBUTEUR partners are shown
  const distributeurs = partnersData?.items?.filter(partner => partner.type === 'DISTRIBUTEUR') || [];

  const { register, handleSubmit, formState: { errors }, control, setValue } = useForm<CentreRemplisseurCreate>({
    defaultValues: {
      is_active: true,
      country: "Côte d'Ivoire",
    },
  });

  // Set the auto-generated code when it's loaded
  useEffect(() => {
    if (nextCode) {
      setValue('code', nextCode);
    }
  }, [nextCode, setValue]);

  const createMutation = useMutation({
    mutationFn: (data: CentreRemplisseurCreate) => centreRemplisseurService.create(data),
    onSuccess: (data) => {
      showToast({
        type: 'success',
        title: 'Succès',
        message: 'Centre remplisseur créé avec succès',
        duration: 3000,
      });
      setTimeout(() => {
      navigate(`/centres-remplisseurs/${data.id}`);
        window.location.reload();
      }, 500);
    },
    onError: (error) => {
      const errorDetails = getErrorDetails(error);
      showToast({
        type: 'error',
        title: errorDetails.title,
        message: errorDetails.message,
        duration: 7000,
      });
    },
  });

  const onSubmit = (data: CentreRemplisseurCreate) => {
    createMutation.mutate(data);
  };

  return (
    <div className="w-full">
      <ToastContainer />
      <div className="mb-6">
        <Link to="/centres-remplisseurs">
          <Button variant="ghost" size="sm">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Retour
          </Button>
        </Link>
        <h1 className="text-3xl font-bold mt-4">Créer un nouveau centre remplisseur</h1>
      </div>

      <form onSubmit={handleSubmit(onSubmit)}>
        <Card className="w-full">
          <CardHeader>
            <CardTitle>Informations du centre remplisseur</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium mb-1">Nom *</label>
                <Input
                  error={errors.name?.message}
                  {...register('name', { required: 'Le nom est requis' })}
                  placeholder="Nom du centre remplisseur"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Code *</label>
                <Input
                  error={errors.code?.message}
                  {...register('code')}
                  value={nextCode}
                  disabled
                  className="bg-gray-100 cursor-not-allowed"
                  placeholder="Génération automatique..."
                />
                <p className="mt-1 text-xs text-muted-foreground">
                  Code généré automatiquement
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Distributeur *</label>
                <Controller
                  name="partner_id"
                  control={control}
                  rules={{ required: 'Le distributeur est requis' }}
                  render={({ field }) => (
                    <select
                      {...field}
                      className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="">Sélectionner un distributeur</option>
                      {distributeurs.map((partner) => (
                        <option key={partner.id} value={partner.id}>
                          {partner.name}
                        </option>
                      ))}
                    </select>
                  )}
                />
                {errors.partner_id && (
                  <p className="mt-1 text-xs text-red-600">{errors.partner_id.message}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Adresse complète (Google Maps / OpenStreetMap)</label>
                <Input
                  error={errors.address?.message}
                  {...register('address')}
                  placeholder="Ex: 123 Rue Example, Abidjan, Côte d'Ivoire"
                />
                <p className="mt-1 text-xs text-muted-foreground">
                  Saisissez l'adresse complète. Les coordonnées GPS seront récupérées automatiquement depuis l'adresse.
                </p>
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

              <div>
                <label className="block text-sm font-medium mb-1">Pays</label>
                <Input
                  error={errors.country?.message}
                  {...register('country')}
                  placeholder="Pays"
                  defaultValue="Côte d'Ivoire"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Téléphone</label>
                  <Input
                    error={errors.phone?.message}
                    {...register('phone')}
                    placeholder="Téléphone"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-1">Email</label>
                  <Input
                    type="email"
                    error={errors.email?.message}
                    {...register('email')}
                    placeholder="Email"
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
                    placeholder="Téléphone du contact"
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

              <div className="flex items-center">
                <input
                  type="checkbox"
                  {...register('is_active')}
                  className="mr-2"
                  defaultChecked
                />
                <label className="text-sm font-medium">Actif</label>
              </div>

              <div className="flex justify-end space-x-4">
                <Link to="/centres-remplisseurs">
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

export default CreateCentreRemplisseurPage;

