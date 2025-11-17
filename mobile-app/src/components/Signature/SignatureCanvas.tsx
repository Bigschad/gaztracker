import React, { useRef, useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Alert, ActivityIndicator } from 'react-native';
import SignatureCanvas from 'react-native-signature-canvas';

interface SignatureCanvasProps {
  onSave: (signatureData: string) => void;
  onCancel?: () => void;
  description?: string;
}

export const SignatureCanvasComponent: React.FC<SignatureCanvasProps> = ({
  onSave,
  onCancel,
  description = 'Veuillez signer ci-dessous',
}) => {
  const [signature, setSignature] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const signatureRef = useRef<any>(null);

  const handleOK = async () => {
    if (!signature) {
      Alert.alert('Attention', 'Veuillez signer avant de continuer');
      return;
    }

    setIsSaving(true);
    try {
      // Extraire les données base64 de la signature
      const base64Data = signature.split(',')[1] || signature;
      onSave(base64Data);
    } catch (error: any) {
      Alert.alert('Erreur', 'Erreur lors de la sauvegarde de la signature');
    } finally {
      setIsSaving(false);
    }
  };

  const handleClear = () => {
    signatureRef.current?.clearSignature();
    setSignature(null);
  };

  const handleEnd = () => {
    signatureRef.current?.readSignature();
  };

  const handleData = (data: string) => {
    setSignature(data);
  };

  const style = `
    body,html {
      width: 100%;
      height: 100%;
      margin: 0;
      padding: 0;
    }
    .m-signature-pad {
      position: absolute;
      font-size: 10px;
      width: 100%;
      height: 100%;
      top: 0;
      left: 0;
      border: 2px solid #007AFF;
      background-color: #fff;
      border-radius: 4px;
    }
    .m-signature-pad--body {
      position: absolute;
      left: 20px;
      right: 20px;
      top: 20px;
      bottom: 60px;
      border: 1px solid #f4f4f4;
    }
    .m-signature-pad--body canvas {
      position: absolute;
      left: 0;
      top: 0;
      width: 100%;
      height: 100%;
      border-radius: 4px;
      box-shadow: 0 0 5px rgba(0, 0, 0, 0.02) inset;
    }
    .m-signature-pad--footer {
      position: absolute;
      left: 20px;
      right: 20px;
      bottom: 20px;
      height: 40px;
    }
    .m-signature-pad--footer
      .button {
      position: absolute;
      bottom: 0;
    }
    .m-signature-pad--footer
      .button.clear {
      left: 0;
    }
    .m-signature-pad--footer
      .button.save {
      right: 0;
    }
  `;

  return (
    <View style={styles.container}>
      <Text style={styles.description}>{description}</Text>

      <View style={styles.canvasContainer}>
        <SignatureCanvas
          ref={signatureRef}
          onOK={handleData}
          onEnd={handleEnd}
          descriptionText=""
          clearText="Effacer"
          confirmText="Confirmer"
          webStyle={style}
          autoClear={false}
          imageType="image/png"
        />
      </View>

      <View style={styles.buttonsContainer}>
        <TouchableOpacity style={styles.clearButton} onPress={handleClear}>
          <Text style={styles.clearButtonText}>Effacer</Text>
        </TouchableOpacity>

        {onCancel && (
          <TouchableOpacity style={styles.cancelButton} onPress={onCancel}>
            <Text style={styles.cancelButtonText}>Annuler</Text>
          </TouchableOpacity>
        )}

        <TouchableOpacity
          style={[styles.saveButton, (!signature || isSaving) && styles.saveButtonDisabled]}
          onPress={handleOK}
          disabled={!signature || isSaving}
        >
          {isSaving ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <Text style={styles.saveButtonText}>Confirmer</Text>
          )}
        </TouchableOpacity>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  description: {
    fontSize: 16,
    color: '#333',
    textAlign: 'center',
    padding: 16,
    backgroundColor: '#fff',
  },
  canvasContainer: {
    flex: 1,
    margin: 16,
    backgroundColor: '#fff',
    borderRadius: 8,
    overflow: 'hidden',
    minHeight: 300,
  },
  buttonsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    padding: 16,
    backgroundColor: '#fff',
    borderTopWidth: 1,
    borderTopColor: '#ddd',
  },
  clearButton: {
    paddingHorizontal: 20,
    paddingVertical: 12,
    borderRadius: 8,
    backgroundColor: '#f5f5f5',
  },
  clearButtonText: {
    color: '#333',
    fontSize: 16,
    fontWeight: '600',
  },
  cancelButton: {
    paddingHorizontal: 20,
    paddingVertical: 12,
    borderRadius: 8,
    backgroundColor: '#f5f5f5',
  },
  cancelButtonText: {
    color: '#666',
    fontSize: 16,
    fontWeight: '600',
  },
  saveButton: {
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 8,
    backgroundColor: '#4CAF50',
    flex: 1,
    marginLeft: 8,
    alignItems: 'center',
  },
  saveButtonDisabled: {
    backgroundColor: '#ccc',
  },
  saveButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
});

