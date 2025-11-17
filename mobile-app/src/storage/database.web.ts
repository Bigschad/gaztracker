// Stub pour le web - SQLite n'est pas disponible, utiliser localStorage
import AsyncStorage from '@react-native-async-storage/async-storage';

class DatabaseWeb {
  private async getStorageKey(key: string): Promise<any> {
    try {
      const data = await AsyncStorage.getItem(key);
      return data ? JSON.parse(data) : [];
    } catch {
      return [];
    }
  }

  private async setStorageKey(key: string, data: any): Promise<void> {
    await AsyncStorage.setItem(key, JSON.stringify(data));
  }

  async init(): Promise<void> {
    console.log('Database Web: Utilisation de AsyncStorage');
  }

  async savePalette(palette: any): Promise<void> {
    const palettes = await this.getStorageKey('palettes');
    const index = palettes.findIndex((p: any) => p.id === palette.id);
    if (index !== -1) {
      palettes[index] = palette;
    } else {
      palettes.push(palette);
    }
    await this.setStorageKey('palettes', palettes);
  }

  async getPalette(id: string): Promise<any | null> {
    const palettes = await this.getStorageKey('palettes');
    return palettes.find((p: any) => p.id === id) || null;
  }

  async getPaletteByRfid(rfidTagId: string): Promise<any | null> {
    const palettes = await this.getStorageKey('palettes');
    return palettes.find((p: any) => p.rfidTagId === rfidTagId) || null;
  }

  async getAllPalettes(): Promise<any[]> {
    return await this.getStorageKey('palettes');
  }

  async saveExpedition(expedition: any): Promise<void> {
    const expeditions = await this.getStorageKey('expeditions');
    const index = expeditions.findIndex((e: any) => e.id === expedition.id);
    if (index !== -1) {
      expeditions[index] = expedition;
    } else {
      expeditions.push(expedition);
    }
    await this.setStorageKey('expeditions', expeditions);
  }

  async getExpedition(id: string): Promise<any | null> {
    const expeditions = await this.getStorageKey('expeditions');
    return expeditions.find((e: any) => e.id === id) || null;
  }

  async getAllExpeditions(): Promise<any[]> {
    return await this.getStorageKey('expeditions');
  }

  async addToSyncQueue(item: {
    action: string;
    entity: string;
    entityId?: string;
    data: any;
  }): Promise<void> {
    const queue = await this.getStorageKey('sync_queue');
    const queueItem = {
      id: `sync_${Date.now()}_${Math.random()}`,
      ...item,
      timestamp: Date.now(),
      retryCount: 0,
      status: 'PENDING',
    };
    queue.push(queueItem);
    await this.setStorageKey('sync_queue', queue);
  }

  async getSyncQueue(status: string = 'PENDING'): Promise<any[]> {
    const queue = await this.getStorageKey('sync_queue');
    return queue.filter((item: any) => item.status === status);
  }

  async updateSyncQueueItem(
    id: string,
    updates: { status?: string; retryCount?: number; errorMessage?: string }
  ): Promise<void> {
    const queue = await this.getStorageKey('sync_queue');
    const index = queue.findIndex((item: any) => item.id === id);
    if (index !== -1) {
      queue[index] = { ...queue[index], ...updates };
      await this.setStorageKey('sync_queue', queue);
    }
  }

  async removeFromSyncQueue(id: string): Promise<void> {
    const queue = await this.getStorageKey('sync_queue');
    const filtered = queue.filter((item: any) => item.id !== id);
    await this.setStorageKey('sync_queue', filtered);
  }

  async markAsSynced(table: string, id: string): Promise<void> {
    // No-op pour le web
  }

  getDatabase(): any {
    return null;
  }
}

export const database = new DatabaseWeb();

