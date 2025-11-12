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
  reference_code: z.string().max(50, 'Le code de référence ne peut pas dépasser 50 caractères').optional().or(z.literal('')),
  palette_type: z.enum(['B6', 'B12', 'B28'], {
    required_error: 'Le type de palette est requis',
  }),
  capacity: z.number().min(1, 'La capacité doit être au moins 1').optional(),
  manufacturing_date: z.string().optional().or(z.literal('')),
  rfid_tag_id: z.string().uuid('ID tag RFID invalide').optional().or(z.literal('')),
  current_partner_id: z.string().uuid('ID partenaire invalide').optional().or(z.literal('')),
  notes: z.string().optional(),
});

/**
 * Expedition creation validation schema
 */
export const expeditionCreateSchema = z.object({
  libelle: z.string().min(1, 'Le libellé est requis'),
  destination_address: z.string().min(1, 'L\'adresse de destination est requise'),
  destination_contact: z.string().optional(),
  destination_phone: z.string().optional(),
  transporter: z.string().optional(),
  vehicle_info: z.string().optional(),
  grossiste_id: z.string().optional(),
  driver_id: z.string().optional(),
  expected_delivery_date: z.string().optional(),
  notes: z.string().optional(),
  palette_ids: z.array(z.string()).optional(),
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

/**
 * Partner creation validation schema
 */
export const partnerCreateSchema = z.object({
  name: z.string().min(1, 'Le nom est requis').max(255, 'Le nom ne peut pas dépasser 255 caractères'),
  type: z.enum(['GROSSISTE', 'FOURNISSEUR', 'TRANSPORTEUR', 'AUTRE'], {
    required_error: 'Le type de partenaire est requis',
  }),
  address: z.string().max(500, 'L\'adresse ne peut pas dépasser 500 caractères').optional(),
  city: z.string().max(100, 'La ville ne peut pas dépasser 100 caractères').optional(),
  postal_code: z.string().max(20, 'Le code postal ne peut pas dépasser 20 caractères').optional(),
  country: z.string().max(100, 'Le pays ne peut pas dépasser 100 caractères').optional(),
  phone: z.string().max(20, 'Le téléphone ne peut pas dépasser 20 caractères').optional(),
  email: z.string().email('Email invalide').max(255, 'L\'email ne peut pas dépasser 255 caractères').optional().or(z.literal('')),
  is_active: z.boolean().optional(),
  notes: z.string().max(1000, 'Les notes ne peuvent pas dépasser 1000 caractères').optional(),
});

/**
 * Partner update validation schema
 */
export const partnerUpdateSchema = partnerCreateSchema.partial();

/**
 * Contact creation validation schema
 */
export const contactCreateSchema = z.object({
  partner_id: z.string().uuid('ID partenaire invalide'),
  first_name: z.string().min(1, 'Le prénom est requis').max(100, 'Le prénom ne peut pas dépasser 100 caractères'),
  last_name: z.string().min(1, 'Le nom est requis').max(100, 'Le nom ne peut pas dépasser 100 caractères'),
  position: z.string().max(100, 'Le poste ne peut pas dépasser 100 caractères').optional(),
  phone: z.string().max(20, 'Le téléphone ne peut pas dépasser 20 caractères').optional(),
  email: z.string().email('Email invalide').max(255, 'L\'email ne peut pas dépasser 255 caractères').optional().or(z.literal('')),
  is_primary: z.boolean().optional(),
  notes: z.string().max(1000, 'Les notes ne peuvent pas dépasser 1000 caractères').optional(),
});

/**
 * Contact update validation schema
 */
export const contactUpdateSchema = contactCreateSchema.partial();

export type LoginFormData = z.infer<typeof loginSchema>;
export type PaletteCreateFormData = z.infer<typeof paletteCreateSchema>;
export type ExpeditionCreateFormData = z.infer<typeof expeditionCreateSchema>;
export type UserCreateFormData = z.infer<typeof userCreateSchema>;
export type PartnerCreateFormData = z.infer<typeof partnerCreateSchema>;
export type PartnerUpdateFormData = z.infer<typeof partnerUpdateSchema>;
export type ContactCreateFormData = z.infer<typeof contactCreateSchema>;
export type ContactUpdateFormData = z.infer<typeof contactUpdateSchema>;
