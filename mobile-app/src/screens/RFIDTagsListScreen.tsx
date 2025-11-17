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
import { rfidApi } from '../api/rfidApi';
import { RFIDTag } from '../types';

export const RFIDTagsListScreen: React.FC<{ navigation: any }> = ({ navigation }) => {
  const [tags, setTags] = useState<RFIDTag[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [filter, setFilter] = useState<'ALL' | 'NOT_ASSIGNED' | 'ASSIGNED'>('ALL');

  const loadTags = useCallback(async (pageNum: number = 1, refresh: boolean = false) => {
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

      if (filter !== 'ALL') {
        params.status = filter;
      }

      const response = await rfidApi.list(params);
      
      if (pageNum === 1) {
        setTags(response.items || []);
      } else {
        setTags((prev) => [...prev, ...(response.items || [])]);
      }

      setHasMore((response.items?.length || 0) >= (params.pageSize || 20));
    } catch (error: any) {
      const errorMessage =
        error.response?.data?.message ||
        error.response?.data?.detail ||
        error.message ||
        'Erreur lors du chargement des tags';
      Alert.alert('Erreur', errorMessage);
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  }, [filter]);

  useEffect(() => {
    loadTags(1, false);
  }, [filter]);

  const handleRefresh = () => {
    setPage(1);
    loadTags(1, true);
  };

  const handleLoadMore = () => {
    if (!isLoading && hasMore) {
      const nextPage = page + 1;
      setPage(nextPage);
      loadTags(nextPage, false);
    }
  };

  const getStatusColor = (status: string): string => {
    const colors: Record<string, string> = {
      NOT_ASSIGNED: '#FFA726',
      ASSIGNED: '#66BB6A',
      LOST: '#EF5350',
      DAMAGED: '#78909C',
    };
    return colors[status] || '#78909C';
  };

  const getStatusLabel = (status: string): string => {
    const labels: Record<string, string> = {
      NOT_ASSIGNED: 'Non assigné',
      ASSIGNED: 'Assigné',
      LOST: 'Perdu',
      DAMAGED: 'Endommagé',
    };
    return labels[status] || status;
  };

  const renderTagItem = ({ item }: { item: RFIDTag }) => (
    <TouchableOpacity style={styles.tagCard}>
      <View style={styles.tagHeader}>
        <View style={styles.tagNumberContainer}>
          <Text style={styles.tagNumber}>{item.tagNumber}</Text>
          {item.label && <Text style={styles.tagLabel}>{item.label}</Text>}
        </View>
        <View style={[styles.statusBadge, { backgroundColor: getStatusColor(item.status) }]}>
          <Text style={styles.statusText}>{getStatusLabel(item.status)}</Text>
        </View>
      </View>
      
      <View style={styles.tagInfo}>
        <Text style={styles.tagInfoText}>
          Créé le: {new Date(item.createdAt).toLocaleDateString('fr-FR')}
        </Text>
        {item.assignedAt && (
          <Text style={styles.tagInfoText}>
            Assigné le: {new Date(item.assignedAt).toLocaleDateString('fr-FR')}
          </Text>
        )}
        {!item.isActive && (
          <Text style={[styles.tagInfoText, styles.inactiveText]}>Inactif</Text>
        )}
      </View>
    </TouchableOpacity>
  );

  const renderFilterButtons = () => (
    <View style={styles.filterContainer}>
      <TouchableOpacity
        style={[styles.filterButton, filter === 'ALL' && styles.filterButtonActive]}
        onPress={() => setFilter('ALL')}
      >
        <Text style={[styles.filterButtonText, filter === 'ALL' && styles.filterButtonTextActive]}>
          Tous
        </Text>
      </TouchableOpacity>
      <TouchableOpacity
        style={[styles.filterButton, filter === 'NOT_ASSIGNED' && styles.filterButtonActive]}
        onPress={() => setFilter('NOT_ASSIGNED')}
      >
        <Text
          style={[
            styles.filterButtonText,
            filter === 'NOT_ASSIGNED' && styles.filterButtonTextActive,
          ]}
        >
          Non assignés
        </Text>
      </TouchableOpacity>
      <TouchableOpacity
        style={[styles.filterButton, filter === 'ASSIGNED' && styles.filterButtonActive]}
        onPress={() => setFilter('ASSIGNED')}
      >
        <Text
          style={[styles.filterButtonText, filter === 'ASSIGNED' && styles.filterButtonTextActive]}
        >
          Assignés
        </Text>
      </TouchableOpacity>
    </View>
  );

  if (isLoading && tags.length === 0) {
    return (
      <View style={styles.centerContainer}>
        <ActivityIndicator size="large" color="#007AFF" />
        <Text style={styles.loadingText}>Chargement des tags RFID...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Tags RFID</Text>
        <TouchableOpacity
          style={styles.createButton}
          onPress={() => navigation.navigate('CreateRFIDTag')}
        >
          <Text style={styles.createButtonText}>+ Nouveau</Text>
        </TouchableOpacity>
      </View>

      {renderFilterButtons()}

      <FlatList
        data={tags}
        renderItem={renderTagItem}
        keyExtractor={(item) => item.id}
        contentContainerStyle={styles.list}
        refreshControl={<RefreshControl refreshing={isRefreshing} onRefresh={handleRefresh} />}
        onEndReached={handleLoadMore}
        onEndReachedThreshold={0.5}
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <Text style={styles.emptyText}>Aucun tag RFID trouvé</Text>
            <TouchableOpacity
              style={styles.emptyButton}
              onPress={() => navigation.navigate('CreateRFIDTag')}
            >
              <Text style={styles.emptyButtonText}>Créer un tag RFID</Text>
            </TouchableOpacity>
          </View>
        }
        ListFooterComponent={
          hasMore && tags.length > 0 ? (
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
  createButton: {
    backgroundColor: '#4CAF50',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 6,
  },
  createButtonText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600',
  },
  filterContainer: {
    flexDirection: 'row',
    padding: 16,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#ddd',
  },
  filterButton: {
    flex: 1,
    paddingVertical: 8,
    paddingHorizontal: 12,
    borderRadius: 6,
    backgroundColor: '#f0f0f0',
    marginHorizontal: 4,
    alignItems: 'center',
  },
  filterButtonActive: {
    backgroundColor: '#007AFF',
  },
  filterButtonText: {
    fontSize: 14,
    color: '#666',
    fontWeight: '500',
  },
  filterButtonTextActive: {
    color: '#fff',
    fontWeight: '600',
  },
  list: {
    padding: 16,
  },
  tagCard: {
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
  tagHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 12,
  },
  tagNumberContainer: {
    flex: 1,
    marginRight: 12,
  },
  tagNumber: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 4,
  },
  tagLabel: {
    fontSize: 14,
    color: '#666',
  },
  statusBadge: {
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 4,
  },
  statusText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: '600',
  },
  tagInfo: {
    borderTopWidth: 1,
    borderTopColor: '#f0f0f0',
    paddingTop: 12,
  },
  tagInfoText: {
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
    marginBottom: 16,
  },
  emptyButton: {
    backgroundColor: '#4CAF50',
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 8,
  },
  emptyButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  footer: {
    paddingVertical: 16,
    alignItems: 'center',
  },
});

