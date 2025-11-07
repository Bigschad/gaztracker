import { useAuthStore } from '../store/authStore';
import { UserRole } from '../types';

export const useAuth = () => {
  const {
    user,
    isAuthenticated,
    isLoading,
    error,
    login,
    logout,
    refreshUser,
    clearError,
  } = useAuthStore();

  const hasRole = (role: UserRole): boolean => {
    return user?.role === role;
  };

  const hasAnyRole = (roles: UserRole[]): boolean => {
    return user ? roles.includes(user.role) : false;
  };

  const isAdmin = (): boolean => {
    return user?.role === UserRole.ADMIN;
  };

  const canManagePalettes = (): boolean => {
    return hasAnyRole([
      UserRole.ADMIN,
      UserRole.RESPONSABLE_LOGISTIQUE,
      UserRole.OPERATEUR_USINE,
    ]);
  };

  const canManageExpeditions = (): boolean => {
    return hasAnyRole([
      UserRole.ADMIN,
      UserRole.RESPONSABLE_LOGISTIQUE,
      UserRole.CHAUFFEUR,
    ]);
  };

  const canViewReports = (): boolean => {
    return hasAnyRole([UserRole.ADMIN, UserRole.RESPONSABLE_LOGISTIQUE]);
  };

  return {
    user,
    isAuthenticated,
    isLoading,
    error,
    login,
    logout,
    refreshUser,
    clearError,
    hasRole,
    hasAnyRole,
    isAdmin,
    canManagePalettes,
    canManageExpeditions,
    canViewReports,
  };
};
