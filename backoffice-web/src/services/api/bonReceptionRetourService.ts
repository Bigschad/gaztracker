import apiClient from './client';
import { API_ENDPOINTS } from '../../config/api';
import {
  BonReceptionRetour,
  BonReceptionRetourList,
  BonReceptionRetourDetail,
  BonReceptionRetourCreate,
  BonReceptionRetourUpdate,
  BonReceptionRetourStatus,
  BonReceptionRetourDepart,
  BonReceptionRetourArrivee,
  BonReceptionRetourControle,
  BonReceptionRetourValidation,
  BonReceptionRetourRefus,
} from '../../types';

interface BonReceptionRetourListParams {
  skip?: number;
  limit?: number;
  grossiste_id?: string;
  centre_id?: string;
  status?: BonReceptionRetourStatus;
  date_from?: string;
  date_to?: string;
  search?: string;
}

export const bonReceptionRetourService = {
  // List bons de réception retour
  list: async (params?: BonReceptionRetourListParams): Promise<BonReceptionRetourList[]> => {
    const response = await apiClient.get<BonReceptionRetourList[]>(
      API_ENDPOINTS.BONS_RECEPTION_RETOUR.BASE,
      { params }
    );
    return response.data;
  },

  // Get bon by ID
  getById: async (id: string): Promise<BonReceptionRetourDetail> => {
    const response = await apiClient.get<BonReceptionRetourDetail>(
      API_ENDPOINTS.BONS_RECEPTION_RETOUR.BY_ID(id)
    );
    return response.data;
  },

  // Create bon
  create: async (data: BonReceptionRetourCreate): Promise<BonReceptionRetour> => {
    const response = await apiClient.post<BonReceptionRetour>(
      API_ENDPOINTS.BONS_RECEPTION_RETOUR.BASE,
      data
    );
    return response.data;
  },

  // Update bon (only in CREATION status)
  update: async (id: string, data: BonReceptionRetourUpdate): Promise<BonReceptionRetour> => {
    const response = await apiClient.patch<BonReceptionRetour>(
      API_ENDPOINTS.BONS_RECEPTION_RETOUR.BY_ID(id),
      data
    );
    return response.data;
  },

  // Depart (CREATION → EN_ROUTE)
  depart: async (id: string, data: BonReceptionRetourDepart): Promise<BonReceptionRetour> => {
    const response = await apiClient.post<BonReceptionRetour>(
      API_ENDPOINTS.BONS_RECEPTION_RETOUR.DEPART(id),
      data
    );
    return response.data;
  },

  // Mark arrival (EN_ROUTE → ARRIVE)
  marquerArrivee: async (id: string, data: BonReceptionRetourArrivee): Promise<BonReceptionRetour> => {
    const response = await apiClient.post<BonReceptionRetour>(
      API_ENDPOINTS.BONS_RECEPTION_RETOUR.ARRIVEE(id),
      data
    );
    return response.data;
  },

  // Quality control (ARRIVE → EN_CONTROLE)
  controleQualite: async (id: string, data: BonReceptionRetourControle): Promise<BonReceptionRetour> => {
    const response = await apiClient.post<BonReceptionRetour>(
      API_ENDPOINTS.BONS_RECEPTION_RETOUR.CONTROLE(id),
      data
    );
    return response.data;
  },

  // Validate (EN_CONTROLE → VALIDE)
  valider: async (id: string, data: BonReceptionRetourValidation): Promise<BonReceptionRetour> => {
    const response = await apiClient.post<BonReceptionRetour>(
      API_ENDPOINTS.BONS_RECEPTION_RETOUR.VALIDER(id),
      data
    );
    return response.data;
  },

  // Refuse (EN_CONTROLE → REFUSE)
  refuser: async (id: string, data: BonReceptionRetourRefus): Promise<BonReceptionRetour> => {
    const response = await apiClient.post<BonReceptionRetour>(
      API_ENDPOINTS.BONS_RECEPTION_RETOUR.REFUSER(id),
      data
    );
    return response.data;
  },
};

