import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
} from 'react-native';
import { useAppDispatch, useAppSelector } from '../redux/hooks';
import { getPaletteByRfid, addScannedPalette } from '../redux/slices/paletteSlice';
import { updateExpedition } from '../redux/slices/expeditionSlice';
import { RFIDScanner } from '../components/RFIDScanner/RFIDScanner';
import { Palette } from '../types';
import { expeditionApi } from '../api/expeditionApi';

export const LoadingScreen: React.FC<{ navigation: any }> = ({ navigation }) => {
  const dispatch = useAppDispatch();
  const { currentExpedition } = useAppSelector((state) => state.expeditions);
  const { scannedPalettes } = useAppSelector((state) => state.palettes);
  const [isProcessing, setIsProcessing] = useState(false);

  if (!currentExpedition) {
    return (
      <View style={styles.container}>
        <Text style={styles.errorText}>Aucune expédition sélectionnée</Text>
        <TouchableOpacity
          style={styles.button}
          onPress={() => navigation.goBack()}
        >
          <Text style={styles.buttonText}>Retour</Text>
        </TouchableOpacity>
      </View>
    );
  }

  const handleScanSuccess = async (tagNumber: string) => {
    setIsProcessing(true);

    try {
      // Récupérer la palette par RFID
      const result = await dispatch(getPaletteByRfid(tagNumber));

      if (result.type === 'palettes/getByRfid/fulfilled') {
        const palette = result.payload as Palette;

        // Vérifier que la palette n'est pas déjà scannée
        if (scannedPalettes.find((p) => p.id === palette.id)) {
          Alert.alert('Attention', 'Cette palette a déjà été scannée');
          setIsProcessing(false);
          return;
        }

        // Si la palette n'est pas assignée à cette expédition, l'assigner automatiquement
        if (palette.currentExpeditionId !== currentExpedition.id) {
          try {
            // Assigner la palette à l'expédition
            await expeditionApi.assignPalettes(currentExpedition.id, [palette.id]);
            
            // Mettre à jour la palette avec le nouvel expeditionId
            const updatedPalette = {
              ...palette,
              currentExpeditionId: currentExpedition.id,
            };
            
            // Ajouter à la liste des palettes scannées
            dispatch(addScannedPalette(updatedPalette));
            
            Alert.alert(
              'Succès',
              'Palette assignée à l\'expédition et ajoutée au chargement'
            );
          } catch (assignError: any) {
            Alert.alert(
              'Erreur',
              assignError.response?.data?.message || 
              'Impossible d\'assigner la palette à l\'expédition'
            );
            setIsProcessing(false);
            return;
          }
        } else {
          // La palette est déjà assignée, l'ajouter simplement à la liste
          dispatch(addScannedPalette(palette));
        }
      } else {
        Alert.alert('Erreur', 'Palette non trouvée. Assurez-vous que le tag RFID est bien assigné à une palette.');
      }
    } catch (error: any) {
      Alert.alert('Erreur', error.message || 'Erreur lors du scan');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleConfirmLoading = async () => {
    if (scannedPalettes.length === 0) {
      Alert.alert('Attention', 'Aucune palette scannée');
      return;
    }

    Alert.alert(
      'Confirmer le chargement',
      `Confirmer le chargement de ${scannedPalettes.length} palette(s) ?`,
      [
        { text: 'Annuler', style: 'cancel' },
        {
          text: 'Confirmer',
          onPress: async () => {
            try {
              const paletteIds = scannedPalettes.map((p) => p.id);
              const updatedExpedition = await expeditionApi.assignPalettes(
                currentExpedition.id,
                paletteIds
              );
              dispatch(updateExpedition(updatedExpedition));
              Alert.alert('Succès', 'Chargement confirmé');
              navigation.goBack();
            } catch (error: any) {
              Alert.alert('Erreur', error.message || 'Erreur lors de la confirmation');
            }
          },
        },
      ]
    );
  };

  const renderPaletteItem = ({ item }: { item: Palette }) => (
    <View style={styles.paletteCard}>
      <Text style={styles.paletteSerial}>{item.serialNumber}</Text>
      <Text style={styles.paletteType}>Type: {item.type}</Text>
      <Text style={styles.paletteFill}>Remplissage: {item.currentFill}/{item.capacity}</Text>
    </View>
  );

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Chargement - {currentExpedition.referenceNumber}</Text>
      </View>

      <View style={styles.scannerSection}>
        <RFIDScanner
          onScanSuccess={handleScanSuccess}
          onScanError={(error) => Alert.alert('Erreur de scan', error)}
          disabled={isProcessing}
        />
        {isProcessing && (
          <View style={styles.processingContainer}>
            <ActivityIndicator size="large" color="#007AFF" />
            <Text style={styles.processingText}>Traitement...</Text>
          </View>
        )}
      </View>

      <View style={styles.listSection}>
        <Text style={styles.listTitle}>
          Palettes scannées ({scannedPalettes.length})
        </Text>
        <FlatList
          data={scannedPalettes}
          renderItem={renderPaletteItem}
          keyExtractor={(item) => item.id}
          style={styles.list}
        />
      </View>

      <TouchableOpacity
        style={[styles.confirmButton, scannedPalettes.length === 0 && styles.confirmButtonDisabled]}
        onPress={handleConfirmLoading}
        disabled={scannedPalettes.length === 0}
      >
        <Text style={styles.confirmButtonText}>
          Confirmer le chargement ({scannedPalettes.length})
        </Text>
      </TouchableOpacity>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    backgroundColor: '#fff',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#ddd',
  },
  title: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
  },
  scannerSection: {
    backgroundColor: '#fff',
    padding: 16,
    marginTop: 8,
    marginBottom: 8,
  },
  processingContainer: {
    marginTop: 16,
    alignItems: 'center',
  },
  processingText: {
    marginTop: 8,
    fontSize: 14,
    color: '#666',
  },
  listSection: {
    flex: 1,
    backgroundColor: '#fff',
    padding: 16,
  },
  listTitle: {
    fontSize: 18,
    fontWeight: '600',
    marginBottom: 12,
    color: '#333',
  },
  list: {
    flex: 1,
  },
  paletteCard: {
    backgroundColor: '#f9f9f9',
    padding: 12,
    borderRadius: 8,
    marginBottom: 8,
  },
  paletteSerial: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
  },
  paletteType: {
    fontSize: 14,
    color: '#666',
    marginTop: 4,
  },
  paletteFill: {
    fontSize: 14,
    color: '#666',
    marginTop: 4,
  },
  confirmButton: {
    backgroundColor: '#007AFF',
    padding: 16,
    alignItems: 'center',
    margin: 16,
    borderRadius: 8,
  },
  confirmButtonDisabled: {
    backgroundColor: '#ccc',
  },
  confirmButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  errorText: {
    fontSize: 16,
    color: '#D32F2F',
    textAlign: 'center',
    marginTop: 32,
  },
  button: {
    backgroundColor: '#007AFF',
    padding: 16,
    borderRadius: 8,
    margin: 16,
    alignItems: 'center',
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
});

