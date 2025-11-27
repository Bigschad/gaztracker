import { useNavigate, Link } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { useForm, Controller } from 'react-hook-form';
import { centreRemplisseurService } from '../../services/api';
import { Card, CardHeader, CardTitle, CardContent, Button, Input } from '../../components/common';
import { ArrowLeft } from 'lucide-react';
import { CentreRemplisseurCreate } from '../../types';

const CreateCentreRemplisseurPage = () => {
  const navigate = useNavigate();

  // For now, we'll create a simple form that requires grand_distributeur_id
  // In a real scenario, you'd have a separate endpoint for grand distributeurs
  const { register, handleSubmit, formState: { errors }, control } = useForm<CentreRemplisseurCreate>({
    defaultValues: {
      is_active: true,
      country: "Côte d'Ivoire",
    },
  });

  const createMutation = useMutation({
    mutationFn: (data: CentreRemplisseurCreate) => centreRemplisseurService.create(data),
    onSuccess: (data) => {
      navigate(`/centres-remplisseurs/${data.id}`);
    },
  });

  const onSubmit = (data: CentreRemplisseurCreate) => {
    createMutation.mutate(data);
  };

  return (
    <div className="w-full">
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
                <label className="block text-sm font-medium mb-1">Code *</label>
                <Input
                  error={errors.code?.message}
                  {...register('code', { required: 'Le code est requis' })}
                  placeholder="Code unique du centre"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Nom *</label>
                <Input
                  error={errors.name?.message}
                  {...register('name', { required: 'Le nom est requis' })}
                  placeholder="Nom du centre remplisseur"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Grand Distributeur ID *</label>
                <Controller
                  name="grand_distributeur_id"
                  control={control}
                  rules={{ required: 'Le grand distributeur est requis' }}
                  render={({ field }) => (
                    <Input
                      {...field}
                      placeholder="UUID du grand distributeur"
                      error={errors.grand_distributeur_id?.message}
                    />
                  )}
                />
                <p className="mt-1 text-xs text-muted-foreground">
                  Entrez l'UUID du grand distributeur. Un endpoint pour lister les grands distributeurs sera ajouté prochainement.
                </p>
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

