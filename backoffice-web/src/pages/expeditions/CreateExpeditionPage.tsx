import { useNavigate, Link } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { expeditionService } from '../../services/api';
import { Card, CardHeader, CardTitle, CardContent, Button, Input } from '../../components/common';
import { ArrowLeft } from 'lucide-react';
import { expeditionCreateSchema, ExpeditionCreateFormData } from '../../utils/validators';

const CreateExpeditionPage = () => {
  const navigate = useNavigate();

  const { register, handleSubmit, formState: { errors } } = useForm<ExpeditionCreateFormData>({
    resolver: zodResolver(expeditionCreateSchema),
  });

  const createMutation = useMutation({
    mutationFn: expeditionService.create,
    onSuccess: (data) => {
      navigate(`/expeditions/${data.id}`);
    },
  });

  const onSubmit = (data: ExpeditionCreateFormData) => {
    createMutation.mutate(data);
  };

  return (
    <div>
      <div className="mb-6">
        <Link to="/expeditions">
          <Button variant="ghost" size="sm">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Retour
          </Button>
        </Link>
        <h1 className="text-3xl font-bold mt-4">Créer une nouvelle expédition</h1>
      </div>

      <Card className="max-w-2xl">
        <CardHeader>
          <CardTitle>Informations de l'expédition</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <Input
              label="Destination"
              type="text"
              error={errors.destination?.message}
              {...register('destination')}
            />

            <Input
              label="Contact"
              type="text"
              error={errors.destination_contact?.message}
              {...register('destination_contact')}
            />

            <Input
              label="Téléphone"
              type="tel"
              error={errors.destination_phone?.message}
              {...register('destination_phone')}
            />

            <Input
              label="Date de livraison prévue (optionnel)"
              type="datetime-local"
              error={errors.expected_delivery_date?.message}
              {...register('expected_delivery_date')}
            />

            <div>
              <label className="block text-sm font-medium mb-2">Notes (optionnel)</label>
              <textarea
                {...register('notes')}
                className="input w-full min-h-[100px]"
              />
            </div>

            <div className="flex space-x-3">
              <Button type="submit" isLoading={createMutation.isPending}>
                Créer l'expédition
              </Button>
              <Link to="/expeditions">
                <Button type="button" variant="outline">
                  Annuler
                </Button>
              </Link>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
};

export default CreateExpeditionPage;
