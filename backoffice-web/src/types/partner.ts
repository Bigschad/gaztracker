// Partner types matching backend schemas

export enum PartnerType {
  GROSSISTE = 'GROSSISTE',
  DISTRIBUTEUR = 'DISTRIBUTEUR',
  TRANSPORTEUR = 'TRANSPORTEUR',
  AUTRE = 'AUTRE',
}

import { Groupe } from './groupe';

export interface Partner {
  id: string; // UUID
  name: string;
  code?: string | null;
  type: PartnerType;
  groupe_id?: string | null; // UUID
  groupe?: Groupe | null; // Groupe details (for DISTRIBUTEUR)
  address?: string | null;
  city?: string | null;
  postal_code?: string | null;
  country?: string | null;
  phone?: string | null;
  email?: string | null;
  is_active: boolean;
  notes?: string | null;
  created_at: string;
  updated_at: string;
}

export interface PartnerCreate {
  name: string;
  type: PartnerType;
  groupe_id?: string; // UUID (for DISTRIBUTEUR)
  address?: string;
  city?: string;
  postal_code?: string;
  country?: string;
  phone?: string;
  email?: string;
  is_active?: boolean;
  notes?: string;
}

export interface PartnerUpdate {
  name?: string;
  type?: PartnerType;
  groupe_id?: string | null; // UUID (for DISTRIBUTEUR)
  address?: string;
  city?: string;
  postal_code?: string;
  country?: string;
  phone?: string;
  email?: string;
  is_active?: boolean;
  notes?: string;
}

