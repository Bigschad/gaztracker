// Bon de Réception Retour types matching backend schemas

export enum BonReceptionRetourStatus {
  CREATION = 'CREATION',
  EN_ROUTE = 'EN_ROUTE',
  ARRIVE = 'ARRIVE',
  EN_CONTROLE = 'EN_CONTROLE',
  VALIDE = 'VALIDE',
  REFUSE = 'REFUSE',
}

export interface BonReceptionRetour {
  id: string; // UUID
  numero_bl: string;
  numero_reception: string;
  grossiste_id: string; // UUID
  depot_depart_id: string; // UUID
  centre_remplisseur_id: string; // UUID
  vehicule_immatriculation?: string | null;
  transporteur_nom?: string | null;
  transporteur_societe?: string | null;
  status: BonReceptionRetourStatus;
  date_creation: string;
  date_depart?: string | null;
  date_arrivee?: string | null;
  date_controle?: string | null;
  date_validation?: string | null;
  controleur_id?: string | null; // UUID
  magasinier_id?: string | null; // UUID
  observations?: string | null;
  manquants?: string | null;
  client_signature?: string | null;
  magasinier_signature?: string | null;
  controleur_signature?: string | null;
  palette_count: number;
  palette_acceptees: number;
  palette_refusees: number;
  created_at: string;
  updated_at: string;
}

export interface BonReceptionRetourList {
  id: string;
  numero_bl: string;
  numero_reception: string;
  status: BonReceptionRetourStatus;
  grossiste_id: string;
  centre_remplisseur_id: string;
  date_creation: string;
  date_arrivee?: string | null;
  palette_count: number;
}

export interface BonReceptionRetourDetail extends BonReceptionRetour {
  grossiste_name?: string | null;
  depot_depart_name?: string | null;
  centre_remplisseur_name?: string | null;
  controleur_name?: string | null;
  magasinier_name?: string | null;
  details_count?: number | null;
  taux_acceptation?: number | null;
}

export interface BonReceptionRetourCreate {
  numero_bl: string;
  numero_reception: string;
  grossiste_id: string;
  depot_depart_id: string;
  centre_remplisseur_id: string;
  vehicule_immatriculation?: string;
  transporteur_nom?: string;
  transporteur_societe?: string;
  observations?: string;
}

export interface BonReceptionRetourUpdate {
  vehicule_immatriculation?: string;
  transporteur_nom?: string;
  transporteur_societe?: string;
  observations?: string;
}

export interface BonReceptionRetourDepart {
  date_depart?: string;
  palette_ids: string[];
  observations?: string;
}

export interface BonReceptionRetourArrivee {
  magasinier_id: string;
  date_arrivee?: string;
  observations?: string;
  magasinier_signature?: string;
}

export interface BonReceptionRetourControle {
  controleur_id: string;
  date_controle?: string;
  details: Array<{
    type_detail: string;
    type_bouteille?: string;
    quantite_prevue: number;
    quantite_recue: number;
    quantite_acceptee: number;
    quantite_refusee: number;
    etat?: string;
  }>;
  manquants?: string;
  observations?: string;
  controleur_signature?: string;
}

export interface BonReceptionRetourValidation {
  date_validation?: string;
  client_signature?: string;
  observations?: string;
}

export interface BonReceptionRetourRefus {
  motif_refus: string;
  observations?: string;
}

