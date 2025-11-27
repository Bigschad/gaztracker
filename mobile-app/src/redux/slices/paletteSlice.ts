import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { paletteApi } from '../../api/paletteApi';
import { Palette } from '../../types';

interface PaletteState {
  palettes: Palette[];
  scannedPalettes: Palette[]; // Pour le chargement/déchargement
  isLoading: boolean;
  error: string | null;
}

const initialState: PaletteState = {
  palettes: [],
  scannedPalettes: [],
  isLoading: false,
  error: null,
};

export const scanPalette = createAsyncThunk(
  'palettes/scan',
  async (data: { rfidTag: string; latitude?: number; longitude?: number }, { rejectWithValue }) => {
    try {
      const palette = await paletteApi.scan(data);
      return palette;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Erreur lors du scan');
    }
  }
);

export const getPaletteByRfid = createAsyncThunk(
  'palettes/getByRfid',
  async (tagNumber: string, { rejectWithValue }) => {
    try {
      const palette = await paletteApi.getByRfid(tagNumber);
      return palette;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Palette non trouvée');
    }
  }
);

const paletteSlice = createSlice({
  name: 'palettes',
  initialState,
  reducers: {
    addScannedPalette: (state, action: PayloadAction<Palette>) => {
      // Éviter les doublons
      if (!state.scannedPalettes.find((p) => p.id === action.payload.id)) {
        state.scannedPalettes.push(action.payload);
      }
    },
    removeScannedPalette: (state, action: PayloadAction<string>) => {
      state.scannedPalettes = state.scannedPalettes.filter((p) => p.id !== action.payload);
    },
    clearScannedPalettes: (state) => {
      state.scannedPalettes = [];
    },
    updatePalette: (state, action: PayloadAction<Palette>) => {
      const index = state.palettes.findIndex((p) => p.id === action.payload.id);
      if (index !== -1) {
        state.palettes[index] = action.payload;
      }
      const scannedIndex = state.scannedPalettes.findIndex((p) => p.id === action.payload.id);
      if (scannedIndex !== -1) {
        state.scannedPalettes[scannedIndex] = action.payload;
      }
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(scanPalette.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(scanPalette.fulfilled, (state, action) => {
        state.isLoading = false;
        const index = state.palettes.findIndex((p) => p.id === action.payload.id);
        if (index !== -1) {
          state.palettes[index] = action.payload;
        } else {
          state.palettes.push(action.payload);
        }
      })
      .addCase(scanPalette.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      .addCase(getPaletteByRfid.fulfilled, (state, action) => {
        const index = state.palettes.findIndex((p) => p.id === action.payload.id);
        if (index !== -1) {
          state.palettes[index] = action.payload;
        } else {
          state.palettes.push(action.payload);
        }
      });
  },
});

export const { addScannedPalette, removeScannedPalette, clearScannedPalettes, updatePalette, clearError } =
  paletteSlice.actions;
export default paletteSlice.reducer;

