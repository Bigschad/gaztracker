// Groupe types matching backend schemas

export interface Groupe {
  id: string; // UUID
  name: string;
  code: string;
  address?: string | null;
  city?: string | null;
  phone?: string | null;
  email?: string | null;
  logo_url?: string | null;
  is_active: boolean;
  notes?: string | null;
  created_at: string;
  updated_at: string;
}

export interface GroupeList {
  id: string;
  name: string;
  code: string;
  logo_url?: string | null;
  is_active: boolean;
}

export interface GroupeDetail extends Groupe {
  grand_distributeurs_count?: number | null;
}

export interface GroupeCreate {
  name: string;
  code: string;
  address?: string;
  city?: string;
  phone?: string;
  email?: string;
  logo_url?: string;
  is_active?: boolean;
  notes?: string;
}

export interface GroupeUpdate {
  name?: string;
  code?: string;
  address?: string;
  city?: string;
  phone?: string;
  email?: string;
  logo_url?: string;
  is_active?: boolean;
  notes?: string;
}

