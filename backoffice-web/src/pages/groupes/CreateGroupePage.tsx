import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import { Card, CardHeader, CardTitle, CardContent, Button, Input } from '../../components/common';
import { groupeService, uploadService } from '../../services/api';
import { GroupeCreate } from '../../types';
import { ArrowLeft, Upload, X } from 'lucide-react';
import { useToast } from '../../hooks/useToast';
import { getErrorDetails } from '../../utils/errorMessages';

const CreateGroupePage = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { showToast, ToastContainer } = useToast();
  const [logoFile, setLogoFile] = useState<File | null>(null);
  const [logoPreview, setLogoPreview] = useState<string | null>(null);
  const [uploadingLogo, setUploadingLogo] = useState(false);

  const { register, handleSubmit, formState: { errors }, setValue } = useForm<GroupeCreate>({
    defaultValues: {
      is_active: true,
    },
  });

  const createMutation = useMutation({
    mutationFn: groupeService.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['groupes'] });
      showToast({
        type: 'success',
        title: 'Succès',
        message: 'Groupe créé avec succès',
        duration: 3000,
      });
      setTimeout(() => {
      navigate('/groupes');
        window.location.reload();
      }, 500);
    },
    onError: (error: any) => {
      const errorDetails = getErrorDetails(error);
      showToast({
        type: 'error',
        title: errorDetails.title,
        message: errorDetails.message,
        duration: 7000,
      });
    },
  });

  const handleLogoChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      // Validate file type
      const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/svg+xml', 'image/webp'];
      if (!validTypes.includes(file.type)) {
        alert('Format non autorisé. Utilisez JPG, PNG, GIF, SVG ou WEBP');
        return;
      }

      // Validate file size (5MB)
      if (file.size > 5 * 1024 * 1024) {
        alert('Fichier trop volumineux. Taille maximale: 5MB');
        return;
      }

      setLogoFile(file);
      
      // Create preview
      const reader = new FileReader();
      reader.onloadend = () => {
        setLogoPreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleRemoveLogo = () => {
    setLogoFile(null);
    setLogoPreview(null);
    setValue('logo_url', undefined);
  };

  const onSubmit = async (data: GroupeCreate) => {
    try {
      // Upload logo first if provided
      if (logoFile) {
        setUploadingLogo(true);
        const uploadResult = await uploadService.uploadLogo(logoFile);
        data.logo_url = uploadResult.url;
        setUploadingLogo(false);
      }

      createMutation.mutate(data);
    } catch (error: any) {
      setUploadingLogo(false);
      alert(error.response?.data?.detail || 'Erreur lors de l\'upload du logo');
    }
  };

  return (
    <div className="space-y-6">
      <ToastContainer />
      <div className="flex items-center gap-4">
        <Link to="/groupes">
          <Button variant="secondary">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Retour
          </Button>
        </Link>
        <div>
          <h1 className="text-3xl font-bold">Nouveau Groupe</h1>
          <p className="text-gray-600">Créer un nouveau groupe</p>
        </div>
      </div>

      <form onSubmit={handleSubmit(onSubmit)}>
        <Card>
          <CardHeader>
            <CardTitle>Informations du groupe</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {/* Logo Upload */}
              <div>
                <label className="block text-sm font-medium mb-2">Logo du groupe</label>
                <div className="flex items-start gap-4">
                  {/* Preview */}
                  {logoPreview ? (
                    <div className="relative">
                      <img
                        src={logoPreview}
                        alt="Logo preview"
                        className="w-24 h-24 object-contain border rounded-lg p-2"
                      />
                      <button
                        type="button"
                        onClick={handleRemoveLogo}
                        className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full p-1 hover:bg-red-600"
                      >
                        <X className="h-3 w-3" />
                      </button>
                    </div>
                  ) : (
                    <div className="w-24 h-24 border-2 border-dashed rounded-lg flex items-center justify-center bg-gray-50">
                      <Upload className="h-8 w-8 text-gray-400" />
                    </div>
                  )}

                  {/* Upload button */}
                  <div className="flex-1">
                    <input
                      type="file"
                      id="logo-upload"
                      accept="image/jpeg,image/jpg,image/png,image/gif,image/svg+xml,image/webp"
                      onChange={handleLogoChange}
                      className="hidden"
                    />
                    <label
                      htmlFor="logo-upload"
                      className="inline-flex items-center px-4 py-2 border rounded-lg cursor-pointer hover:bg-accent transition-colors"
                    >
                      <Upload className="h-4 w-4 mr-2" />
                      Choisir un logo
                    </label>
                    <p className="text-xs text-muted-foreground mt-2">
                      JPG, PNG, GIF, SVG ou WEBP - Max 5MB
                    </p>
                  </div>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Nom *</label>
                <Input
                  error={errors.name?.message}
                  {...register('name', { required: 'Le nom est requis' })}
                  placeholder="Nom du groupe"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Code *</label>
                <Input
                  error={errors.code?.message}
                  {...register('code', { required: 'Le code est requis' })}
                  placeholder="Code unique"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Adresse</label>
                <Input
                  error={errors.address?.message}
                  {...register('address')}
                  placeholder="Adresse"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Ville</label>
                <Input
                  error={errors.city?.message}
                  {...register('city')}
                  placeholder="Ville"
                />
              </div>

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
                <Link to="/groupes">
                  <Button type="button" variant="outline">Annuler</Button>
                </Link>
                <Button type="submit" disabled={createMutation.isPending || uploadingLogo}>
                  {uploadingLogo ? 'Upload du logo...' : createMutation.isPending ? 'Création...' : 'Créer'}
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </form>
    </div>
  );
};

export default CreateGroupePage;
