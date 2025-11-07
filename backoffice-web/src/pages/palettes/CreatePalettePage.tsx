import { useNavigate, Link } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { paletteService } from '../../services/api';
import { Card, CardHeader, CardTitle, CardContent, Button, Input } from '../../components/common';
import { ArrowLeft } from 'lucide-react';
import { paletteCreateSchema, PaletteCreateFormData } from '../../utils/validators';

const CreatePalettePage = () => {
  const navigate = useNavigate();

  const { register, handleSubmit, formState: { errors } } = useForm<PaletteCreateFormData>({
    resolver: zodResolver(paletteCreateSchema),
    defaultValues: {
      bottle_quantity: 12,
    },
  });

  const createMutation = useMutation({
    mutationFn: (data: PaletteCreateFormData) => paletteService.create(data as any),
    onSuccess: (data) => {
      navigate(`/palettes/${data.id}`);
    },
  });

  const onSubmit = (data: PaletteCreateFormData) => {
    createMutation.mutate(data);
  };

  return (
    <div>
      <div className="mb-6">
        <Link to="/palettes">
          <Button variant="ghost" size="sm">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Retour
          </Button>
        </Link>
        <h1 className="text-3xl font-bold mt-4">Créer une nouvelle palette</h1>
      </div>

      <Card className="max-w-2xl">
        <CardHeader>
          <CardTitle>Informations de la palette</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">Type de palette</label>
              <select
                {...register('palette_type')}
                className="input w-full"
              >
                <option value="B6">B6 (6kg)</option>
                <option value="B12">B12 (12kg)</option>
                <option value="B28">B28 (28kg)</option>
              </select>
              {errors.palette_type && (
                <p className="mt-1 text-sm text-destructive">{errors.palette_type.message}</p>
              )}
            </div>

            <Input
              label="Quantité de bouteilles"
              type="number"
              error={errors.bottle_quantity?.message}
              {...register('bottle_quantity', { valueAsNumber: true })}
            />

            <Input
              label="Localisation (optionnel)"
              type="text"
              error={errors.current_location?.message}
              {...register('current_location')}
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
                Créer la palette
              </Button>
              <Link to="/palettes">
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

export default CreatePalettePage;
