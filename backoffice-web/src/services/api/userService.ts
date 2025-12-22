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
  getById: async (id: string): Promise<User> => {
    const response = await apiClient.get<User>(`/api/v1/users/${id}`);
    return response.data;
  },

  // Create user
  create: async (data: UserCreate): Promise<User> => {
    const response = await apiClient.post<User>(API_ENDPOINTS.USERS.BASE, data);
    return response.data;
  },

  // Update user
  update: async (id: string, data: UserUpdate): Promise<User> => {
    const response = await apiClient.put<User>(
      `/api/v1/users/${id}`,
      data
    );
    return response.data;
  },

  // Delete user
  delete: async (id: string): Promise<void> => {
    await apiClient.delete(`/api/v1/users/${id}`);
  },

  // Reset password (admin only)
  resetPassword: async (id: string, newPassword: string): Promise<void> => {
    await apiClient.put(
      API_ENDPOINTS.USERS.RESET_PASSWORD(id),
      { new_password: newPassword }
    );
  },
};
