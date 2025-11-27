import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { useAppSelector } from '../../redux/hooks';

export const OfflineIndicator: React.FC = () => {
  const { isOnline, isSyncing } = useAppSelector((state) => state.offline);

  if (isOnline) {
    return null;
  }

  return (
    <View style={styles.container}>
      <View style={styles.content}>
        <Text style={styles.text}>Mode hors ligne</Text>
        {isSyncing && <Text style={styles.syncingText}>Synchronisation...</Text>}
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    backgroundColor: '#FF9800',
    paddingVertical: 8,
    paddingHorizontal: 16,
  },
  content: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  text: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600',
  },
  syncingText: {
    color: '#fff',
    fontSize: 12,
    fontStyle: 'italic',
  },
});

