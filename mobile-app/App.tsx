import React from 'react';
import { View, Text, StyleSheet, ActivityIndicator } from 'react-native';
import { Provider } from 'react-redux';
import { PersistGate } from 'redux-persist/integration/react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { StatusBar } from 'expo-status-bar';
import { ErrorBoundary } from './src/components/ErrorBoundary';

// Imports conditionnels pour éviter les erreurs si un module n'est pas disponible
let store: any;
let persistor: any;
let useAuth: any;
let LoginScreen: any;
let DashboardScreen: any;
let LoadingScreen: any;
let UnloadingScreen: any;
let DeliveryNoteScreen: any;

try {
  const storeModule = require('./src/redux/store');
  store = storeModule.store;
  persistor = storeModule.persistor;
} catch (error) {
  console.error('[App] ❌ Error importing store:', error);
}

try {
  useAuth = require('./src/hooks/useAuth').useAuth;
} catch (error) {
  console.error('[App] ❌ Error importing useAuth:', error);
}

try {
  LoginScreen = require('./src/screens/LoginScreen').LoginScreen;
} catch (error) {
  console.error('[App] ❌ Error importing LoginScreen:', error);
}

try {
  DashboardScreen = require('./src/screens/DashboardScreen').DashboardScreen;
} catch (error) {
  console.error('[App] ❌ Error importing DashboardScreen:', error);
}

try {
  LoadingScreen = require('./src/screens/LoadingScreen').LoadingScreen;
} catch (error) {
  console.error('[App] ❌ Error importing LoadingScreen:', error);
}

try {
  UnloadingScreen = require('./src/screens/UnloadingScreen').UnloadingScreen;
} catch (error) {
  console.error('[App] ❌ Error importing UnloadingScreen:', error);
}

try {
  DeliveryNoteScreen = require('./src/screens/DeliveryNoteScreen').DeliveryNoteScreen;
} catch (error) {
  console.error('[App] ❌ Error importing DeliveryNoteScreen:', error);
}

let CreateRFIDTagScreen: any;
try {
  CreateRFIDTagScreen = require('./src/screens/CreateRFIDTagScreen').CreateRFIDTagScreen;
} catch (error) {
  console.error('[App] ❌ Error importing CreateRFIDTagScreen:', error);
}

let RFIDTagsListScreen: any;
try {
  RFIDTagsListScreen = require('./src/screens/RFIDTagsListScreen').RFIDTagsListScreen;
} catch (error) {
  console.error('[App] ❌ Error importing RFIDTagsListScreen:', error);
}

let VehiclesListScreen: any;
try {
  VehiclesListScreen = require('./src/screens/VehiclesListScreen').VehiclesListScreen;
} catch (error) {
  console.error('[App] ❌ Error importing VehiclesListScreen:', error);
}

const Stack = createStackNavigator();

const PersistGateLoading = () => (
  <View style={styles.container}>
    <ActivityIndicator size="large" color="#007AFF" />
    <Text style={styles.subtext}>Chargement PersistGate...</Text>
  </View>
);

// Screen placeholder pour ExpeditionDetail (à implémenter plus tard)
const ExpeditionDetailScreen = ({ navigation }: { navigation: any }) => {
  // Pour l'instant, afficher un écran simple
  // L'implémentation complète utilisera useAppSelector pour récupérer currentExpedition
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Détails de l'expédition</Text>
      <Text style={styles.text}>
        L'écran de détails de l'expédition sera implémenté ici.
      </Text>
      <Text style={styles.subtext}>
        L'expédition sélectionnée sera affichée avec toutes ses informations.
      </Text>
    </View>
  );
};

// Screen placeholder pour Notifications (à implémenter plus tard)
const NotificationsScreen = () => (
  <View style={styles.container}>
    <Text style={styles.title}>Notifications</Text>
    <Text style={styles.text}>Écran de notifications à implémenter</Text>
  </View>
);

const AppNavigator = () => {
  if (!useAuth) {
    throw new Error('useAuth hook is not available. Check imports.');
  }
  
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <View style={styles.container}>
        <ActivityIndicator size="large" color="#007AFF" />
        <Text style={styles.subtext}>Vérification de session...</Text>
      </View>
    );
  }

  if (!isAuthenticated) {
    if (!LoginScreen) {
      return (
        <View style={styles.container}>
          <Text style={styles.title}>❌ LoginScreen non disponible</Text>
          <Text style={styles.text}>
            Le LoginScreen n'a pas pu être chargé.
          </Text>
        </View>
      );
    }
    return (
      <Stack.Navigator 
        screenOptions={{ 
          headerShown: false,
          cardStyle: { backgroundColor: '#fff' },
        }}
      >
        <Stack.Screen name="Login" component={LoginScreen} />
      </Stack.Navigator>
    );
  }

  // Navigation principale pour les utilisateurs authentifiés
  return (
    <Stack.Navigator
      screenOptions={{
        headerStyle: {
          backgroundColor: '#007AFF',
          shadowColor: 'transparent',
          shadowOffset: { width: 0, height: 0 },
          shadowOpacity: 0,
          shadowRadius: 0,
          elevation: 0,
        },
        headerTintColor: '#fff',
        headerTitleStyle: {
          fontWeight: 'bold',
        },
        cardStyle: { 
          backgroundColor: '#f5f5f5',
          shadowColor: 'transparent',
          shadowOffset: { width: 0, height: 0 },
          shadowOpacity: 0,
          shadowRadius: 0,
          elevation: 0,
        },
      }}
    >
      <Stack.Screen 
        name="Dashboard" 
        component={DashboardScreen || ExpeditionDetailScreen}
        options={{ title: 'Mes Expéditions' }}
      />
      {LoadingScreen && (
        <Stack.Screen 
          name="Loading" 
          component={LoadingScreen}
          options={{ title: 'Chargement' }}
        />
      )}
      {UnloadingScreen && (
        <Stack.Screen 
          name="Unloading" 
          component={UnloadingScreen}
          options={{ title: 'Déchargement' }}
        />
      )}
      {DeliveryNoteScreen && (
        <Stack.Screen 
          name="DeliveryNote" 
          component={DeliveryNoteScreen}
          options={{ title: 'Bon de Livraison' }}
        />
      )}
      {CreateRFIDTagScreen && (
        <Stack.Screen 
          name="CreateRFIDTag" 
          component={CreateRFIDTagScreen}
          options={{ title: 'Créer un tag RFID' }}
        />
      )}
      {RFIDTagsListScreen && (
        <Stack.Screen 
          name="RFIDTagsList" 
          component={RFIDTagsListScreen}
          options={{ title: 'Liste des tags RFID' }}
        />
      )}
      {VehiclesListScreen && (
        <Stack.Screen 
          name="VehiclesList" 
          component={VehiclesListScreen}
          options={{ title: 'Mes véhicules' }}
        />
      )}
      <Stack.Screen 
        name="ExpeditionDetail" 
        component={ExpeditionDetailScreen}
        options={{ title: 'Détails Expédition' }}
      />
      <Stack.Screen 
        name="Notifications" 
        component={NotificationsScreen}
        options={{ title: 'Notifications' }}
      />
    </Stack.Navigator>
  );
};

const AppContent = () => {
  React.useEffect(() => {
    console.log('[AppContent] Component mounted');
  }, []);

  try {
    return (
      <NavigationContainer>
        <AppNavigator />
        <StatusBar style="auto" />
      </NavigationContainer>
    );
  } catch (error) {
    console.error('[AppContent] Navigation error:', error);
    return (
      <View style={styles.container}>
        <Text style={styles.title}>❌ Erreur Navigation</Text>
        <Text style={styles.text}>
          {error instanceof Error ? error.message : 'Erreur inconnue'}
        </Text>
      </View>
    );
  }
};

export default function App() {
  React.useEffect(() => {
    if (store) {
      try {
        const state = store.getState();
        console.log('[App] ✅ Store initialized with slices:', Object.keys(state));
      } catch (error) {
        console.error('[App] ❌ Error accessing store state:', error);
      }
    }
  }, []);

  if (!store || !persistor) {
    return (
      <ErrorBoundary>
        <View style={styles.container}>
          <Text style={styles.title}>❌ Store non disponible</Text>
          <Text style={styles.text}>
            Le store Redux n'a pas pu être chargé.
          </Text>
          <Text style={styles.subtext}>
            Vérifiez la console pour l'erreur.
          </Text>
        </View>
      </ErrorBoundary>
    );
  }

  return (
    <ErrorBoundary>
      <Provider store={store}>
        <PersistGate loading={<PersistGateLoading />} persistor={persistor}>
          <AppContent />
        </PersistGate>
      </Provider>
    </ErrorBoundary>
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
    color: '#4CAF50',
    marginBottom: 16,
    textAlign: 'center',
  },
  text: {
    fontSize: 18,
    color: '#333',
    textAlign: 'center',
    marginBottom: 12,
  },
  subtext: {
    fontSize: 14,
    color: '#666',
    textAlign: 'center',
    marginBottom: 8,
  },
});
