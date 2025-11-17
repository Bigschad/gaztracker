import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

// Version de test ultra-minimale pour isoler le problème
export default function App() {
  console.log('[App.test] Component rendering...');
  
  React.useEffect(() => {
    console.log('[App.test] Component mounted');
  }, []);

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Test de démarrage</Text>
      <Text style={styles.text}>
        Si vous voyez ceci, React Native fonctionne.
      </Text>
      <Text style={styles.subtext}>
        Vérifiez la console pour les logs.
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f5f5f5',
    padding: 20,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 16,
  },
  text: {
    fontSize: 18,
    color: '#666',
    textAlign: 'center',
    marginBottom: 8,
  },
  subtext: {
    fontSize: 14,
    color: '#999',
    textAlign: 'center',
  },
});

