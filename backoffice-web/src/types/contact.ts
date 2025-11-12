// Contact types matching backend schemas

export interface Contact {
  id: string; // UUID
  partner_id: string; // UUID
  first_name: string;
  last_name: string;
  position?: string | null;
  phone?: string | null;
  email?: string | null;
  is_primary: boolean;
  notes?: string | null;
  created_at: string;
  updated_at: string;
}

export interface ContactCreate {
  partner_id: string; // UUID
  first_name: string;
  last_name: string;
  position?: string;
  phone?: string;
  email?: string;
  is_primary?: boolean;
  notes?: string;
}

export interface ContactUpdate {
  partner_id?: string; // UUID
  first_name?: string;
  last_name?: string;
  position?: string;
  phone?: string;
  email?: string;
  is_primary?: boolean;
  notes?: string;
}

