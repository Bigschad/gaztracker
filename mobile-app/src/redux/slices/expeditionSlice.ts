import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { expeditionApi } from '../../api/expeditionApi';
import { Expedition } from '../../types';

interface ExpeditionState {
  expeditions: Expedition[];
  currentExpedition: Expedition | null;
  isLoading: boolean;
  error: string | null;
  lastSync: number | null;
}

const initialState: ExpeditionState = {
  expeditions: [],
  currentExpedition: null,
  isLoading: false,
  error: null,
  lastSync: null,
};

export const fetchExpeditions = createAsyncThunk(
  'expeditions/fetch',
  async (params: { status?: string; driverId?: string } | undefined, { rejectWithValue }) => {
    try {
      const response = await expeditionApi.list(params);
      return response.items;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Erreur lors du chargement');
    }
  }
);

export const fetchExpeditionById = createAsyncThunk(
  'expeditions/fetchById',
  async (id: string, { rejectWithValue }) => {
    try {
      const expedition = await expeditionApi.getById(id);
      return expedition;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Erreur lors du chargement');
    }
  }
);

export const assignPalettesToExpedition = createAsyncThunk(
  'expeditions/assignPalettes',
  async ({ expeditionId, paletteIds }: { expeditionId: string; paletteIds: string[] }, { rejectWithValue }) => {
    try {
      const expedition = await expeditionApi.assignPalettes(expeditionId, paletteIds);
      return expedition;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Erreur lors de l\'assignation');
    }
  }
);

const expeditionSlice = createSlice({
  name: 'expeditions',
  initialState,
  reducers: {
    setCurrentExpedition: (state, action: PayloadAction<Expedition | null>) => {
      state.currentExpedition = action.payload;
    },
    updateExpedition: (state, action: PayloadAction<Expedition>) => {
      const index = state.expeditions.findIndex((e) => e.id === action.payload.id);
      if (index !== -1) {
        state.expeditions[index] = action.payload;
      }
      if (state.currentExpedition?.id === action.payload.id) {
        state.currentExpedition = action.payload;
      }
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchExpeditions.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchExpeditions.fulfilled, (state, action) => {
        state.isLoading = false;
        state.expeditions = action.payload;
        state.lastSync = Date.now();
      })
      .addCase(fetchExpeditions.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      .addCase(fetchExpeditionById.fulfilled, (state, action) => {
        state.currentExpedition = action.payload;
        const index = state.expeditions.findIndex((e) => e.id === action.payload.id);
        if (index !== -1) {
          state.expeditions[index] = action.payload;
        } else {
          state.expeditions.push(action.payload);
        }
      })
      .addCase(assignPalettesToExpedition.fulfilled, (state, action) => {
        const index = state.expeditions.findIndex((e) => e.id === action.payload.id);
        if (index !== -1) {
          state.expeditions[index] = action.payload;
        }
        if (state.currentExpedition?.id === action.payload.id) {
          state.currentExpedition = action.payload;
        }
      });
  },
});

export const { setCurrentExpedition, updateExpedition, clearError } = expeditionSlice.actions;
export default expeditionSlice.reducer;

