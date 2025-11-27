// Depot types matching backend schemas

export interface Depot {
  id: string; // UUID
  name: string;
  code?: string | null;
  partner_id: string; // UUID
  address?: string | null;
  city?: string | null;
  postal_code?: string | null;
  latitude?: number | null;
  longitude?: number | null;
  contact_name?: string | null;
  contact_phone?: string | null;
  capacity_b28?: number | null;
  capacity_b12?: number | null;
  capacity_b6?: number | null;
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
  city?: string | null;
  is_active: boolean;
  is_main_depot: boolean;
}

export interface DepotDetail extends Depot {
  partner_name?: string | null;
  partner_type?: string | null;
  total_capacity?: number | null;
  palettes_count?: number | null;
}

export interface DepotLocation {
  id: string;
  name: string;
  latitude?: number | null;
  longitude?: number | null;
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
  latitude?: number;
  longitude?: number;
  contact_name?: string;
  contact_phone?: string;
  capacity_b28?: number;
  capacity_b12?: number;
  capacity_b6?: number;
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
  latitude?: number;
  longitude?: number;
  contact_name?: string;
  contact_phone?: string;
  capacity_b28?: number;
  capacity_b12?: number;
  capacity_b6?: number;
  is_active?: boolean;
  is_main_depot?: boolean;
  notes?: string;
}

