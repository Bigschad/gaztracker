// User types matching backend schemas

export enum UserRole {
  ADMIN = 'ADMIN',
  RESPONSABLE_LOGISTIQUE = 'RESPONSABLE_LOGISTIQUE',
  OPERATEUR_USINE = 'OPERATEUR_USINE',
  CHAUFFEUR = 'CHAUFFEUR',
  GROSSISTE = 'GROSSISTE',
}

export interface User {
  id: number;
  username: string;
  email: string;
  full_name: string;
  role: UserRole;
  phone?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  last_login?: string;
}

export interface UserCreate {
  username: string;
  email: string;
  password: string;
  full_name: string;
  role: UserRole;
  phone?: string;
}

export interface UserUpdate {
  email?: string;
  full_name?: string;
  role?: UserRole;
  phone?: string;
  is_active?: boolean;
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
