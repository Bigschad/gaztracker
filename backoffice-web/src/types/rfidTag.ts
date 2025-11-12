// RFID Tag types matching backend schemas

export enum RFIDTagStatus {
  NOT_ASSIGNED = 'NOT_ASSIGNED',
  ASSIGNED = 'ASSIGNED',
  LOST = 'LOST',
  DAMAGED = 'DAMAGED',
}

export interface RFIDTag {
  id: string; // UUID
  tag_number: string;
  label?: string;
  status: RFIDTagStatus;
  created_by_id: string; // UUID
  is_active: boolean;
  notes?: string;
  created_at: string;
  updated_at: string;
  assigned_at?: string;
}

export interface RFIDTagDetail extends RFIDTag {
  palette_id?: string; // UUID
}

export interface RFIDTagCreate {
  tag_number: string;
  label?: string;
  notes?: string;
}

export interface RFIDTagUpdate {
  label?: string;
  status?: RFIDTagStatus;
  notes?: string;
  is_active?: boolean;
}

export interface RFIDTagStatistics {
  total_tags: number;
  by_status: Record<string, number>;
  not_assigned: number;
  assigned: number;
  lost: number;
  damaged: number;
  active: number;
  inactive: number;
}

export interface RFIDTagListResponse {
  items: RFIDTag[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
  filters: Record<string, any>;
}

export interface BulkImportResult {
  success: number;
  failed: number;
  errors: Array<{
    row: number;
    tag_number: string;
    error: string;
  }>;
}
