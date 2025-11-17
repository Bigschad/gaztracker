import { useEffect, useCallback } from 'react';
import { Platform } from 'react-native';
import { useAppDispatch, useAppSelector } from '../redux/hooks';
import { setOnlineStatus, setSyncing, setLastSyncTime } from '../redux/slices/offlineSlice';
import { SYNC_INTERVAL } from '../config/constants';
import { syncService } from '../services/syncService';
import { database } from '../storage/database';

// Import conditionnel NetInfo
let NetInfo: any;
if (Platform.OS !== 'web') {
  try {
    NetInfo = require('@react-native-community/netinfo');
  } catch (e) {
    console.warn('NetInfo not available');
  }
}

export const useOfflineSync = () => {
  const dispatch = useAppDispatch();
  const { isOnline, isSyncing } = useAppSelector((state) => state.offline);

  const syncNow = useCallback(async () => {
    if (!isOnline || isSyncing) {
      return { success: false, message: 'Pas de connexion ou sync en cours' };
    }

    const queue = await database.getSyncQueue('PENDING');
    if (queue.length === 0) {
      return { success: true, message: 'Rien à synchroniser' };
    }

    dispatch(setSyncing(true));

    try {
      const result = await syncService.syncQueue();
      dispatch(setLastSyncTime(Date.now()));
      
      return {
        success: result.failed === 0,
        message: `Sync: ${result.success} réussie(s), ${result.failed} échouée(s)`,
      };
    } catch (error: any) {
      return { success: false, message: error.message || 'Erreur de sync' };
    } finally {
      dispatch(setSyncing(false));
    }
  }, [isOnline, isSyncing, dispatch]);

  // Initialiser la base de données
  useEffect(() => {
    database.init().catch((error) => {
      console.error('Error initializing database:', error);
    });
  }, []);

  // Surveiller la connexion réseau
  useEffect(() => {
    if (Platform.OS === 'web') {
      // Sur le web, toujours considéré comme en ligne
      dispatch(setOnlineStatus(true));
      return;
    }

    if (!NetInfo) {
      dispatch(setOnlineStatus(true));
      return;
    }

    const unsubscribe = NetInfo.addEventListener((state: any) => {
      const isConnected = state.isConnected ?? false;
      dispatch(setOnlineStatus(isConnected));
      
      // Si on vient de se reconnecter, lancer une sync
      if (isConnected && !isSyncing) {
        syncNow();
      }
    });

    return () => {
      if (unsubscribe) unsubscribe();
    };
  }, [dispatch, isSyncing, syncNow]);

  // Sync automatique périodique
  useEffect(() => {
    if (!isOnline || isSyncing) return;

    const interval = setInterval(async () => {
      const queue = await database.getSyncQueue('PENDING');
      if (queue.length > 0) {
        syncNow();
      }
    }, SYNC_INTERVAL);

    return () => clearInterval(interval);
  }, [isOnline, isSyncing, syncNow]);

  return {
    isOnline,
    isSyncing,
    syncNow,
  };
};

