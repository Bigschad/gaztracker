import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ActivityIndicator, Alert, Platform } from 'react-native';
import { useRFID } from '../../hooks/useRFID';
import { RFIDScanResult } from '../../services/rfidService';

interface RFIDScannerProps {
  onScanSuccess: (tagNumber: string) => void;
  onScanError?: (error: string) => void;
  timeout?: number;
  autoScan?: boolean;
  disabled?: boolean;
}

export const RFIDScanner: React.FC<RFIDScannerProps> = ({
  onScanSuccess,
  onScanError,
  timeout,
  autoScan = false,
  disabled = false,
}) => {
  const { isInitialized, isScanning, error, scanTag, stopScan } = useRFID();
  const [lastResult, setLastResult] = useState<RFIDScanResult | null>(null);

  useEffect(() => {
    if (autoScan && isInitialized && !isScanning && !disabled) {
      handleScan();
    }
  }, [autoScan, isInitialized, disabled]);

  const handleScan = async () => {
    if (disabled || isScanning) return;

    const result = await scanTag(timeout);

    if (result) {
      setLastResult(result);

      if (result.success) {
        onScanSuccess(result.tagNumber);
      } else if (result.error && onScanError) {
        onScanError(result.error);
      }
    }
  };

  const handleStop = async () => {
    await stopScan();
  };

  if (Platform.OS === 'web') {
    return (
      <View style={styles.container}>
        <Text style={styles.errorText}>NFC non disponible sur le web</Text>
        <Text style={styles.hintText}>Utilisez un appareil mobile Android pour scanner les tags RFID</Text>
      </View>
    );
  }

  if (!isInitialized) {
    return (
      <View style={styles.container}>
        <Text style={styles.errorText}>NFC non disponible</Text>
        <Text style={styles.hintText}>Vérifiez que votre appareil supporte NFC et qu'il est activé</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {error && (
        <View style={styles.errorContainer}>
          <Text style={styles.errorText}>{error}</Text>
        </View>
      )}

      {lastResult?.success && (
        <View style={styles.successContainer}>
          <Text style={styles.successText}>Tag scanné: {lastResult.tagNumber}</Text>
        </View>
      )}

      <TouchableOpacity
        style={[styles.scanButton, (isScanning || disabled) && styles.scanButtonDisabled]}
        onPress={isScanning ? handleStop : handleScan}
        disabled={disabled}
      >
        {isScanning ? (
          <>
            <ActivityIndicator color="#fff" style={styles.loader} />
            <Text style={styles.scanButtonText}>Arrêter le scan</Text>
          </>
        ) : (
          <Text style={styles.scanButtonText}>Scanner un tag RFID</Text>
        )}
      </TouchableOpacity>

      {isScanning && (
        <Text style={styles.hintText}>Approchez le tag RFID de votre appareil...</Text>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    padding: 16,
    alignItems: 'center',
  },
  scanButton: {
    backgroundColor: '#007AFF',
    paddingHorizontal: 32,
    paddingVertical: 16,
    borderRadius: 8,
    flexDirection: 'row',
    alignItems: 'center',
    minWidth: 200,
    justifyContent: 'center',
  },
  scanButtonDisabled: {
    backgroundColor: '#ccc',
  },
  scanButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  loader: {
    marginRight: 8,
  },
  hintText: {
    marginTop: 12,
    fontSize: 14,
    color: '#666',
    textAlign: 'center',
  },
  errorContainer: {
    backgroundColor: '#FFE5E5',
    padding: 12,
    borderRadius: 8,
    marginBottom: 16,
    width: '100%',
  },
  errorText: {
    color: '#D32F2F',
    fontSize: 14,
    textAlign: 'center',
  },
  successContainer: {
    backgroundColor: '#E8F5E9',
    padding: 12,
    borderRadius: 8,
    marginBottom: 16,
    width: '100%',
  },
  successText: {
    color: '#2E7D32',
    fontSize: 14,
    textAlign: 'center',
    fontWeight: '600',
  },
});

