import React, { useEffect } from 'react';
import { View, Text, StyleSheet, FlatList, TouchableOpacity, RefreshControl } from 'react-native';
import { useAppDispatch, useAppSelector } from '../redux/hooks';
import { fetchExpeditions, setCurrentExpedition } from '../redux/slices/expeditionSlice';
import { useAuth } from '../hooks/useAuth';
import { Expedition } from '../types';

export const DashboardScreen: React.FC<{ navigation: any }> = ({ navigation }) => {
  const dispatch = useAppDispatch();
  const { user } = useAuth();
  const { expeditions, isLoading } = useAppSelector((state) => state.expeditions);
  const { unreadCount } = useAppSelector((state) => state.notifications);

  useEffect(() => {
    loadExpeditions();
  }, []);

  const loadExpeditions = async () => {
    if (user?.role === 'CHAUFFEUR' && user.id) {
      await dispatch(fetchExpeditions({ driverId: user.id }));
    } else {
      await dispatch(fetchExpeditions());
    }
  };

  const handleExpeditionPress = (expedition: Expedition) => {
    dispatch(setCurrentExpedition(expedition));
    navigation.navigate('ExpeditionDetail');
  };

  const renderExpeditionItem = ({ item }: { item: Expedition }) => (
    <TouchableOpacity
      style={styles.expeditionCard}
      onPress={() => handleExpeditionPress(item)}
    >
      <View style={styles.expeditionHeader}>
        <Text style={styles.expeditionRef}>{item.referenceNumber}</Text>
        <View style={[styles.statusBadge, { backgroundColor: getStatusColor(item.status) }]}>
          <Text style={styles.statusText}>{item.status}</Text>
        </View>
      </View>
      <Text style={styles.destination}>{item.destinationAddress}</Text>
      <Text style={styles.paletteCount}>{item.paletteCount} palette(s)</Text>
      {item.eta && (
        <Text style={styles.eta}>ETA: {new Date(item.eta).toLocaleString()}</Text>
      )}
    </TouchableOpacity>
  );

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Mes Expéditions</Text>
        <View style={styles.headerActions}>
          <TouchableOpacity
            style={styles.tagsListButton}
            onPress={() => navigation.navigate('RFIDTagsList')}
          >
            <Text style={styles.tagsListButtonText}>Tags</Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={styles.createTagButton}
            onPress={() => navigation.navigate('CreateRFIDTag')}
          >
            <Text style={styles.createTagButtonText}>+ Tag</Text>
          </TouchableOpacity>
          {unreadCount > 0 && (
            <TouchableOpacity
              style={styles.notificationBadge}
              onPress={() => navigation.navigate('Notifications')}
            >
              <Text style={styles.notificationText}>{unreadCount}</Text>
            </TouchableOpacity>
          )}
        </View>
      </View>

      <FlatList
        data={expeditions}
        renderItem={renderExpeditionItem}
        keyExtractor={(item) => item.id}
        contentContainerStyle={styles.list}
        refreshControl={
          <RefreshControl refreshing={isLoading} onRefresh={loadExpeditions} />
        }
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <Text style={styles.emptyText}>Aucune expédition</Text>
          </View>
        }
      />
    </View>
  );
};

const getStatusColor = (status: string): string => {
  const colors: Record<string, string> = {
    CREATION: '#FFA726',
    EN_ATTENTE: '#42A5F5',
    CREEE: '#66BB6A',
    EN_TRANSIT: '#29B6F6',
    ARRIVEE: '#AB47BC',
    LIVREE: '#66BB6A',
    PROBLEME: '#EF5350',
    ANNULEE: '#78909C',
  };
  return colors[status] || '#78909C';
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
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
  headerActions: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  tagsListButton: {
    backgroundColor: '#2196F3',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 6,
    marginRight: 8,
  },
  tagsListButtonText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600',
  },
  createTagButton: {
    backgroundColor: '#4CAF50',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 6,
    marginRight: 8,
  },
  createTagButtonText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600',
  },
  notificationBadge: {
    backgroundColor: '#EF5350',
    borderRadius: 12,
    minWidth: 24,
    height: 24,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 8,
  },
  notificationText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: 'bold',
  },
  list: {
    padding: 16,
  },
  expeditionCard: {
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
  expeditionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  expeditionRef: {
    fontSize: 18,
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
  destination: {
    fontSize: 14,
    color: '#666',
    marginBottom: 4,
  },
  paletteCount: {
    fontSize: 14,
    color: '#333',
    marginTop: 4,
  },
  eta: {
    fontSize: 12,
    color: '#999',
    marginTop: 4,
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
});

