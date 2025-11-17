import { useState, useEffect, useCallback } from 'react';
import { Alert, Platform } from 'react-native';
import { rfidService, RFIDScanResult } from '../services/rfidService';
import { useAppSelector } from '../redux/hooks';

export const useRFID = () => {
  const [isInitialized, setIsInitialized] = useState(false);
  const [isScanning, setIsScanning] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const rfidSettings = useAppSelector((state) => state.settings.rfid);

  useEffect(() => {
    const init = async () => {
      const initialized = await rfidService.init();
      setIsInitialized(initialized);
      if (!initialized) {
        setError('NFC non supporté ou non activé');
      }
    };

    init();

    return () => {
      rfidService.stopScan();
    };
  }, []);

  const scanTag = useCallback(
    async (timeout?: number): Promise<RFIDScanResult | null> => {
      if (!isInitialized) {
        const enabled = await rfidService.isEnabled();
        if (!enabled) {
          Alert.alert(
            'NFC désactivé',
            'Veuillez activer le NFC dans les paramètres de votre appareil.',
            [
              { text: 'Annuler', style: 'cancel' },
              {
                text: 'Paramètres',
                onPress: () => rfidService.enable(),
              },
            ]
          );
          return null;
        }
      }

      setIsScanning(true);
      setError(null);

      try {
        const result = await rfidService.scanTag(timeout || rfidSettings.timeout || 10000);
        
        if (!result.success && result.error) {
          setError(result.error);
        }

        return result;
      } catch (err: any) {
        const errorMsg = err.message || 'Erreur lors du scan';
        setError(errorMsg);
        return { tagNumber: '', success: false, error: errorMsg };
      } finally {
        setIsScanning(false);
      }
    },
    [isInitialized, rfidSettings.timeout]
  );

  const stopScan = useCallback(async () => {
    await rfidService.stopScan();
    setIsScanning(false);
  }, []);

  return {
    isInitialized,
    isScanning,
    error,
    scanTag,
    stopScan,
  };
};

