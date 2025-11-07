import apiClient from './client';
import { API_ENDPOINTS } from '../../config/api';
import {
  User,
  UserCreate,
  UserUpdate,
  PaginatedResponse,
  PaginationParams,
} from '../../types';

export const userService = {
  // List users
  list: async (params?: PaginationParams): Promise<PaginatedResponse<User>> => {
    const response = await apiClient.get<PaginatedResponse<User>>(
      API_ENDPOINTS.USERS.BASE,
      { params }
    );
    return response.data;
  },

  // Get user by ID
  getById: async (id: number): Promise<User> => {
    const response = await apiClient.get<User>(API_ENDPOINTS.USERS.BY_ID(id));
    return response.data;
  },

  // Create user
  create: async (data: UserCreate): Promise<User> => {
    const response = await apiClient.post<User>(API_ENDPOINTS.USERS.BASE, data);
    return response.data;
  },

  // Update user
  update: async (id: number, data: UserUpdate): Promise<User> => {
    const response = await apiClient.put<User>(
      API_ENDPOINTS.USERS.BY_ID(id),
      data
    );
    return response.data;
  },

  // Delete user
  delete: async (id: number): Promise<void> => {
    await apiClient.delete(API_ENDPOINTS.USERS.BY_ID(id));
  },
};
