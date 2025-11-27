import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { SyncQueueItem } from '../../types';

interface OfflineState {
  isOnline: boolean;
  syncQueue: SyncQueueItem[];
  isSyncing: boolean;
  lastSyncTime: number | null;
}

const initialState: OfflineState = {
  isOnline: true,
  syncQueue: [],
  isSyncing: false,
  lastSyncTime: null,
};

const offlineSlice = createSlice({
  name: 'offline',
  initialState,
  reducers: {
    setOnlineStatus: (state, action: PayloadAction<boolean>) => {
      state.isOnline = action.payload;
    },
    addToSyncQueue: (state, action: PayloadAction<Omit<SyncQueueItem, 'id' | 'timestamp' | 'retryCount' | 'status'>>) => {
      const queueItem: SyncQueueItem = {
        id: `sync_${Date.now()}_${Math.random()}`,
        ...action.payload,
        timestamp: Date.now(),
        retryCount: 0,
        status: 'PENDING',
      };
      state.syncQueue.push(queueItem);
    },
    updateSyncQueueItem: (state, action: PayloadAction<{ id: string; updates: Partial<SyncQueueItem> }>) => {
      const index = state.syncQueue.findIndex((item) => item.id === action.payload.id);
      if (index !== -1) {
        state.syncQueue[index] = { ...state.syncQueue[index], ...action.payload.updates };
      }
    },
    removeFromSyncQueue: (state, action: PayloadAction<string>) => {
      state.syncQueue = state.syncQueue.filter((item) => item.id !== action.payload);
    },
    setSyncing: (state, action: PayloadAction<boolean>) => {
      state.isSyncing = action.payload;
    },
    setLastSyncTime: (state, action: PayloadAction<number>) => {
      state.lastSyncTime = action.payload;
    },
    clearSyncQueue: (state) => {
      state.syncQueue = [];
    },
  },
});

export const {
  setOnlineStatus,
  addToSyncQueue,
  updateSyncQueueItem,
  removeFromSyncQueue,
  setSyncing,
  setLastSyncTime,
  clearSyncQueue,
} = offlineSlice.actions;
export default offlineSlice.reducer;

