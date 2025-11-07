// Expedition types matching backend schemas

export enum ExpeditionStatus {
  CREATED = 'CREATED',
  VALIDATED = 'VALIDATED',
  IN_PREPARATION = 'IN_PREPARATION',
  READY = 'READY',
  DEPARTED = 'DEPARTED',
  IN_TRANSIT = 'IN_TRANSIT',
  DELIVERED = 'DELIVERED',
  COMPLETED = 'COMPLETED',
}

export interface Expedition {
  id: number;
  reference: string;
  status: ExpeditionStatus;
  destination: string;
  destination_contact: string;
  destination_phone: string;
  driver_id?: number;
  grossiste_id?: number;
  departure_date?: string;
  expected_delivery_date?: string;
  actual_delivery_date?: string;
  otp_code?: string;
  otp_expires_at?: string;
  validated_at?: string;
  validated_by?: number;
  total_palettes: number;
  notes?: string;
  created_by: number;
  created_at: string;
  updated_at: string;
  is_deleted: boolean;
  palettes?: number[];
}

export interface ExpeditionCreate {
  destination: string;
  destination_contact: string;
  destination_phone: string;
  grossiste_id?: number;
  expected_delivery_date?: string;
  notes?: string;
  palette_ids?: number[];
}

export interface ExpeditionUpdate {
  destination?: string;
  destination_contact?: string;
  destination_phone?: string;
  driver_id?: number;
  expected_delivery_date?: string;
  notes?: string;
}

export interface ExpeditionAssignPalettes {
  palette_ids: number[];
}

export interface ExpeditionMarkDeparted {
  driver_id: number;
  departure_date?: string;
}

export interface ExpeditionValidateDelivery {
  otp_code: string;
}

export interface ExpeditionStatistics {
  total: number;
  by_status: Record<ExpeditionStatus, number>;
  in_transit: number;
  completed_today: number;
  delayed: number;
  average_delivery_time_hours: number;
  success_rate: number;
}
