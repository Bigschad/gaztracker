// Partner types matching backend schemas

export enum PartnerType {
  GROSSISTE = 'GROSSISTE',
  FOURNISSEUR = 'FOURNISSEUR',
  TRANSPORTEUR = 'TRANSPORTEUR',
  AUTRE = 'AUTRE',
}

export interface Partner {
  id: string; // UUID
  name: string;
  type: PartnerType;
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
  address?: string;
  city?: string;
  postal_code?: string;
  country?: string;
  phone?: string;
  email?: string;
  is_active?: boolean;
  notes?: string;
}

