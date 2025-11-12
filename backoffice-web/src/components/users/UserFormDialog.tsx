import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Dialog, Input, Select, Button } from '../common';
import { userService } from '../../services/api';
import { User, UserRole, UserCreate, UserUpdate } from '../../types';
import { useState, useEffect } from 'react';

const userCreateSchema = z.object({
  email: z.string().email('Email invalide'),
  password: z.string()
    .min(8, 'Le mot de passe doit contenir au moins 8 caractères')
    .regex(/[A-Z]/, 'Le mot de passe doit contenir au moins une majuscule')
    .regex(/[a-z]/, 'Le mot de passe doit contenir au moins une minuscule')
    .regex(/[0-9]/, 'Le mot de passe doit contenir au moins un chiffre'),
  first_name: z.string().min(1, 'Le prénom est requis'),
  last_name: z.string().min(1, 'Le nom est requis'),
  phone_number: z.string().optional(),
  company_name: z.string().optional(),
  role: z.nativeEnum(UserRole),
});

const userUpdateSchema = z.object({
  email: z.string().email('Email invalide').optional(),
  first_name: z.string().min(1, 'Le prénom est requis').optional(),
  last_name: z.string().min(1, 'Le nom est requis').optional(),
  phone_number: z.string().optional(),
  company_name: z.string().optional(),
  role: z.nativeEnum(UserRole).optional(),
  is_active: z.boolean().optional(),
  is_verified: z.boolean().optional(),
});

type UserFormData = z.infer<typeof userCreateSchema> | z.infer<typeof userUpdateSchema>;

interface UserFormDialogProps {
  isOpen: boolean;
  onClose: () => void;
  user?: User;
}

export const UserFormDialog = ({ isOpen, onClose, user }: UserFormDialogProps) => {
  const queryClient = useQueryClient();
  const [error, setError] = useState<string | null>(null);
  const isEditMode = !!user;

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<UserFormData>({
    resolver: zodResolver(isEditMode ? userUpdateSchema : userCreateSchema),
    defaultValues: user ? {
      email: user.email,
      first_name: user.first_name,
      last_name: user.last_name,
      phone_number: user.phone_number || '',
      company_name: user.company_name || '',
      role: user.role,
      is_active: user.is_active,
      is_verified: user.is_verified,
    } : {
      email: '',
      password: '',
      first_name: '',
      last_name: '',
      phone_number: '',
      company_name: '',
      role: UserRole.OPERATEUR_USINE,
    },
  });

  // Reset form when user changes or dialog opens/closes
  useEffect(() => {
    if (isOpen) {
      if (user) {
        // Edit mode: populate form with user data
        reset({
          email: user.email,
          first_name: user.first_name,
          last_name: user.last_name,
          phone_number: user.phone_number || '',
          company_name: user.company_name || '',
          role: user.role,
          is_active: user.is_active,
          is_verified: user.is_verified,
        });
      } else {
        // Create mode: reset to empty form
        reset({
          email: '',
          password: '',
          first_name: '',
          last_name: '',
          phone_number: '',
          company_name: '',
          role: UserRole.OPERATEUR_USINE,
        });
      }
    }
  }, [isOpen, user, reset]);

  const createMutation = useMutation({
    mutationFn: (data: UserCreate) => userService.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
      reset();
      onClose();
    },
    onError: (error: any) => {
      setError(error.response?.data?.detail || 'Erreur lors de la création de l\'utilisateur');
    },
  });

  const updateMutation = useMutation({
    mutationFn: (data: UserUpdate) => userService.update(user!.id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
      reset();
      onClose();
    },
    onError: (error: any) => {
      setError(error.response?.data?.detail || 'Erreur lors de la modification de l\'utilisateur');
    },
  });

  const onSubmit = (data: UserFormData) => {
    setError(null);
    if (isEditMode) {
      updateMutation.mutate(data as UserUpdate);
    } else {
      createMutation.mutate(data as UserCreate);
    }
  };

  const roleOptions = [
    { value: UserRole.ADMIN, label: 'Administrateur' },
    { value: UserRole.RESPONSABLE_LOGISTIQUE, label: 'Responsable Logistique' },
    { value: UserRole.OPERATEUR_USINE, label: 'Opérateur Usine' },
    { value: UserRole.CHAUFFEUR, label: 'Chauffeur' },
    { value: UserRole.GROSSISTE, label: 'Grossiste' },
  ];

  return (
    <Dialog
      isOpen={isOpen}
      onClose={onClose}
      title={isEditMode ? 'Modifier un utilisateur' : 'Nouvel utilisateur'}
      size="lg"
    >
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        {error && (
          <div className="p-3 bg-red-50 border border-red-200 text-red-700 rounded-lg text-sm">
            {error}
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Input
            label="Email"
            type="email"
            {...register('email')}
            error={errors.email?.message}
            placeholder="john@example.com"
          />

          <Input
            label="Prénom"
            {...register('first_name')}
            error={errors.first_name?.message}
            placeholder="John"
          />

          <Input
            label="Nom"
            {...register('last_name')}
            error={errors.last_name?.message}
            placeholder="Doe"
          />

          <Input
            label="Téléphone"
            type="tel"
            {...register('phone_number')}
            error={errors.phone_number?.message}
            placeholder="+33 6 12 34 56 78"
          />

          <Input
            label="Entreprise"
            {...register('company_name')}
            error={errors.company_name?.message}
            placeholder="Nom de l'entreprise (optionnel)"
          />

          <Select
            label="Rôle"
            {...register('role')}
            error={errors.role?.message}
            options={roleOptions}
          />

          {!isEditMode && (
            <Input
              label="Mot de passe"
              type="password"
              {...register('password')}
              error={'password' in errors ? errors.password?.message : undefined}
              placeholder="••••••••"
            />
          )}

          {isEditMode && (
            <>
              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  {...register('is_active')}
                  className="h-4 w-4 text-blue-600 rounded focus:ring-blue-500"
                />
                <label className="text-sm font-medium text-gray-700">
                  Compte actif
                </label>
              </div>
              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  {...register('is_verified')}
                  className="h-4 w-4 text-blue-600 rounded focus:ring-blue-500"
                />
                <label className="text-sm font-medium text-gray-700">
                  Email vérifié
                </label>
              </div>
            </>
          )}
        </div>

        <div className="flex justify-end space-x-3 pt-4">
          <Button type="button" variant="outline" onClick={onClose}>
            Annuler
          </Button>
          <Button
            type="submit"
            disabled={createMutation.isPending || updateMutation.isPending}
          >
            {createMutation.isPending || updateMutation.isPending
              ? 'En cours...'
              : isEditMode
              ? 'Modifier'
              : 'Créer'}
          </Button>
        </div>
      </form>
    </Dialog>
  );
};
