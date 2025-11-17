import axiosClient from './axiosClient';
import { API_ENDPOINTS } from '../config/apiConfig';
import { RFIDTag, PaginatedResponse } from '../types';

export interface RFIDTagCreate {
  tagNumber: string;
  label?: string;
  notes?: string;
}

export const rfidApi = {
  list: async (params?: {
    page?: number;
    pageSize?: number;
    status?: string;
    isActive?: boolean;
  }): Promise<PaginatedResponse<RFIDTag>> => {
    const response = await axiosClient.get(API_ENDPOINTS.RFID_TAGS.LIST, { params });
    return response.data;
  },

  create: async (data: RFIDTagCreate): Promise<RFIDTag> => {
    const response = await axiosClient.post(API_ENDPOINTS.RFID_TAGS.CREATE, data);
    return response.data.data;
  },

  getByNumber: async (tagNumber: string): Promise<RFIDTag> => {
    const response = await axiosClient.get(API_ENDPOINTS.RFID_TAGS.GET_BY_NUMBER(tagNumber));
    return response.data.data;
  },

  getById: async (id: string): Promise<RFIDTag> => {
    const response = await axiosClient.get(API_ENDPOINTS.RFID_TAGS.GET_BY_ID(id));
    return response.data.data;
  },
};

