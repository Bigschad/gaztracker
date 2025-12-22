// Palette types matching backend schemas

import { RFIDTag } from './rfidTag';
import { CentreRemplisseur } from './centreRemplisseur';

export enum PaletteType {
  B6 = 'B6',
  B12 = 'B12',
  B28 = 'B28',
}

export enum PaletteStatus {
  CREATION = 'CREATION',
  AU_CENTRE = 'AU_CENTRE',
  EN_CHARGEMENT = 'EN_CHARGEMENT',
  EN_ROUTE_LIVRAISON = 'EN_ROUTE_LIVRAISON',
  AU_DEPOT = 'AU_DEPOT',
  EN_ROUTE_RETOUR = 'EN_ROUTE_RETOUR',
  EN_CONTROLE = 'EN_CONTROLE',
  VALIDEE = 'VALIDEE',
  OUT = 'OUT',
}

export enum PaletteCondition {
  NEUVE = 'NEUVE',
  RECONDITIONNEE = 'RECONDITIONNEE',
}

export interface Palette {
  id: string; // UUID
  serial_number: string; // Numéro de série unique (PAL-YYYY-NNNNN)
  reference_code?: string | null; // Code de référence personnalisé
  rfid_tag_id?: string | null; // UUID
  rfid_tag?: RFIDTag | null; // Tag RFID complet
  type: PaletteType;
  condition?: PaletteCondition | null; // Condition de la palette (NEUVE ou RECONDITIONNEE)
  capacity?: number | null; // Capacité en nombre de bouteilles possibles
  manufacturing_date?: string | null; // Date de fabrication
  status: PaletteStatus;
  is_full?: boolean | null; // Whether the palette is full
  current_partner_id?: string | null; // UUID du partenaire (grossiste) actuel
  current_centre_remplisseur_id?: string | null; // UUID du centre remplisseur actuel
  current_centre_remplisseur?: CentreRemplisseur | null; // Centre remplisseur complet
  bon_enlevement_actuel_id?: string | null; // UUID du bon d'enlèvement actuel
  location_latitude?: number | null;
  location_longitude?: number | null;
  location_address?: string | null;
  notes?: string | null;
  created_by_id?: string; // UUID
  current_expedition_id?: string | null; // UUID
  created_at: string;
  updated_at: string;
}

export interface PaletteCreate {
  type: PaletteType;
  condition?: PaletteCondition; // Condition de la palette (NEUVE ou RECONDITIONNEE)
  reference_code?: string; // Code de référence personnalisé
  capacity?: number; // Capacité en nombre de bouteilles possibles
  manufacturing_date?: string; // Date de fabrication (format ISO date)
  rfid_tag_id?: string; // UUID du tag RFID (optionnel, peut être ajouté plus tard)
  current_partner_id?: string; // UUID du partenaire (grossiste) actuel
  location_latitude?: number;
  location_longitude?: number;
  location_address?: string;
  notes?: string;
}

export interface PaletteUpdate {
  type?: PaletteType;
  condition?: PaletteCondition; // Condition de la palette (NEUVE ou RECONDITIONNEE)
  status?: PaletteStatus;
  rfid_tag_id?: string; // Permet de réassigner un tag RFID
  location_latitude?: number;
  location_longitude?: number;
  location_address?: string;
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
