import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
} from 'react-native';
import { useAppSelector } from '../redux/hooks';
import { SignatureCanvasComponent } from '../components/Signature/SignatureCanvas';
import { pdfService } from '../services/pdfService';
import { Expedition } from '../types';
import * as Sharing from 'expo-sharing';
import * as FileSystem from 'expo-file-system';

export const DeliveryNoteScreen: React.FC<{ navigation: any; route: any }> = ({
  navigation,
  route,
}) => {
  const { currentExpedition } = useAppSelector((state) => state.expeditions);
  const { scannedPalettes } = useAppSelector((state) => state.palettes);
  const { signature: signatureSettings } = useAppSelector((state) => state.settings);

  const expedition = currentExpedition || route.params?.expedition;
  const [showSignature, setShowSignature] = useState(false);
  const [signatureData, setSignatureData] = useState<string | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [pdfUri, setPdfUri] = useState<string | null>(null);

  if (!expedition) {
    return (
      <View style={styles.container}>
        <Text style={styles.errorText}>Aucune expédition trouvée</Text>
        <TouchableOpacity style={styles.button} onPress={() => navigation.goBack()}>
          <Text style={styles.buttonText}>Retour</Text>
        </TouchableOpacity>
      </View>
    );
  }

  const palettes = scannedPalettes.length > 0 ? scannedPalettes : expedition.palettes || [];

  const handleSignatureSave = (data: string) => {
    setSignatureData(data);
    setShowSignature(false);
  };

  const handleGeneratePDF = async () => {
    // Vérifier la signature selon les paramètres
    if (signatureSettings.method === 'GRAPHIC' || signatureSettings.method === 'HYBRID') {
      if (!signatureData) {
        Alert.alert('Signature requise', 'Veuillez signer le bon de livraison');
        setShowSignature(true);
        return;
      }
    }

    setIsGenerating(true);

    try {
      const uri = await pdfService.generateDeliveryNote({
        expedition,
        palettes,
        signature: signatureData
          ? {
              type: signatureSettings.method,
              graphicData: signatureData,
              timestamp: Date.now(),
            }
          : undefined,
      });

      setPdfUri(uri);
      Alert.alert('Succès', 'Bon de livraison généré avec succès', [
        {
          text: 'Partager',
          onPress: async () => {
            if (await Sharing.isAvailableAsync()) {
              await Sharing.shareAsync(uri);
            } else {
              Alert.alert('Erreur', 'Le partage n\'est pas disponible sur cet appareil');
            }
          },
        },
        { text: 'OK' },
      ]);
    } catch (error: any) {
      Alert.alert('Erreur', error.message || 'Erreur lors de la génération du PDF');
    } finally {
      setIsGenerating(false);
    }
  };

  const totalPalettes = palettes.length;
  const totalBottles = palettes.reduce((sum: number, p: any) => sum + p.currentFill, 0);

  if (showSignature) {
    return (
      <SignatureCanvasComponent
        onSave={handleSignatureSave}
        onCancel={() => setShowSignature(false)}
        description="Veuillez signer le bon de livraison"
      />
    );
  }

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Bon de Livraison</Text>
        <Text style={styles.reference}>{expedition.referenceNumber}</Text>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Informations Expédition</Text>
        <View style={styles.infoRow}>
          <Text style={styles.infoLabel}>Date:</Text>
          <Text style={styles.infoValue}>
            {new Date().toLocaleDateString('fr-FR', {
              day: '2-digit',
              month: '2-digit',
              year: 'numeric',
            })}
          </Text>
        </View>
        {expedition.transporter && (
          <View style={styles.infoRow}>
            <Text style={styles.infoLabel}>Chauffeur:</Text>
            <Text style={styles.infoValue}>{expedition.transporter}</Text>
          </View>
        )}
        {expedition.vehicleInfo && (
          <View style={styles.infoRow}>
            <Text style={styles.infoLabel}>Véhicule:</Text>
            <Text style={styles.infoValue}>{expedition.vehicleInfo}</Text>
          </View>
        )}
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Destination</Text>
        <Text style={styles.destination}>{expedition.destinationAddress}</Text>
        {expedition.destinationContact && (
          <Text style={styles.contact}>Contact: {expedition.destinationContact}</Text>
        )}
        {expedition.destinationPhone && (
          <Text style={styles.contact}>Tél: {expedition.destinationPhone}</Text>
        )}
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Palettes Livrées</Text>
        {palettes.map((palette: any) => (
          <View key={palette.id} style={styles.paletteItem}>
            <Text style={styles.paletteSerial}>{palette.serialNumber}</Text>
            <Text style={styles.paletteDetails}>
              {palette.type} - {palette.currentFill}/{palette.capacity} bouteilles
            </Text>
          </View>
        ))}
      </View>

      <View style={styles.summary}>
        <View style={styles.summaryRow}>
          <Text style={styles.summaryLabel}>Total palettes:</Text>
          <Text style={styles.summaryValue}>{totalPalettes}</Text>
        </View>
        <View style={styles.summaryRow}>
          <Text style={styles.summaryLabel}>Total bouteilles:</Text>
          <Text style={styles.summaryValue}>{totalBottles}</Text>
        </View>
      </View>

      {signatureData && (
        <View style={styles.signatureSection}>
          <Text style={styles.sectionTitle}>Signature</Text>
          <View style={styles.signatureBox}>
            <Text style={styles.signatureText}>✓ Signé</Text>
            <Text style={styles.signatureDate}>
              {new Date().toLocaleString('fr-FR')}
            </Text>
          </View>
        </View>
      )}

      <View style={styles.actions}>
        {!signatureData && (signatureSettings.method === 'GRAPHIC' || signatureSettings.method === 'HYBRID') && (
          <TouchableOpacity
            style={styles.signatureButton}
            onPress={() => setShowSignature(true)}
          >
            <Text style={styles.signatureButtonText}>Signer</Text>
          </TouchableOpacity>
        )}

        <TouchableOpacity
          style={[styles.generateButton, isGenerating && styles.generateButtonDisabled]}
          onPress={handleGeneratePDF}
          disabled={isGenerating}
        >
          {isGenerating ? (
            <>
              <ActivityIndicator color="#fff" style={styles.buttonLoader} />
              <Text style={styles.generateButtonText}>Génération...</Text>
            </>
          ) : (
            <Text style={styles.generateButtonText}>Générer le PDF</Text>
          )}
        </TouchableOpacity>

        {pdfUri && (
          <TouchableOpacity
            style={styles.shareButton}
            onPress={async () => {
              if (await Sharing.isAvailableAsync()) {
                await Sharing.shareAsync(pdfUri);
              }
            }}
          >
            <Text style={styles.shareButtonText}>Partager le PDF</Text>
          </TouchableOpacity>
        )}
      </View>
    </ScrollView>
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
    borderBottomWidth: 2,
    borderBottomColor: '#007AFF',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#007AFF',
    marginBottom: 4,
  },
  reference: {
    fontSize: 16,
    color: '#666',
  },
  section: {
    backgroundColor: '#fff',
    padding: 16,
    marginTop: 8,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 12,
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
  destination: {
    fontSize: 14,
    color: '#333',
    marginBottom: 4,
  },
  contact: {
    fontSize: 14,
    color: '#666',
    marginTop: 4,
  },
  paletteItem: {
    padding: 12,
    backgroundColor: '#f9f9f9',
    borderRadius: 8,
    marginBottom: 8,
  },
  paletteSerial: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
  },
  paletteDetails: {
    fontSize: 14,
    color: '#666',
    marginTop: 4,
  },
  summary: {
    backgroundColor: '#f9f9f9',
    padding: 16,
    margin: 16,
    borderRadius: 8,
  },
  summaryRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 8,
  },
  summaryLabel: {
    fontSize: 16,
    color: '#333',
  },
  summaryValue: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
  },
  signatureSection: {
    backgroundColor: '#fff',
    padding: 16,
    marginTop: 8,
  },
  signatureBox: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    padding: 16,
    alignItems: 'center',
    minHeight: 100,
    justifyContent: 'center',
  },
  signatureText: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#4CAF50',
  },
  signatureDate: {
    fontSize: 12,
    color: '#666',
    marginTop: 8,
  },
  actions: {
    padding: 16,
  },
  signatureButton: {
    backgroundColor: '#007AFF',
    padding: 16,
    borderRadius: 8,
    alignItems: 'center',
    marginBottom: 12,
  },
  signatureButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  generateButton: {
    backgroundColor: '#4CAF50',
    padding: 16,
    borderRadius: 8,
    alignItems: 'center',
    flexDirection: 'row',
    justifyContent: 'center',
    marginBottom: 12,
  },
  generateButtonDisabled: {
    backgroundColor: '#ccc',
  },
  generateButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  shareButton: {
    backgroundColor: '#FF9800',
    padding: 16,
    borderRadius: 8,
    alignItems: 'center',
  },
  shareButtonText: {
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

