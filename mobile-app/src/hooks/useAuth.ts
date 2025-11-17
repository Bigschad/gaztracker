import { useEffect, useCallback, useState, useRef } from 'react';
import { Platform } from 'react-native';
import { useAppDispatch, useAppSelector } from '../redux/hooks';
import { login, logout, checkSession, resetAuth } from '../redux/slices/authSlice';
import { SESSION_TIMEOUT } from '../config/constants';
import { STORAGE_KEYS } from '../config/constants';

// Import conditionnel SecureStore
let SecureStore: any;
if (Platform.OS === 'web') {
  SecureStore = require('../utils/secureStore.web').SecureStore;
} else {
  SecureStore = require('expo-secure-store');
}

// Variable globale pour s'assurer que checkSession n'est appelé qu'une seule fois
// même si plusieurs instances de useAuth sont créées
let hasCheckedSession = false;

export const useAuth = () => {
  const dispatch = useAppDispatch();
  const { user, isAuthenticated, isLoading, error, sessionExpiry } = useAppSelector((state) => state.auth);
  const [hasTimedOut, setHasTimedOut] = useState(false);
  const hasCheckedRef = useRef(false);

  // Définir handleLogout avant les useEffect qui l'utilisent
  const handleLogout = useCallback(async () => {
    await dispatch(logout());
    await SecureStore.deleteItemAsync(STORAGE_KEYS.AUTH_TOKENS);
    await SecureStore.deleteItemAsync(STORAGE_KEYS.USER);
    dispatch(resetAuth());
  }, [dispatch]);

  const handleLogin = useCallback(
    async (email: string, password: string) => {
      const result = await dispatch(login({ email, password }));
      return result;
    },
    [dispatch]
  );

  // Vérifier la session au démarrage (une seule fois, même si le composant se remonte)
  useEffect(() => {
    // Vérifier si checkSession a déjà été appelé (globalement ou dans cette instance)
    if (hasCheckedSession || hasCheckedRef.current) {
      console.log('[useAuth] checkSession already called, skipping');
      return;
    }

    console.log('[useAuth] Checking session...');
    hasCheckedSession = true;
    hasCheckedRef.current = true;
    
    let isMounted = true;
    let timeoutId: NodeJS.Timeout | null = null;
    
    const checkSessionPromise = dispatch(checkSession());
    
    // Timeout de sécurité : si checkSession prend plus de 3 secondes, on force l'arrêt
    timeoutId = setTimeout(() => {
      if (isMounted) {
        console.warn('[useAuth] checkSession timeout after 3s, forcing completion');
        setHasTimedOut(true);
      }
    }, 3000);
    
    checkSessionPromise
      .then((result) => {
        if (isMounted) {
          console.log('[useAuth] checkSession completed:', result.type);
          if (timeoutId) clearTimeout(timeoutId);
        }
      })
      .catch((error) => {
        if (isMounted) {
          console.error('[useAuth] checkSession error:', error);
          if (timeoutId) clearTimeout(timeoutId);
        }
      });
    
    return () => {
      isMounted = false;
      if (timeoutId) clearTimeout(timeoutId);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // Exécuter une seule fois au montage

  // Vérifier l'expiration de la session
  useEffect(() => {
    if (!sessionExpiry || !isAuthenticated) return;

    const checkExpiry = () => {
      const now = Date.now();
      if (now >= sessionExpiry) {
        handleLogout();
      }
    };

    const interval = setInterval(checkExpiry, 60000); // Vérifier toutes les minutes
    checkExpiry(); // Vérifier immédiatement

    return () => clearInterval(interval);
  }, [sessionExpiry, isAuthenticated, handleLogout]);

  const hasPermission = useCallback(
    (permission: string): boolean => {
      if (!user) return false;
      if (user.role === 'ADMIN') return true;

      // TODO: Implémenter la logique de permissions selon les rôles
      // Pour l'instant, retourner true pour les tests
      return true;
    },
    [user]
  );

  // Si on a timeout, on considère qu'on n'est pas en chargement
  const effectiveIsLoading = hasTimedOut ? false : isLoading;

  return {
    user,
    isAuthenticated,
    isLoading: effectiveIsLoading,
    error,
    login: handleLogin,
    logout: handleLogout,
    hasPermission,
  };
};

