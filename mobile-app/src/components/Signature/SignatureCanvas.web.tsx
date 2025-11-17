// Version web du composant SignatureCanvas utilisant un canvas HTML natif
import React, { useRef, useState, useEffect } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Alert, ActivityIndicator } from 'react-native';

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
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const isDrawingRef = useRef(false);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Configuration du canvas
    ctx.strokeStyle = '#000000';
    ctx.lineWidth = 2;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';

    const getCoordinates = (e: MouseEvent | TouchEvent) => {
      const rect = canvas.getBoundingClientRect();
      if (e instanceof MouseEvent) {
        return {
          x: e.clientX - rect.left,
          y: e.clientY - rect.top,
        };
      } else {
        const touch = e.touches[0] || e.changedTouches[0];
        return {
          x: touch.clientX - rect.left,
          y: touch.clientY - rect.top,
        };
      }
    };

    const startDrawing = (e: MouseEvent | TouchEvent) => {
      e.preventDefault();
      isDrawingRef.current = true;
      const { x, y } = getCoordinates(e);
      ctx.beginPath();
      ctx.moveTo(x, y);
    };

    const draw = (e: MouseEvent | TouchEvent) => {
      e.preventDefault();
      if (!isDrawingRef.current) return;
      const { x, y } = getCoordinates(e);
      ctx.lineTo(x, y);
      ctx.stroke();
    };

    const stopDrawing = () => {
      if (isDrawingRef.current) {
        isDrawingRef.current = false;
        const dataURL = canvas.toDataURL('image/png');
        setSignature(dataURL);
      }
    };

    // Événements souris
    canvas.addEventListener('mousedown', startDrawing);
    canvas.addEventListener('mousemove', draw);
    canvas.addEventListener('mouseup', stopDrawing);
    canvas.addEventListener('mouseleave', stopDrawing);

    // Événements tactiles
    canvas.addEventListener('touchstart', startDrawing);
    canvas.addEventListener('touchmove', draw);
    canvas.addEventListener('touchend', stopDrawing);

    return () => {
      canvas.removeEventListener('mousedown', startDrawing);
      canvas.removeEventListener('mousemove', draw);
      canvas.removeEventListener('mouseup', stopDrawing);
      canvas.removeEventListener('mouseleave', stopDrawing);
      canvas.removeEventListener('touchstart', startDrawing);
      canvas.removeEventListener('touchmove', draw);
      canvas.removeEventListener('touchend', stopDrawing);
    };
  }, []);

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
    const canvas = canvasRef.current;
    if (canvas) {
      const ctx = canvas.getContext('2d');
      if (ctx) {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        setSignature(null);
      }
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.description}>{description}</Text>

      <View style={styles.canvasContainer}>
        {/* @ts-ignore - canvas HTML natif pour le web */}
        <canvas
          ref={canvasRef}
          width={600}
          height={300}
          style={{
            width: '100%',
            height: '100%',
            border: '2px solid #007AFF',
            borderRadius: '4px',
            backgroundColor: '#fff',
            touchAction: 'none',
          } as any}
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
    padding: 20,
    backgroundColor: '#fff',
  },
  description: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 20,
    textAlign: 'center',
    color: '#333',
  },
  canvasContainer: {
    flex: 1,
    minHeight: 300,
    marginBottom: 20,
    borderRadius: 4,
    overflow: 'hidden',
  },
  buttonsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    gap: 10,
  },
  clearButton: {
    flex: 1,
    padding: 15,
    backgroundColor: '#f0f0f0',
    borderRadius: 8,
    alignItems: 'center',
  },
  clearButtonText: {
    color: '#333',
    fontSize: 16,
    fontWeight: '600',
  },
  cancelButton: {
    flex: 1,
    padding: 15,
    backgroundColor: '#ff6b6b',
    borderRadius: 8,
    alignItems: 'center',
  },
  cancelButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  saveButton: {
    flex: 1,
    padding: 15,
    backgroundColor: '#007AFF',
    borderRadius: 8,
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

