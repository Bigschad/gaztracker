// User types matching backend schemas

export enum UserRole {
  ADMIN = 'ADMIN',
  RESPONSABLE_LOGISTIQUE = 'RESPONSABLE_LOGISTIQUE',
  OPERATEUR_USINE = 'OPERATEUR_USINE',
  CHAUFFEUR = 'CHAUFFEUR',
  GROSSISTE = 'GROSSISTE',
}

export interface User {
  id: string; // UUID
  email: string;
  first_name: string;
  last_name: string;
  phone_number?: string;
  company_name?: string;
  role: UserRole;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
  updated_at: string;
}

export interface UserCreate {
  email: string;
  first_name: string;
  last_name: string;
  phone_number?: string;
  company_name?: string;
  role: UserRole;
  password: string;
}

export interface UserUpdate {
  email?: string;
  first_name?: string;
  last_name?: string;
  phone_number?: string;
  company_name?: string;
  role?: UserRole;
  is_active?: boolean;
  is_verified?: boolean;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}

export interface TokenRefreshRequest {
  refresh_token: string;
}

export interface TokenRefreshResponse {
  access_token: string;
  token_type: string;
}
