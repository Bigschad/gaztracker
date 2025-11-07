// Palette types matching backend schemas

export enum PaletteType {
  B6 = 'B6',
  B12 = 'B12',
  B28 = 'B28',
}

export enum PaletteStatus {
  CREATED = 'CREATED',
  IN_STOCK = 'IN_STOCK',
  ASSIGNED = 'ASSIGNED',
  IN_TRANSIT = 'IN_TRANSIT',
  DELIVERED = 'DELIVERED',
  RETURNED = 'RETURNED',
  MAINTENANCE = 'MAINTENANCE',
  LOST = 'LOST',
}

export interface Palette {
  id: number;
  rfid_tag: string;
  palette_type: PaletteType;
  bottle_quantity: number;
  status: PaletteStatus;
  current_location?: string;
  assigned_to?: number;
  expedition_id?: number;
  notes?: string;
  created_by: number;
  created_at: string;
  updated_at: string;
  is_deleted: boolean;
}

export interface PaletteCreate {
  palette_type: PaletteType;
  bottle_quantity: number;
  current_location?: string;
  notes?: string;
}

export interface PaletteUpdate {
  status?: PaletteStatus;
  current_location?: string;
  notes?: string;
}

export interface PaletteScan {
  rfid_tag: string;
  location?: string;
  notes?: string;
}

export interface PaletteStatistics {
  total: number;
  by_status: Record<PaletteStatus, number>;
  by_type: Record<PaletteType, number>;
  in_transit: number;
  available: number;
  utilization_rate: number;
}

export interface PaletteMovement {
  id: number;
  palette_id: number;
  from_status: PaletteStatus;
  to_status: PaletteStatus;
  from_location?: string;
  to_location?: string;
  expedition_id?: number;
  moved_by: number;
  notes?: string;
  created_at: string;
}
