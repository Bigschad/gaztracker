import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  RefreshControl,
  ActivityIndicator,
  Alert,
} from 'react-native';
import { vehicleApi } from '../api/vehicleApi';
import { Vehicle } from '../types';
import { useAuth } from '../hooks/useAuth';

export const VehiclesListScreen: React.FC<{ navigation: any }> = ({ navigation }) => {
  const { user } = useAuth();
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  const loadVehicles = useCallback(async (pageNum: number = 1, refresh: boolean = false) => {
    try {
      if (refresh) {
        setIsRefreshing(true);
      } else if (pageNum === 1) {
        setIsLoading(true);
      }

      const params: any = {
        page: pageNum,
        pageSize: 20,
      };

      // Filter by driver if user is a driver
      if (user?.role === 'CHAUFFEUR' && user.id) {
        params.driverId = user.id;
      }

      const response = await vehicleApi.list(params);
      
      if (pageNum === 1) {
        setVehicles(response.items || []);
      } else {
        setVehicles((prev) => [...prev, ...(response.items || [])]);
      }

      setHasMore((response.items?.length || 0) >= (params.pageSize || 20));
    } catch (error: any) {
      const errorMessage =
        error.response?.data?.message ||
        error.response?.data?.detail ||
        error.message ||
        'Erreur lors du chargement des véhicules';
      Alert.alert('Erreur', errorMessage);
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  }, [user]);

  useEffect(() => {
    loadVehicles(1, false);
  }, [loadVehicles]);

  const handleRefresh = () => {
    setPage(1);
    loadVehicles(1, true);
  };

  const handleLoadMore = () => {
    if (!isLoading && hasMore) {
      const nextPage = page + 1;
      setPage(nextPage);
      loadVehicles(nextPage, false);
    }
  };

  const handleDelete = (vehicle: Vehicle) => {
    Alert.alert(
      'Supprimer le véhicule',
      `Êtes-vous sûr de vouloir supprimer le véhicule "${vehicle.immatriculation}" ? Cette action est irréversible.`,
      [
        {
          text: 'Annuler',
          style: 'cancel',
        },
        {
          text: 'Supprimer',
          style: 'destructive',
          onPress: async () => {
            try {
              setDeletingId(vehicle.id);
              await vehicleApi.delete(vehicle.id);
              // Remove from local state
              setVehicles((prev) => prev.filter((v) => v.id !== vehicle.id));
              Alert.alert('Succès', 'Véhicule supprimé avec succès');
            } catch (error: any) {
              const errorMessage =
                error.response?.data?.message ||
                error.response?.data?.detail ||
                error.message ||
                'Erreur lors de la suppression du véhicule';
              Alert.alert('Erreur', errorMessage);
            } finally {
              setDeletingId(null);
            }
          },
        },
      ]
    );
  };

  const renderVehicleItem = ({ item }: { item: Vehicle }) => (
    <View style={styles.vehicleCard}>
      <View style={styles.vehicleHeader}>
        <View style={styles.vehicleInfoContainer}>
          <Text style={styles.immatriculation}>{item.immatriculation}</Text>
          {item.type && <Text style={styles.vehicleType}>{item.type}</Text>}
          {item.brand && item.model && (
            <Text style={styles.vehicleDetails}>
              {item.brand} {item.model}
            </Text>
          )}
        </View>
        <TouchableOpacity
          style={[styles.deleteButton, deletingId === item.id && styles.deleteButtonDisabled]}
          onPress={() => handleDelete(item)}
          disabled={deletingId === item.id}
        >
          {deletingId === item.id ? (
            <ActivityIndicator size="small" color="#EF5350" />
          ) : (
            <Trash2 size={20} color="#EF5350" />
          )}
        </TouchableOpacity>
      </View>
      
      <View style={styles.vehicleInfo}>
        <Text style={styles.vehicleInfoText}>
          Créé le: {new Date(item.createdAt).toLocaleDateString('fr-FR')}
        </Text>
        {!item.isActive && (
          <Text style={[styles.vehicleInfoText, styles.inactiveText]}>Inactif</Text>
        )}
      </View>
    </View>
  );

  if (isLoading && vehicles.length === 0) {
    return (
      <View style={styles.centerContainer}>
        <ActivityIndicator size="large" color="#007AFF" />
        <Text style={styles.loadingText}>Chargement des véhicules...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Mes véhicules</Text>
      </View>

      <FlatList
        data={vehicles}
        renderItem={renderVehicleItem}
        keyExtractor={(item) => item.id}
        contentContainerStyle={styles.list}
        refreshControl={<RefreshControl refreshing={isRefreshing} onRefresh={handleRefresh} />}
        onEndReached={handleLoadMore}
        onEndReachedThreshold={0.5}
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <Text style={styles.emptyText}>Aucun véhicule trouvé</Text>
          </View>
        }
        ListFooterComponent={
          hasMore && vehicles.length > 0 ? (
            <View style={styles.footer}>
              <ActivityIndicator size="small" color="#007AFF" />
            </View>
          ) : null
        }
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  centerContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f5f5f5',
  },
  loadingText: {
    marginTop: 16,
    fontSize: 16,
    color: '#666',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#ddd',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
  },
  list: {
    padding: 16,
  },
  vehicleCard: {
    backgroundColor: '#fff',
    borderRadius: 8,
    padding: 16,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  vehicleHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 12,
  },
  vehicleInfoContainer: {
    flex: 1,
    marginRight: 12,
  },
  immatriculation: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 4,
  },
  vehicleType: {
    fontSize: 14,
    color: '#666',
    marginBottom: 2,
  },
  vehicleDetails: {
    fontSize: 12,
    color: '#999',
  },
  deleteButton: {
    padding: 8,
    borderRadius: 6,
    backgroundColor: '#fff',
    borderWidth: 1,
    borderColor: '#EF5350',
    minWidth: 36,
    minHeight: 36,
    justifyContent: 'center',
    alignItems: 'center',
  },
  deleteButtonDisabled: {
    opacity: 0.5,
  },
  deleteButtonText: {
    fontSize: 18,
  },
  vehicleInfo: {
    borderTopWidth: 1,
    borderTopColor: '#f0f0f0',
    paddingTop: 12,
  },
  vehicleInfoText: {
    fontSize: 12,
    color: '#666',
    marginBottom: 4,
  },
  inactiveText: {
    color: '#EF5350',
    fontWeight: '600',
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 64,
  },
  emptyText: {
    fontSize: 16,
    color: '#999',
  },
  footer: {
    paddingVertical: 16,
    alignItems: 'center',
  },
});
