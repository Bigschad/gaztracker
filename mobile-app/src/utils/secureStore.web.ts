// Version web de SecureStore utilisant AsyncStorage (qui fonctionne sur le web)
import AsyncStorage from '@react-native-async-storage/async-storage';

export const SecureStore = {
  async getItemAsync(key: string): Promise<string | null> {
    try {
      return await AsyncStorage.getItem(key);
    } catch (error) {
      console.error('Error getting item from SecureStore:', error);
      return null;
    }
  },

  async setItemAsync(key: string, value: string): Promise<void> {
    try {
      await AsyncStorage.setItem(key, value);
    } catch (error) {
      console.error('Error setting item in SecureStore:', error);
      throw error;
    }
  },

  async deleteItemAsync(key: string): Promise<void> {
    try {
      await AsyncStorage.removeItem(key);
    } catch (error) {
      console.error('Error deleting item from SecureStore:', error);
      throw error;
    }
  },
};

