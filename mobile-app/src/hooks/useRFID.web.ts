// Version web de useRFID - NFC non disponible
import { useState } from 'react';
import { RFIDScanResult } from '../services/rfidService';

export const useRFID = () => {
  const [isInitialized] = useState(false);
  const [isScanning] = useState(false);
  const [error] = useState<string | null>('NFC non disponible sur le web');

  const scanTag = async (timeout?: number): Promise<RFIDScanResult | null> => {
    return {
      tagNumber: '',
      success: false,
      error: 'NFC n\'est pas disponible sur le web. Utilisez un appareil mobile pour scanner.',
    };
  };

  const stopScan = async () => {
    // No-op
  };

  return {
    isInitialized,
    isScanning,
    error,
    scanTag,
    stopScan,
  };
};

