import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Dialog, Input, Button, Select } from '../common';
import { rfidTagService } from '../../services/api';
import { RFIDTag, RFIDTagCreate, RFIDTagUpdate, RFIDTagStatus } from '../../types';
import { useState, useEffect } from 'react';

const tagCreateSchema = z.object({
  tag_number: z.string().min(1, 'Le numéro du tag est requis').max(50, 'Maximum 50 caractères'),
  label: z.string().max(255, 'Maximum 255 caractères').optional().or(z.literal('')),
  notes: z.string().max(500, 'Maximum 500 caractères').optional().or(z.literal('')),
});

const tagUpdateSchema = z.object({
  label: z.string().max(255, 'Maximum 255 caractères').optional().or(z.literal('')),
  status: z.nativeEnum(RFIDTagStatus).optional(),
  notes: z.string().max(500, 'Maximum 500 caractères').optional(),
  is_active: z.boolean().optional(),
});

type TagFormData = z.infer<typeof tagCreateSchema> | z.infer<typeof tagUpdateSchema>;

interface RFIDTagFormDialogProps {
  isOpen: boolean;
  onClose: () => void;
  tag?: RFIDTag;
}

export const RFIDTagFormDialog = ({ isOpen, onClose, tag }: RFIDTagFormDialogProps) => {
  const queryClient = useQueryClient();
  const [error, setError] = useState<string | null>(null);
  const isEditMode = !!tag;

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<TagFormData>({
    resolver: zodResolver(isEditMode ? tagUpdateSchema : tagCreateSchema),
    defaultValues: tag
      ? {
          label: tag.label || '',
          status: tag.status,
          notes: tag.notes || '',
          is_active: tag.is_active,
        }
      : {
          tag_number: '',
          label: '',
          notes: '',
        },
  });

  // Reset form when tag changes or dialog opens/closes
  useEffect(() => {
    if (isOpen) {
      if (tag) {
        // Edit mode: populate form with tag data
        reset({
          label: tag.label || '',
          status: tag.status,
          notes: tag.notes || '',
          is_active: tag.is_active,
        });
      } else {
        // Create mode: reset to empty form
        reset({
          tag_number: '',
          label: '',
          notes: '',
        });
      }
    }
  }, [isOpen, tag, reset]);

  const createMutation = useMutation({
    mutationFn: (data: RFIDTagCreate) => rfidTagService.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['rfid-tags'] });
      reset();
      onClose();
    },
    onError: (error: any) => {
      const errorMessage = error.response?.data?.detail || 'Erreur lors de la création du tag RFID';
      // Améliorer le message d'erreur pour l'unicité
      if (error.response?.status === 400 && errorMessage.includes('already exists')) {
        setError('Ce numéro de tag existe déjà. Le numéro de tag doit être unique.');
      } else {
        setError(errorMessage);
      }
    },
  });

  const updateMutation = useMutation({
    mutationFn: (data: RFIDTagUpdate) => rfidTagService.update(tag!.id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['rfid-tags'] });
      reset();
      onClose();
    },
    onError: (error: any) => {
      setError(error.response?.data?.detail || 'Erreur lors de la modification du tag RFID');
    },
  });

  const onSubmit = (data: TagFormData) => {
    setError(null);
    if (isEditMode) {
      // Clean update data: remove empty notes and label
      const updateData: RFIDTagUpdate = {};
      if ((data as any).label !== undefined) {
        const labelValue = String((data as any).label || '').trim();
        updateData.label = labelValue || undefined;
      }
      if ((data as any).status !== undefined) {
        updateData.status = (data as any).status;
      }
      if ((data as any).notes !== undefined && (data as any).notes?.trim()) {
        updateData.notes = (data as any).notes.trim();
      }
      if ((data as any).is_active !== undefined) {
        updateData.is_active = (data as any).is_active;
      }
      updateMutation.mutate(updateData);
    } else {
      // Clean create data: ensure tag_number is present, remove empty notes and label
      const createData: RFIDTagCreate = {
        tag_number: String((data as any).tag_number || '').trim(),
      };
      if ((data as any).label && String((data as any).label).trim()) {
        createData.label = String((data as any).label).trim();
      }
      if ((data as any).notes && String((data as any).notes).trim()) {
        createData.notes = String((data as any).notes).trim();
      }
      createMutation.mutate(createData);
    }
  };

  const statusOptions = [
    { value: RFIDTagStatus.NOT_ASSIGNED, label: 'Non assigné' },
    { value: RFIDTagStatus.ASSIGNED, label: 'Assigné' },
    { value: RFIDTagStatus.LOST, label: 'Perdu' },
    { value: RFIDTagStatus.DAMAGED, label: 'Endommagé' },
  ];

  return (
    <Dialog
      isOpen={isOpen}
      onClose={onClose}
      title={isEditMode ? 'Modifier un tag RFID' : 'Nouveau tag RFID'}
      size="lg"
    >
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        {error && (
          <div className="p-3 bg-red-50 border border-red-200 text-red-700 rounded-lg text-sm">
            {error}
          </div>
        )}

        <div className="space-y-4">
          {!isEditMode && (
            <>
              <Input
                label="Numéro du tag"
                {...register('tag_number')}
                error={'tag_number' in errors ? errors.tag_number?.message : undefined}
                placeholder="RFID-2024-001"
                helperText="Numéro unique du tag RFID (fourni par le lecteur)"
              />
              <Input
                label="Libellé (optionnel)"
                {...register('label')}
                error={'label' in errors ? errors.label?.message : undefined}
                placeholder="Nom personnalisé du tag"
                helperText="Nom ou libellé pour identifier facilement ce tag"
              />
            </>
          )}

          {isEditMode && (
            <>
              <Input
                label="Libellé (optionnel)"
                {...register('label')}
                error={'label' in errors ? errors.label?.message : undefined}
                placeholder="Nom personnalisé du tag"
                helperText="Nom ou libellé pour identifier facilement ce tag"
              />
              <Select
                label="Statut"
                {...register('status')}
                error={'status' in errors ? errors.status?.message : undefined}
                options={statusOptions}
              />
              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  {...register('is_active')}
                  className="h-4 w-4 text-blue-600 rounded focus:ring-blue-500"
                />
                <label className="text-sm font-medium text-gray-700">Tag actif</label>
              </div>
            </>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Notes
            </label>
            <textarea
              {...register('notes')}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
              placeholder="Notes additionnelles (optionnel)"
            />
            {errors.notes && (
              <p className="mt-1 text-sm text-red-600">{errors.notes.message}</p>
            )}
          </div>
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
