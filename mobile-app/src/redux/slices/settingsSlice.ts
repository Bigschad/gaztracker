import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface SettingsState {
  rfid: {
    readerBrand?: string;
    sensitivity?: number;
    timeout?: number;
    scanMode?: 'CONTINUOUS' | 'SINGLE';
  };
  notifications: {
    enabled: boolean;
    sound: boolean;
    vibration: boolean;
    quietHours: { start: string; end: string } | null;
  };
  signature: {
    method: 'GRAPHIC' | 'OTP' | 'HYBRID';
    otpChannel: 'EMAIL' | 'SMS';
    securityLevel: 'LOW' | 'MEDIUM' | 'HIGH';
  };
  theme: 'light' | 'dark' | 'auto';
}

const initialState: SettingsState = {
  rfid: {
    timeout: 10000,
    scanMode: 'SINGLE',
  },
  notifications: {
    enabled: true,
    sound: true,
    vibration: true,
    quietHours: null,
  },
  signature: {
    method: 'HYBRID',
    otpChannel: 'SMS',
    securityLevel: 'HIGH',
  },
  theme: 'light',
};

const settingsSlice = createSlice({
  name: 'settings',
  initialState,
  reducers: {
    updateRfidSettings: (state, action: PayloadAction<Partial<SettingsState['rfid']>>) => {
      state.rfid = { ...state.rfid, ...action.payload };
    },
    updateNotificationSettings: (state, action: PayloadAction<Partial<SettingsState['notifications']>>) => {
      state.notifications = { ...state.notifications, ...action.payload };
    },
    updateSignatureSettings: (state, action: PayloadAction<Partial<SettingsState['signature']>>) => {
      state.signature = { ...state.signature, ...action.payload };
    },
    setTheme: (state, action: PayloadAction<SettingsState['theme']>) => {
      state.theme = action.payload;
    },
    resetSettings: (state) => {
      return initialState;
    },
  },
});

export const { updateRfidSettings, updateNotificationSettings, updateSignatureSettings, setTheme, resetSettings } =
  settingsSlice.actions;
export default settingsSlice.reducer;

