// Version web simplifiée de useOfflineSync
import { useEffect, useCallback } from 'react';
import { useAppDispatch, useAppSelector } from '../redux/hooks';
import { setOnlineStatus, setSyncing, setLastSyncTime } from '../redux/slices/offlineSlice';

export const useOfflineSync = () => {
  const dispatch = useAppDispatch();
  const { isOnline, isSyncing } = useAppSelector((state) => state.offline);

  const syncNow = useCallback(async () => {
    // Sur le web, toujours considéré comme en ligne
    return { success: true, message: 'Mode web - toujours en ligne' };
  }, []);

  // Sur le web, toujours considéré comme en ligne
  useEffect(() => {
    dispatch(setOnlineStatus(true));
  }, [dispatch]);

  return {
    isOnline: true,
    isSyncing: false,
    syncNow,
  };
};

