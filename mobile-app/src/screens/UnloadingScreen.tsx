import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
  ScrollView,
} from 'react-native';
import { useAppDispatch, useAppSelector } from '../redux/hooks';
import { getPaletteByRfid, addScannedPalette, clearScannedPalettes } from '../redux/slices/paletteSlice';
import { updateExpedition } from '../redux/slices/expeditionSlice';
import { RFIDScanner } from '../components/RFIDScanner/RFIDScanner';
import { Palette, Expedition } from '../types';
import { paletteApi } from '../api/paletteApi';

export const UnloadingScreen: React.FC<{ navigation: any; route: any }> = ({ navigation, route }) => {
  const dispatch = useAppDispatch();
  const { currentExpedition } = useAppSelector((state) => state.expeditions);
  const { scannedPalettes } = useAppSelector((state) => state.palettes);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isConfirming, setIsConfirming] = useState(false);

  const expedition = currentExpedition || route.params?.expedition;

  if (!expedition) {
    return (
      <View style={styles.container}>
        <Text style={styles.errorText}>Aucune expédition sélectionnée</Text>
        <TouchableOpacity style={styles.button} onPress={() => navigation.goBack()}>
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
          Alert.alert('Attention', 'Cette palette a déjà été déchargée');
          setIsProcessing(false);
          return;
        }

        // Vérifier que la palette est assignée à cette expédition
        if (palette.currentExpeditionId !== expedition.id) {
          Alert.alert('Erreur', 'Cette palette n\'appartient pas à cette expédition');
          setIsProcessing(false);
          return;
        }

        // Vérifier que la palette est en transit
        if (palette.status !== 'EN_ROUTE') {
          Alert.alert(
            'Attention',
            `Cette palette n'est pas en transit. Statut actuel: ${palette.status}`
          );
          setIsProcessing(false);
          return;
        }

        // Ajouter à la liste des palettes scannées
        dispatch(addScannedPalette(palette));
      } else {
        Alert.alert('Erreur', 'Palette non trouvée');
      }
    } catch (error: any) {
      Alert.alert('Erreur', error.message || 'Erreur lors du scan');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleConfirmUnloading = async () => {
    if (scannedPalettes.length === 0) {
      Alert.alert('Attention', 'Aucune palette scannée');
      return;
    }

    Alert.alert(
      'Confirmer le déchargement',
      `Confirmer le déchargement de ${scannedPalettes.length} palette(s) ?\n\nCette action marquera les palettes comme livrées.`,
      [
        { text: 'Annuler', style: 'cancel' },
        {
          text: 'Confirmer',
          style: 'destructive',
          onPress: async () => {
            setIsConfirming(true);
            try {
              // Scanner chaque palette pour enregistrer le déchargement
              const scanPromises = scannedPalettes.map((palette) =>
                paletteApi.scan({
                  rfidTag: palette.rfidTag?.tagNumber || '',
                  notes: 'Déchargement confirmé',
                })
              );

              await Promise.all(scanPromises);

              // Mettre à jour l'expédition si toutes les palettes sont déchargées
              const allPalettesUnloaded = expedition.paletteCount === scannedPalettes.length;
              
              if (allPalettesUnloaded) {
                // TODO: Mettre à jour le statut de l'expédition à LIVREE
                // await expeditionApi.updateStatus(expedition.id, 'LIVREE');
              }

              Alert.alert(
                'Succès',
                `${scannedPalettes.length} palette(s) déchargée(s) avec succès`,
                [
                  {
                    text: 'OK',
                    onPress: () => {
                      dispatch(clearScannedPalettes());
                      navigation.navigate('DeliveryNote', { expedition });
                    },
                  },
                ]
              );
            } catch (error: any) {
              Alert.alert('Erreur', error.message || 'Erreur lors de la confirmation');
            } finally {
              setIsConfirming(false);
            }
          },
        },
      ]
    );
  };

  const renderPaletteItem = ({ item }: { item: Palette }) => (
    <View style={styles.paletteCard}>
      <View style={styles.paletteHeader}>
        <Text style={styles.paletteSerial}>{item.serialNumber}</Text>
        <View style={[styles.statusBadge, { backgroundColor: '#4CAF50' }]}>
          <Text style={styles.statusText}>Déchargée</Text>
        </View>
      </View>
      <Text style={styles.paletteType}>Type: {item.type}</Text>
      <Text style={styles.paletteFill}>
        Remplissage: {item.currentFill}/{item.capacity}
      </Text>
      {item.rfidTag && (
        <Text style={styles.rfidTag}>RFID: {item.rfidTag.tagNumber}</Text>
      )}
    </View>
  );

  const getUnloadedCount = () => scannedPalettes.length;
  const getTotalCount = () => expedition.paletteCount || 0;
  const getRemainingCount = () => getTotalCount() - getUnloadedCount();

  return (
    <View style={styles.container}>
      <ScrollView style={styles.scrollView}>
        <View style={styles.header}>
          <Text style={styles.title}>Déchargement</Text>
          <Text style={styles.expeditionRef}>{expedition.referenceNumber}</Text>
        </View>

        <View style={styles.infoCard}>
          <View style={styles.infoRow}>
            <Text style={styles.infoLabel}>Destination:</Text>
            <Text style={styles.infoValue}>{expedition.destinationAddress}</Text>
          </View>
          {expedition.destinationContact && (
            <View style={styles.infoRow}>
              <Text style={styles.infoLabel}>Contact:</Text>
              <Text style={styles.infoValue}>{expedition.destinationContact}</Text>
            </View>
          )}
          <View style={styles.progressContainer}>
            <Text style={styles.progressText}>
              {getUnloadedCount()} / {getTotalCount()} palettes déchargées
            </Text>
            <View style={styles.progressBar}>
              <View
                style={[
                  styles.progressFill,
                  { width: `${(getUnloadedCount() / getTotalCount()) * 100}%` },
                ]}
              />
            </View>
          </View>
        </View>

        <View style={styles.scannerSection}>
          <Text style={styles.sectionTitle}>Scanner une palette</Text>
          <RFIDScanner
            onScanSuccess={handleScanSuccess}
            onScanError={(error) => Alert.alert('Erreur de scan', error)}
            disabled={isProcessing || isConfirming}
          />
          {isProcessing && (
            <View style={styles.processingContainer}>
              <ActivityIndicator size="large" color="#007AFF" />
              <Text style={styles.processingText}>Traitement...</Text>
            </View>
          )}
        </View>

        {scannedPalettes.length > 0 && (
          <View style={styles.listSection}>
            <Text style={styles.sectionTitle}>
              Palettes déchargées ({scannedPalettes.length})
            </Text>
            <FlatList
              data={scannedPalettes}
              renderItem={renderPaletteItem}
              keyExtractor={(item) => item.id}
              scrollEnabled={false}
            />
          </View>
        )}

        {getRemainingCount() > 0 && (
          <View style={styles.remainingCard}>
            <Text style={styles.remainingText}>
              {getRemainingCount()} palette(s) restante(s) à décharger
            </Text>
          </View>
        )}
      </ScrollView>

      <View style={styles.footer}>
        <TouchableOpacity
          style={[
            styles.confirmButton,
            (scannedPalettes.length === 0 || isConfirming) && styles.confirmButtonDisabled,
          ]}
          onPress={handleConfirmUnloading}
          disabled={scannedPalettes.length === 0 || isConfirming}
        >
          {isConfirming ? (
            <>
              <ActivityIndicator color="#fff" style={styles.buttonLoader} />
              <Text style={styles.confirmButtonText}>Confirmation...</Text>
            </>
          ) : (
            <Text style={styles.confirmButtonText}>
              Confirmer le déchargement ({scannedPalettes.length})
            </Text>
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
  scrollView: {
    flex: 1,
  },
  header: {
    backgroundColor: '#fff',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#ddd',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 4,
  },
  expeditionRef: {
    fontSize: 16,
    color: '#666',
  },
  infoCard: {
    backgroundColor: '#fff',
    padding: 16,
    marginTop: 8,
    marginBottom: 8,
  },
  infoRow: {
    flexDirection: 'row',
    marginBottom: 8,
  },
  infoLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: '#666',
    width: 100,
  },
  infoValue: {
    fontSize: 14,
    color: '#333',
    flex: 1,
  },
  progressContainer: {
    marginTop: 16,
  },
  progressText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
    marginBottom: 8,
  },
  progressBar: {
    height: 8,
    backgroundColor: '#e0e0e0',
    borderRadius: 4,
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
    backgroundColor: '#4CAF50',
  },
  scannerSection: {
    backgroundColor: '#fff',
    padding: 16,
    marginTop: 8,
    marginBottom: 8,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    marginBottom: 12,
    color: '#333',
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
    backgroundColor: '#fff',
    padding: 16,
    marginTop: 8,
    marginBottom: 8,
  },
  paletteCard: {
    backgroundColor: '#f9f9f9',
    padding: 12,
    borderRadius: 8,
    marginBottom: 8,
  },
  paletteHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  paletteSerial: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
  },
  statusBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 4,
  },
  statusText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: '600',
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
  rfidTag: {
    fontSize: 12,
    color: '#999',
    marginTop: 4,
    fontFamily: 'monospace',
  },
  remainingCard: {
    backgroundColor: '#FFF3E0',
    padding: 16,
    margin: 16,
    borderRadius: 8,
    borderLeftWidth: 4,
    borderLeftColor: '#FF9800',
  },
  remainingText: {
    fontSize: 14,
    color: '#E65100',
    fontWeight: '600',
  },
  footer: {
    backgroundColor: '#fff',
    padding: 16,
    borderTopWidth: 1,
    borderTopColor: '#ddd',
  },
  confirmButton: {
    backgroundColor: '#4CAF50',
    padding: 16,
    borderRadius: 8,
    alignItems: 'center',
    flexDirection: 'row',
    justifyContent: 'center',
  },
  confirmButtonDisabled: {
    backgroundColor: '#ccc',
  },
  confirmButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  buttonLoader: {
    marginRight: 8,
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

