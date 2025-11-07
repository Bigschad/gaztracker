import { z } from 'zod';

/**
 * Login form validation schema
 */
export const loginSchema = z.object({
  email: z.string().email('Email invalide').min(1, 'L\'email est requis'),
  password: z.string().min(1, 'Le mot de passe est requis'),
});

/**
 * Palette creation validation schema
 */
export const paletteCreateSchema = z.object({
  palette_type: z.enum(['B6', 'B12', 'B28'], {
    required_error: 'Le type de palette est requis',
  }),
  bottle_quantity: z.number().min(1, 'La quantité doit être au moins 1'),
  current_location: z.string().optional(),
  notes: z.string().optional(),
});

/**
 * Expedition creation validation schema
 */
export const expeditionCreateSchema = z.object({
  destination: z.string().min(1, 'La destination est requise'),
  destination_contact: z.string().min(1, 'Le contact est requis'),
  destination_phone: z
    .string()
    .min(1, 'Le téléphone est requis')
    .regex(/^[0-9+\s-]+$/, 'Format de téléphone invalide'),
  grossiste_id: z.number().optional(),
  expected_delivery_date: z.string().optional(),
  notes: z.string().optional(),
  palette_ids: z.array(z.number()).optional(),
});

/**
 * User creation validation schema
 */
export const userCreateSchema = z.object({
  username: z.string().min(3, 'Le nom d\'utilisateur doit avoir au moins 3 caractères'),
  email: z.string().email('Email invalide'),
  password: z.string().min(6, 'Le mot de passe doit avoir au moins 6 caractères'),
  full_name: z.string().min(1, 'Le nom complet est requis'),
  role: z.enum(['ADMIN', 'RESPONSABLE_LOGISTIQUE', 'OPERATEUR_USINE', 'CHAUFFEUR', 'GROSSISTE'], {
    required_error: 'Le rôle est requis',
  }),
  phone: z.string().optional(),
});

export type LoginFormData = z.infer<typeof loginSchema>;
export type PaletteCreateFormData = z.infer<typeof paletteCreateSchema>;
export type ExpeditionCreateFormData = z.infer<typeof expeditionCreateSchema>;
export type UserCreateFormData = z.infer<typeof userCreateSchema>;
