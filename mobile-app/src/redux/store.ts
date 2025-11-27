import { configureStore, combineReducers } from '@reduxjs/toolkit';
import { persistStore, persistReducer, FLUSH, REHYDRATE, PAUSE, PERSIST, PURGE, REGISTER } from 'redux-persist';
import AsyncStorage from '@react-native-async-storage/async-storage';
import authSlice from './slices/authSlice';
import expeditionSlice from './slices/expeditionSlice';
import paletteSlice from './slices/paletteSlice';
import notificationSlice from './slices/notificationSlice';
import offlineSlice from './slices/offlineSlice';
import settingsSlice from './slices/settingsSlice';

const rootReducer = combineReducers({
  auth: authSlice,
  expeditions: expeditionSlice,
  palettes: paletteSlice,
  notifications: notificationSlice,
  offline: offlineSlice,
  settings: settingsSlice,
});

const persistConfig = {
  key: 'root',
  storage: AsyncStorage,
  whitelist: ['auth', 'settings', 'offline'], // Seuls ces slices seront persistés
  blacklist: ['expeditions', 'palettes', 'notifications'], // Ces slices ne seront pas persistés
};

const persistedReducer = persistReducer(persistConfig, rootReducer);

console.log('[Store] Creating store...');
export const store = configureStore({
  reducer: persistedReducer,
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: [FLUSH, REHYDRATE, PAUSE, PERSIST, PURGE, REGISTER],
        // Increase warning threshold to reduce noise in development
        warnAfter: 128,
      },
      immutableCheck: {
        // Increase warning threshold to reduce noise in development
        warnAfter: 128,
      },
    }),
});

console.log('[Store] Store created, creating persistor...');
export const persistor = persistStore(store);
console.log('[Store] Persistor created');

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;

