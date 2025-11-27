// Stub pour le web - NFC n'est pas disponible
import { Platform } from 'react-native';
import { RFIDScanResult } from './rfidService';

class RFIDServiceWeb {
  async init(): Promise<boolean> {
    console.warn('NFC n\'est pas disponible sur le web');
    return false;
  }

  async scanTag(timeout: number = 10000): Promise<RFIDScanResult> {
    return {
      tagNumber: '',
      success: false,
      error: 'NFC n\'est pas disponible sur le web. Utilisez un appareil mobile.',
    };
  }

  async stopScan(): Promise<void> {
    // No-op
  }

  async isEnabled(): Promise<boolean> {
    return false;
  }

  async enable(): Promise<void> {
    // No-op
  }
}

export const rfidService = new RFIDServiceWeb();

