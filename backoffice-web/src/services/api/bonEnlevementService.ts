import apiClient from './client';
import { API_ENDPOINTS } from '../../config/api';
import {
  BonEnlevement,
  BonEnlevementList,
  BonEnlevementDetail,
  BonEnlevementCreate,
  BonEnlevementUpdate,
  BonEnlevementStatus,
  BonEnlevementValidation,
  BonEnlevementChargement,
  BonEnlevementDepart,
  BonEnlevementReception,
} from '../../types';

interface BonEnlevementListParams {
  skip?: number;
  limit?: number;
  centre_id?: string;
  grossiste_id?: string;
  status?: BonEnlevementStatus;
  date_from?: string;
  date_to?: string;
  search?: string;
}

export const bonEnlevementService = {
  // List bons d'enlèvement
  list: async (params?: BonEnlevementListParams): Promise<BonEnlevementList[]> => {
    const response = await apiClient.get<BonEnlevementList[]>(
      API_ENDPOINTS.BONS_ENLEVEMENT.BASE,
      { params }
    );
    return response.data;
  },

  // Get bon by ID
  getById: async (id: string): Promise<BonEnlevementDetail> => {
    const response = await apiClient.get<BonEnlevementDetail>(
      API_ENDPOINTS.BONS_ENLEVEMENT.BY_ID(id)
    );
    return response.data;
  },

  // Create bon
  create: async (data: BonEnlevementCreate): Promise<BonEnlevement> => {
    const response = await apiClient.post<BonEnlevement>(
      API_ENDPOINTS.BONS_ENLEVEMENT.BASE,
      data
    );
    return response.data;
  },

  // Update bon (only in CREATION status)
  update: async (id: string, data: BonEnlevementUpdate): Promise<BonEnlevement> => {
    const response = await apiClient.patch<BonEnlevement>(
      API_ENDPOINTS.BONS_ENLEVEMENT.BY_ID(id),
      data
    );
    return response.data;
  },

  // Validate bon (CREATION → VALIDE)
  valider: async (id: string, data: BonEnlevementValidation): Promise<BonEnlevement> => {
    const response = await apiClient.post<BonEnlevement>(
      API_ENDPOINTS.BONS_ENLEVEMENT.VALIDER(id),
      data
    );
    return response.data;
  },

  // Start loading (VALIDE → EN_CHARGEMENT)
  startChargement: async (id: string, data: BonEnlevementChargement): Promise<BonEnlevement> => {
    const response = await apiClient.post<BonEnlevement>(
      API_ENDPOINTS.BONS_ENLEVEMENT.START_CHARGEMENT(id),
      data
    );
    return response.data;
  },

  // Depart (EN_CHARGEMENT → EN_ROUTE)
  depart: async (id: string, data: BonEnlevementDepart): Promise<BonEnlevement> => {
    const response = await apiClient.post<BonEnlevement>(
      API_ENDPOINTS.BONS_ENLEVEMENT.DEPART(id),
      data
    );
    return response.data;
  },

  // Start delivery (EN_ROUTE → EN_LIVRAISON)
  startLivraison: async (id: string): Promise<BonEnlevement> => {
    const response = await apiClient.post<BonEnlevement>(
      API_ENDPOINTS.BONS_ENLEVEMENT.START_LIVRAISON(id)
    );
    return response.data;
  },

  // Complete (EN_LIVRAISON → TERMINE)
  terminer: async (id: string, data: BonEnlevementReception): Promise<BonEnlevement> => {
    const response = await apiClient.post<BonEnlevement>(
      API_ENDPOINTS.BONS_ENLEVEMENT.TERMINER(id),
      data
    );
    return response.data;
  },

  // Cancel bon
  annuler: async (id: string, reason: string): Promise<BonEnlevement> => {
    const response = await apiClient.post<BonEnlevement>(
      API_ENDPOINTS.BONS_ENLEVEMENT.ANNULER(id),
      null,
      { params: { reason } }
    );
    return response.data;
  },
};

