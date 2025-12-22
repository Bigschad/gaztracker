// Depot types matching backend schemas

export interface Depot {
  id: string; // UUID
  name: string;
  code?: string | null;
  partner_id: string; // UUID
  address?: string | null;
  city?: string | null;
  postal_code?: string | null;
  contact_name?: string | null;
  contact_phone?: string | null;
  is_active: boolean;
  is_main_depot: boolean;
  notes?: string | null;
  created_at: string;
  updated_at: string;
}

export interface DepotList {
  id: string;
  name: string;
  code?: string | null;
  partner_id: string;
  partner_name?: string | null;
  city?: string | null;
  is_active: boolean;
  is_main_depot: boolean;
}

export interface DepotDetail extends Depot {
  partner_name?: string | null;
  partner_type?: string | null;
  palettes_count?: number | null;
}

export interface DepotLocation {
  id: string;
  name: string;
  address?: string | null;
  city?: string | null;
}

export interface DepotCreate {
  name: string;
  code?: string;
  partner_id: string;
  address?: string;
  city?: string;
  postal_code?: string;
  contact_name?: string;
  contact_phone?: string;
  is_active?: boolean;
  is_main_depot?: boolean;
  notes?: string;
}

export interface DepotUpdate {
  name?: string;
  code?: string;
  partner_id?: string;
  address?: string;
  city?: string;
  postal_code?: string;
  contact_name?: string;
  contact_phone?: string;
  is_active?: boolean;
  is_main_depot?: boolean;
  notes?: string;
}

