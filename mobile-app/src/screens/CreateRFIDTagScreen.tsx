import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TextInput,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
  ScrollView,
} from 'react-native';
import { useAppDispatch } from '../redux/hooks';
import { RFIDScanner } from '../components/RFIDScanner/RFIDScanner';
import { rfidApi, RFIDTagCreate } from '../api/rfidApi';
import { useAuth } from '../hooks/useAuth';

export const CreateRFIDTagScreen: React.FC<{ navigation: any }> = ({ navigation }) => {
  const dispatch = useAppDispatch();
  const { user } = useAuth();
  const [tagNumber, setTagNumber] = useState('');
  const [label, setLabel] = useState('');
  const [notes, setNotes] = useState('');
  const [isCreating, setIsCreating] = useState(false);
  const [isScanning, setIsScanning] = useState(false);

  const handleScanSuccess = (scannedTagNumber: string) => {
    setTagNumber(scannedTagNumber);
    setIsScanning(false);
  };

  const handleScanError = (error: string) => {
    Alert.alert('Erreur de scan', error);
    setIsScanning(false);
  };

  const handleCreateTag = async () => {
    if (!tagNumber.trim()) {
      Alert.alert('Erreur', 'Veuillez scanner un tag RFID ou entrer un numéro de tag');
      return;
    }

    setIsCreating(true);

    try {
      const tagData: RFIDTagCreate = {
        tagNumber: tagNumber.trim().toUpperCase(),
        label: label.trim() || undefined,
        notes: notes.trim() || undefined,
      };

      const createdTag = await rfidApi.create(tagData);

      Alert.alert(
        'Succès',
        `Tag RFID créé avec succès!\nNuméro: ${createdTag.tagNumber}`,
        [
          {
            text: 'Voir la liste',
            onPress: () => navigation.navigate('RFIDTagsList'),
          },
          {
            text: 'Créer un autre',
            style: 'cancel',
            onPress: () => {
              setTagNumber('');
              setLabel('');
              setNotes('');
            },
          },
          {
            text: 'Retour',
            onPress: () => navigation.goBack(),
          },
        ]
      );
    } catch (error: any) {
      const errorMessage =
        error.response?.data?.message ||
        error.response?.data?.detail ||
        error.message ||
        'Erreur lors de la création du tag';
      Alert.alert('Erreur', errorMessage);
    } finally {
      setIsCreating(false);
    }
  };

  const handleManualInput = () => {
    setIsScanning(false);
    // Le TextInput est déjà disponible, on peut simplement le focus
    // ou afficher un message pour guider l'utilisateur
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.contentContainer}>
      <View style={styles.header}>
        <Text style={styles.title}>Créer un tag RFID</Text>
        <Text style={styles.subtitle}>
          Scannez un tag RFID physique ou entrez le numéro manuellement
        </Text>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Numéro du tag RFID *</Text>
        <View style={styles.tagNumberContainer}>
          <TextInput
            style={styles.tagNumberInput}
            value={tagNumber}
            onChangeText={setTagNumber}
            placeholder="Numéro du tag (scanné ou saisi manuellement)"
            placeholderTextColor="#999"
            editable={!isScanning}
            autoCapitalize="characters"
          />
          <TouchableOpacity
            style={[styles.scanButton, isScanning && styles.scanButtonActive]}
            onPress={() => setIsScanning(!isScanning)}
            disabled={isCreating}
          >
            <Text style={styles.scanButtonText}>
              {isScanning ? 'Arrêter' : 'Scanner'}
            </Text>
          </TouchableOpacity>
        </View>
        <TouchableOpacity
          style={styles.manualButton}
          onPress={handleManualInput}
          disabled={isCreating || isScanning}
        >
          <Text style={styles.manualButtonText}>Saisir manuellement</Text>
        </TouchableOpacity>

        {isScanning && (
          <View style={styles.scannerContainer}>
            <RFIDScanner
              onScanSuccess={handleScanSuccess}
              onScanError={handleScanError}
              autoScan={true}
              disabled={isCreating}
            />
            <Text style={styles.scannerHint}>
              Approchez le tag RFID de votre appareil
            </Text>
          </View>
        )}
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Label (optionnel)</Text>
        <TextInput
          style={styles.input}
          value={label}
          onChangeText={setLabel}
          placeholder="Ex: Palette B6-001"
          placeholderTextColor="#999"
          editable={!isCreating}
        />
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Notes (optionnel)</Text>
        <TextInput
          style={[styles.input, styles.textArea]}
          value={notes}
          onChangeText={setNotes}
          placeholder="Notes supplémentaires sur ce tag..."
          placeholderTextColor="#999"
          multiline
          numberOfLines={4}
          editable={!isCreating}
        />
      </View>

      <TouchableOpacity
        style={[styles.createButton, (!tagNumber.trim() || isCreating) && styles.createButtonDisabled]}
        onPress={handleCreateTag}
        disabled={!tagNumber.trim() || isCreating}
      >
        {isCreating ? (
          <ActivityIndicator color="#fff" />
        ) : (
          <Text style={styles.createButtonText}>Créer le tag RFID</Text>
        )}
      </TouchableOpacity>

      <View style={styles.infoBox}>
        <Text style={styles.infoTitle}>ℹ️ Information</Text>
        <Text style={styles.infoText}>
          Une fois créé, ce tag RFID pourra être assigné à une palette depuis le backoffice.
          Vous pourrez ensuite scanner ce tag lors du chargement d'une expédition.
        </Text>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  contentContainer: {
    padding: 16,
  },
  header: {
    marginBottom: 24,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 14,
    color: '#666',
  },
  section: {
    backgroundColor: '#fff',
    borderRadius: 8,
    padding: 16,
    marginBottom: 16,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 12,
  },
  tagNumberContainer: {
    flexDirection: 'row',
    marginBottom: 8,
  },
  tagNumberInput: {
    flex: 1,
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
    backgroundColor: '#f9f9f9',
    marginRight: 8,
  },
  scanButton: {
    backgroundColor: '#007AFF',
    paddingHorizontal: 20,
    paddingVertical: 12,
    borderRadius: 8,
    justifyContent: 'center',
  },
  scanButtonActive: {
    backgroundColor: '#EF5350',
  },
  scanButtonText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600',
  },
  manualButton: {
    paddingVertical: 8,
  },
  manualButtonText: {
    color: '#007AFF',
    fontSize: 14,
    textAlign: 'center',
  },
  scannerContainer: {
    marginTop: 16,
    padding: 16,
    backgroundColor: '#f9f9f9',
    borderRadius: 8,
    borderWidth: 2,
    borderColor: '#007AFF',
    borderStyle: 'dashed',
  },
  scannerHint: {
    marginTop: 12,
    fontSize: 14,
    color: '#666',
    textAlign: 'center',
  },
  input: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
    backgroundColor: '#f9f9f9',
  },
  textArea: {
    minHeight: 100,
    textAlignVertical: 'top',
  },
  createButton: {
    backgroundColor: '#4CAF50',
    padding: 16,
    borderRadius: 8,
    alignItems: 'center',
    marginTop: 8,
    marginBottom: 16,
  },
  createButtonDisabled: {
    backgroundColor: '#ccc',
  },
  createButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  infoBox: {
    backgroundColor: '#E3F2FD',
    borderRadius: 8,
    padding: 16,
    borderLeftWidth: 4,
    borderLeftColor: '#2196F3',
  },
  infoTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1976D2',
    marginBottom: 8,
  },
  infoText: {
    fontSize: 14,
    color: '#424242',
    lineHeight: 20,
  },
});

