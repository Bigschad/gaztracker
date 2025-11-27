// Centre Remplisseur types matching backend schemas

export interface CentreRemplisseur {
  id: string; // UUID
  name: string;
  code: string;
  grand_distributeur_id: string; // UUID
  address?: string | null;
  city?: string | null;
  postal_code?: string | null;
  country?: string | null;
  phone?: string | null;
  email?: string | null;
  contact_name?: string | null;
  contact_phone?: string | null;
  is_active: boolean;
  latitude?: number | null;
  longitude?: number | null;
  notes?: string | null;
  created_at: string;
  updated_at: string;
}

export interface CentreRemplisseurList {
  id: string;
  name: string;
  code: string;
  grand_distributeur_id: string;
  city?: string | null;
  is_active: boolean;
}

export interface CentreRemplisseurDetail extends CentreRemplisseur {
  grand_distributeur_name?: string | null;
  groupe_name?: string | null;
  bons_enlevement_count?: number | null;
  bons_retour_count?: number | null;
}

export interface CentreRemplisseurCreate {
  name: string;
  code: string;
  grand_distributeur_id: string;
  address?: string;
  city?: string;
  postal_code?: string;
  country?: string;
  phone?: string;
  email?: string;
  contact_name?: string;
  contact_phone?: string;
  is_active?: boolean;
  latitude?: number;
  longitude?: number;
  notes?: string;
}

export interface CentreRemplisseurUpdate {
  name?: string;
  code?: string;
  grand_distributeur_id?: string;
  address?: string;
  city?: string;
  postal_code?: string;
  country?: string;
  phone?: string;
  email?: string;
  contact_name?: string;
  contact_phone?: string;
  is_active?: boolean;
  latitude?: number;
  longitude?: number;
  notes?: string;
}

