import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { Platform } from 'react-native';
import { authApi } from '../../api/authApi';
import { User, AuthTokens, LoginCredentials } from '../../types';
import { STORAGE_KEYS } from '../../config/constants';

// Import conditionnel SecureStore
let SecureStore: any;
if (Platform.OS === 'web') {
  SecureStore = require('../../utils/secureStore.web').SecureStore;
} else {
  SecureStore = require('expo-secure-store');
}

interface AuthState {
  user: User | null;
  tokens: AuthTokens | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  sessionExpiry: number | null;
}

const initialState: AuthState = {
  user: null,
  tokens: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,
  sessionExpiry: null,
};

// Async Thunks
export const login = createAsyncThunk(
  'auth/login',
  async (credentials: LoginCredentials, { rejectWithValue }) => {
    try {
      const { user, tokens } = await authApi.login(credentials);
      
      console.log('[AuthSlice] Storing tokens:', {
        hasAccessToken: !!tokens.accessToken,
        hasRefreshToken: !!tokens.refreshToken,
        expiresIn: tokens.expiresIn,
      });
      
      // Stocker les tokens de manière sécurisée
      await SecureStore.setItemAsync(STORAGE_KEYS.AUTH_TOKENS, JSON.stringify(tokens));
      await SecureStore.setItemAsync(STORAGE_KEYS.USER, JSON.stringify(user));
      
      // Vérifier que les tokens ont bien été stockés
      const storedTokens = await SecureStore.getItemAsync(STORAGE_KEYS.AUTH_TOKENS);
      if (storedTokens) {
        const parsed = JSON.parse(storedTokens);
        console.log('[AuthSlice] Tokens stored successfully:', {
          hasAccessToken: !!parsed.accessToken,
          hasRefreshToken: !!parsed.refreshToken,
        });
      } else {
        console.error('[AuthSlice] Failed to store tokens!');
      }
      
      return { user, tokens };
    } catch (error: any) {
      console.error('[AuthSlice] Login error:', error);
      // Gérer différents types d'erreurs
      if (error.response) {
        // Erreur de réponse du serveur
        const message = error.response?.data?.message || error.response?.data?.detail || 'Erreur de connexion';
        return rejectWithValue(message);
      } else if (error.request) {
        // Requête envoyée mais pas de réponse (timeout, réseau, etc.)
        return rejectWithValue('Impossible de se connecter au serveur. Vérifiez votre connexion réseau.');
      } else {
        // Erreur lors de la configuration de la requête
        return rejectWithValue(error.message || 'Erreur de connexion');
      }
    }
  }
);

export const logout = createAsyncThunk('auth/logout', async (_, { rejectWithValue }) => {
  try {
    await authApi.logout();
  } catch (error) {
    // Même en cas d'erreur, on déconnecte localement
    console.error('Logout API error:', error);
  } finally {
    // Supprimer les tokens et user
    await SecureStore.deleteItemAsync(STORAGE_KEYS.AUTH_TOKENS);
    await SecureStore.deleteItemAsync(STORAGE_KEYS.USER);
  }
});

export const checkSession = createAsyncThunk('auth/checkSession', async (_, { rejectWithValue }) => {
  try {
    console.log('[AuthSlice] checkSession: Starting...');
    const tokensJson = await SecureStore.getItemAsync(STORAGE_KEYS.AUTH_TOKENS);
    const userJson = await SecureStore.getItemAsync(STORAGE_KEYS.USER);
    
    console.log('[AuthSlice] checkSession: Storage check', {
      hasTokens: !!tokensJson,
      hasUser: !!userJson,
    });
    
    if (!tokensJson || !userJson) {
      // Pas de session trouvée, c'est normal au premier démarrage
      console.log('[AuthSlice] checkSession: No session found (normal for first launch)');
      return rejectWithValue('No session found');
    }
    
    const tokens: AuthTokens = JSON.parse(tokensJson);
    const user: User = JSON.parse(userJson);
    
    // Vérifier si le token est expiré
    const now = Date.now();
    if (tokens.expiresIn && now > tokens.expiresIn) {
      // Token expiré, nettoyer et rejeter
      console.log('[AuthSlice] checkSession: Token expired');
      await SecureStore.deleteItemAsync(STORAGE_KEYS.AUTH_TOKENS);
      await SecureStore.deleteItemAsync(STORAGE_KEYS.USER);
      return rejectWithValue('Token expired');
    }
    
    console.log('[AuthSlice] checkSession: Session valid');
    return { user, tokens };
  } catch (error: any) {
    console.error('[AuthSlice] checkSession error:', error);
    // En cas d'erreur, nettoyer les données corrompues
    try {
      await SecureStore.deleteItemAsync(STORAGE_KEYS.AUTH_TOKENS);
      await SecureStore.deleteItemAsync(STORAGE_KEYS.USER);
    } catch (cleanupError) {
      console.error('[AuthSlice] Error cleaning up storage:', cleanupError);
    }
    return rejectWithValue(error.message || 'Session check failed');
  }
});

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    setUser: (state, action: PayloadAction<User>) => {
      state.user = action.payload;
      state.isAuthenticated = true;
    },
    setTokens: (state, action: PayloadAction<AuthTokens>) => {
      state.tokens = action.payload;
      state.sessionExpiry = action.payload.expiresIn || null;
    },
    clearError: (state) => {
      state.error = null;
    },
    resetAuth: (state) => {
      state.user = null;
      state.tokens = null;
      state.isAuthenticated = false;
      state.sessionExpiry = null;
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    // Login
    builder
      .addCase(login.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(login.fulfilled, (state, action) => {
        state.isLoading = false;
        state.user = action.payload.user;
        state.tokens = action.payload.tokens;
        state.isAuthenticated = true;
        state.sessionExpiry = action.payload.tokens.expiresIn || null;
        state.error = null;
      })
      .addCase(login.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
        state.isAuthenticated = false;
      });

    // Logout
    builder
      .addCase(logout.fulfilled, (state) => {
        state.user = null;
        state.tokens = null;
        state.isAuthenticated = false;
        state.sessionExpiry = null;
        state.error = null;
      });

    // Check Session
    builder
      .addCase(checkSession.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(checkSession.fulfilled, (state, action) => {
        state.isLoading = false;
        state.user = action.payload.user;
        state.tokens = action.payload.tokens;
        state.isAuthenticated = true;
        state.sessionExpiry = action.payload.tokens.expiresIn || null;
        state.error = null;
      })
      .addCase(checkSession.rejected, (state) => {
        state.isLoading = false;
        state.user = null;
        state.tokens = null;
        state.isAuthenticated = false;
        state.sessionExpiry = null;
        state.error = null; // Pas d'erreur si pas de session, c'est normal
      });
  },
});

export const { setUser, setTokens, clearError, resetAuth } = authSlice.actions;
export default authSlice.reducer;

