import { Platform } from 'react-native';

// Import conditionnel pour éviter les erreurs sur le web
let NfcManager: any;
let NfcTech: any;
let Ndef: any;

if (Platform.OS !== 'web') {
  try {
    const nfcModule = require('react-native-nfc-manager');
    NfcManager = nfcModule.default;
    NfcTech = nfcModule.NfcTech;
    Ndef = nfcModule.Ndef;
  } catch (e) {
    console.warn('NFC Manager not available');
  }
}

export interface RFIDScanResult {
  tagNumber: string;
  success: boolean;
  error?: string;
}

class RFIDService {
  private isScanning = false;

  async init(): Promise<boolean> {
    if (Platform.OS === 'web') {
      console.warn('NFC n\'est pas disponible sur le web');
      return false;
    }

    if (!NfcManager) {
      console.warn('NFC Manager not available');
      return false;
    }

    try {
      const supported = await NfcManager.isSupported();
      if (!supported) {
        throw new Error('NFC non supporté sur cet appareil');
      }

      await NfcManager.start();
      return true;
    } catch (error: any) {
      console.error('NFC init error:', error);
      return false;
    }
  }

  async scanTag(timeout: number = 10000): Promise<RFIDScanResult> {
    if (Platform.OS === 'web') {
      return {
        tagNumber: '',
        success: false,
        error: 'NFC n\'est pas disponible sur le web. Utilisez un appareil mobile.',
      };
    }

    if (!NfcManager || !NfcTech) {
      return {
        tagNumber: '',
        success: false,
        error: 'NFC Manager non disponible',
      };
    }

    if (this.isScanning) {
      return { tagNumber: '', success: false, error: 'Scan déjà en cours' };
    }

    this.isScanning = true;

    try {
      // Demander la technologie NFC
      await NfcManager.requestTechnology(NfcTech.Ndef);

      // Lire le tag
      const tag = await NfcManager.getTag();

      if (!tag) {
        throw new Error('Aucun tag détecté');
      }

      // Extraire l'UID du tag
      let tagNumber = '';

      if (Platform.OS === 'android' && tag.id) {
        // Android: utiliser l'ID du tag
        const idArray = Array.isArray(tag.id) ? tag.id : Array.from(tag.id);
        tagNumber = idArray
          .map((byte: number) => byte.toString(16).padStart(2, '0'))
          .join('')
          .toUpperCase();
      } else if (tag.ndefMessage && tag.ndefMessage.length > 0 && Ndef) {
        // iOS ou Android avec NDEF
        const ndefRecord = tag.ndefMessage[0];
        if (ndefRecord.payload) {
          tagNumber = Ndef.text.decodePayload(ndefRecord.payload);
        }
      }

      if (!tagNumber) {
        throw new Error('Impossible de lire le numéro du tag');
      }

      return { tagNumber, success: true };
    } catch (error: any) {
      console.error('RFID scan error:', error);
      return {
        tagNumber: '',
        success: false,
        error: error.message || 'Erreur lors du scan',
      };
    } finally {
      this.isScanning = false;
      try {
        await NfcManager.cancelTechnologyRequest();
      } catch (e) {
        // Ignorer les erreurs de cancel
      }
    }
  }

  async stopScan(): Promise<void> {
    if (Platform.OS === 'web' || !NfcManager) {
      this.isScanning = false;
      return;
    }

    try {
      await NfcManager.cancelTechnologyRequest();
      this.isScanning = false;
    } catch (error) {
      console.error('Error stopping scan:', error);
    }
  }

  async isEnabled(): Promise<boolean> {
    if (Platform.OS === 'web' || !NfcManager) {
      return false;
    }

    try {
      return await NfcManager.isEnabled();
    } catch (error) {
      return false;
    }
  }

  async enable(): Promise<void> {
    if (Platform.OS === 'web' || !NfcManager) {
      return;
    }

    try {
      if (Platform.OS === 'android') {
        await NfcManager.goToNfcSetting();
      }
    } catch (error) {
      console.error('Error enabling NFC:', error);
    }
  }
}

export const rfidService = new RFIDService();

