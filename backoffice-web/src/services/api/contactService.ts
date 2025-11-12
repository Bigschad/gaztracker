import apiClient from './client';
import { API_ENDPOINTS } from '../../config/api';
import {
  Contact,
  ContactCreate,
  ContactUpdate,
  PaginatedResponse,
  PaginationParams,
} from '../../types';

interface ContactListParams extends PaginationParams {
  partner_id?: string;
  is_primary?: boolean;
  search?: string;
}

export const contactService = {
  // List contacts
  list: async (params?: ContactListParams): Promise<PaginatedResponse<Contact>> => {
    const response = await apiClient.get<PaginatedResponse<Contact>>(
      API_ENDPOINTS.CONTACTS.BASE,
      { params }
    );
    return response.data;
  },

  // Get contact by ID
  getById: async (id: string): Promise<Contact> => {
    const response = await apiClient.get<Contact>(
      API_ENDPOINTS.CONTACTS.BY_ID(id)
    );
    return response.data;
  },

  // Create contact
  create: async (data: ContactCreate): Promise<Contact> => {
    const response = await apiClient.post<Contact>(
      API_ENDPOINTS.CONTACTS.BASE,
      data
    );
    return response.data;
  },

  // Update contact
  update: async (id: string, data: ContactUpdate): Promise<Contact> => {
    const response = await apiClient.put<Contact>(
      API_ENDPOINTS.CONTACTS.BY_ID(id),
      data
    );
    return response.data;
  },

  // Delete contact
  delete: async (id: string): Promise<void> => {
    await apiClient.delete(API_ENDPOINTS.CONTACTS.BY_ID(id));
  },
};

