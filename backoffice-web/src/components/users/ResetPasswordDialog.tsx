import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { Dialog, Button, Input } from '../common';
import { userService } from '../../services/api';
import { User } from '../../types';
import { useToast } from '../../hooks/useToast';
import { Key } from 'lucide-react';

interface ResetPasswordDialogProps {
  isOpen: boolean;
  onClose: () => void;
  user: User | null;
}

interface PasswordResetForm {
  newPassword: string;
  confirmPassword: string;
}

export const ResetPasswordDialog: React.FC<ResetPasswordDialogProps> = ({
  isOpen,
  onClose,
  user,
}) => {
  const { showToast, ToastContainer } = useToast();
  const [isResetting, setIsResetting] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
    watch,
  } = useForm<PasswordResetForm>();

  const newPassword = watch('newPassword');

  const onSubmit = async (data: PasswordResetForm) => {
    if (!user) return;

    if (data.newPassword !== data.confirmPassword) {
      showToast({
        type: 'error',
        title: 'Erreur',
        message: 'Les mots de passe ne correspondent pas',
        duration: 3000,
      });
      return;
    }

    try {
      setIsResetting(true);
      await userService.resetPassword(user.id, data.newPassword);
      
      showToast({
        type: 'success',
        title: 'Succès',
        message: `Le mot de passe de ${user.first_name} ${user.last_name} a été réinitialisé avec succès`,
        duration: 3000,
      });
      
      reset();
      onClose();
    } catch (error: any) {
      const errorMessage =
        error.response?.data?.detail ||
        error.message ||
        'Erreur lors de la réinitialisation du mot de passe';
      
      showToast({
        type: 'error',
        title: 'Erreur',
        message: errorMessage,
        duration: 5000,
      });
    } finally {
      setIsResetting(false);
    }
  };

  const validatePassword = (value: string) => {
    if (value.length < 8) {
      return 'Le mot de passe doit contenir au moins 8 caractères';
    }
    if (!/[A-Z]/.test(value)) {
      return 'Le mot de passe doit contenir au moins une majuscule';
    }
    if (!/[a-z]/.test(value)) {
      return 'Le mot de passe doit contenir au moins une minuscule';
    }
    if (!/[0-9]/.test(value)) {
      return 'Le mot de passe doit contenir au moins un chiffre';
    }
    return true;
  };

  return (
    <>
      <ToastContainer />
      <Dialog isOpen={isOpen} onClose={onClose} title="Réinitialiser le mot de passe">
        {user && (
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <p className="text-sm text-blue-800">
                Vous êtes sur le point de réinitialiser le mot de passe de{' '}
                <strong>{user.first_name} {user.last_name}</strong> ({user.email}).
              </p>
              <p className="text-sm text-blue-700 mt-2">
                L'utilisateur devra utiliser ce nouveau mot de passe pour se connecter.
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">
                Nouveau mot de passe *
              </label>
              <Input
                type="password"
                error={errors.newPassword?.message}
                {...register('newPassword', {
                  required: 'Le nouveau mot de passe est requis',
                  validate: validatePassword,
                })}
                placeholder="Nouveau mot de passe"
                autoComplete="new-password"
              />
              <p className="mt-1 text-xs text-muted-foreground">
                Minimum 8 caractères, avec au moins une majuscule, une minuscule et un chiffre
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">
                Confirmer le mot de passe *
              </label>
              <Input
                type="password"
                error={errors.confirmPassword?.message}
                {...register('confirmPassword', {
                  required: 'Veuillez confirmer le mot de passe',
                  validate: (value) => {
                    if (value !== newPassword) {
                      return 'Les mots de passe ne correspondent pas';
                    }
                    return true;
                  },
                })}
                placeholder="Confirmer le mot de passe"
                autoComplete="new-password"
              />
            </div>

            <div className="flex justify-end space-x-3 pt-4">
              <Button type="button" variant="outline" onClick={onClose} disabled={isResetting}>
                Annuler
              </Button>
              <Button type="submit" disabled={isResetting}>
                {isResetting ? (
                  'Réinitialisation...'
                ) : (
                  <>
                    <Key className="h-4 w-4 mr-2" />
                    Réinitialiser le mot de passe
                  </>
                )}
              </Button>
            </div>
          </form>
        )}
      </Dialog>
    </>
  );
};
