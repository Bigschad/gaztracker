import { Platform } from 'react-native';

// Import conditionnel pour éviter les erreurs sur le web
let SQLite: any;

if (Platform.OS !== 'web') {
  try {
    SQLite = require('expo-sqlite');
  } catch (e) {
    console.warn('SQLite not available');
  }
}

class Database {
  private db: any = null;

  async init(): Promise<void> {
    if (Platform.OS === 'web') {
      console.log('Database: Mode web - utilisation de AsyncStorage');
      return;
    }

    if (!SQLite) {
      console.warn('SQLite not available');
      return;
    }

    try {
      this.db = await SQLite.openDatabaseAsync('gaztracker.db');
      await this.createTables();
    } catch (error) {
      console.error('Error initializing database:', error);
      throw error;
    }
  }

  private async createTables(): Promise<void> {
    if (Platform.OS === 'web' || !this.db) return;

    // Table pour les palettes
    await this.db.execAsync(`
      CREATE TABLE IF NOT EXISTS palettes (
        id TEXT PRIMARY KEY,
        serial_number TEXT NOT NULL,
        reference_code TEXT,
        rfid_tag_id TEXT,
        type TEXT NOT NULL,
        capacity INTEGER NOT NULL,
        current_fill INTEGER NOT NULL,
        status TEXT NOT NULL,
        location_latitude REAL,
        location_longitude REAL,
        location_address TEXT,
        notes TEXT,
        current_expedition_id TEXT,
        current_partner_id TEXT,
        created_by_id TEXT NOT NULL,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        synced INTEGER DEFAULT 0
      );
    `);

    // Table pour les expéditions
    await this.db.execAsync(`
      CREATE TABLE IF NOT EXISTS expeditions (
        id TEXT PRIMARY KEY,
        reference_number TEXT NOT NULL UNIQUE,
        status TEXT NOT NULL,
        date_creation TEXT NOT NULL,
        date_departure TEXT,
        eta TEXT,
        date_arrival TEXT,
        date_delivery TEXT,
        transporter TEXT,
        vehicle_info TEXT,
        destination_address TEXT NOT NULL,
        destination_contact TEXT,
        destination_phone TEXT,
        notes TEXT,
        otp_code TEXT,
        otp_expiry TEXT,
        palette_count INTEGER DEFAULT 0,
        grossiste_id TEXT,
        driver_id TEXT,
        created_by_id TEXT NOT NULL,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        synced INTEGER DEFAULT 0
      );
    `);

    // Table pour les tags RFID
    await this.db.execAsync(`
      CREATE TABLE IF NOT EXISTS rfid_tags (
        id TEXT PRIMARY KEY,
        tag_number TEXT NOT NULL UNIQUE,
        label TEXT,
        status TEXT NOT NULL,
        is_active INTEGER DEFAULT 1,
        created_by_id TEXT NOT NULL,
        notes TEXT,
        assigned_at TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        synced INTEGER DEFAULT 0
      );
    `);

    // Table pour la queue de sync
    await this.db.execAsync(`
      CREATE TABLE IF NOT EXISTS sync_queue (
        id TEXT PRIMARY KEY,
        action TEXT NOT NULL,
        entity TEXT NOT NULL,
        entity_id TEXT,
        data TEXT NOT NULL,
        timestamp INTEGER NOT NULL,
        retry_count INTEGER DEFAULT 0,
        status TEXT DEFAULT 'PENDING',
        error_message TEXT
      );
    `);

    // Index pour améliorer les performances
    await this.db.execAsync(`
      CREATE INDEX IF NOT EXISTS idx_palettes_rfid ON palettes(rfid_tag_id);
      CREATE INDEX IF NOT EXISTS idx_palettes_expedition ON palettes(current_expedition_id);
      CREATE INDEX IF NOT EXISTS idx_palettes_status ON palettes(status);
      CREATE INDEX IF NOT EXISTS idx_expeditions_status ON expeditions(status);
      CREATE INDEX IF NOT EXISTS idx_expeditions_driver ON expeditions(driver_id);
      CREATE INDEX IF NOT EXISTS idx_sync_queue_status ON sync_queue(status);
    `);
  }

  // Méthodes pour les palettes
  async savePalette(palette: any): Promise<void> {
    if (Platform.OS === 'web') {
      // Utiliser AsyncStorage sur le web
      const AsyncStorage = require('@react-native-async-storage/async-storage').default;
      const palettes = JSON.parse((await AsyncStorage.getItem('palettes')) || '[]');
      const index = palettes.findIndex((p: any) => p.id === palette.id);
      if (index !== -1) {
        palettes[index] = palette;
      } else {
        palettes.push(palette);
      }
      await AsyncStorage.setItem('palettes', JSON.stringify(palettes));
      return;
    }

    if (!this.db) throw new Error('Database not initialized');

    await this.db.runAsync(
      `INSERT OR REPLACE INTO palettes (
        id, serial_number, reference_code, rfid_tag_id, type, capacity, current_fill,
        status, location_latitude, location_longitude, location_address, notes,
        current_expedition_id, current_partner_id, created_by_id, created_at, updated_at, synced
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
      [
        palette.id,
        palette.serialNumber,
        palette.referenceCode || null,
        palette.rfidTagId || null,
        palette.type,
        palette.capacity,
        palette.currentFill,
        palette.status,
        palette.locationLatitude || null,
        palette.locationLongitude || null,
        palette.locationAddress || null,
        palette.notes || null,
        palette.currentExpeditionId || null,
        palette.currentPartnerId || null,
        palette.createdById,
        palette.createdAt,
        palette.updatedAt,
        0, // synced = false
      ]
    );
  }

  async getPalette(id: string): Promise<any | null> {
    if (Platform.OS === 'web') {
      const AsyncStorage = require('@react-native-async-storage/async-storage').default;
      const palettes = JSON.parse((await AsyncStorage.getItem('palettes')) || '[]');
      return palettes.find((p: any) => p.id === id) || null;
    }

    if (!this.db) throw new Error('Database not initialized');

    const result = await this.db.getFirstAsync<any>(
      'SELECT * FROM palettes WHERE id = ?',
      [id]
    );
    return result || null;
  }

  async getPaletteByRfid(rfidTagId: string): Promise<any | null> {
    if (Platform.OS === 'web') {
      const AsyncStorage = require('@react-native-async-storage/async-storage').default;
      const palettes = JSON.parse((await AsyncStorage.getItem('palettes')) || '[]');
      return palettes.find((p: any) => p.rfidTagId === rfidTagId) || null;
    }

    if (!this.db) throw new Error('Database not initialized');

    const result = await this.db.getFirstAsync<any>(
      'SELECT * FROM palettes WHERE rfid_tag_id = ?',
      [rfidTagId]
    );
    return result || null;
  }

  async getAllPalettes(): Promise<any[]> {
    if (Platform.OS === 'web') {
      const AsyncStorage = require('@react-native-async-storage/async-storage').default;
      return JSON.parse((await AsyncStorage.getItem('palettes')) || '[]');
    }

    if (!this.db) throw new Error('Database not initialized');

    return await this.db.getAllAsync<any>('SELECT * FROM palettes ORDER BY updated_at DESC');
  }

  // Méthodes pour les expéditions
  async saveExpedition(expedition: any): Promise<void> {
    if (Platform.OS === 'web') {
      const AsyncStorage = require('@react-native-async-storage/async-storage').default;
      const expeditions = JSON.parse((await AsyncStorage.getItem('expeditions')) || '[]');
      const index = expeditions.findIndex((e: any) => e.id === expedition.id);
      if (index !== -1) {
        expeditions[index] = expedition;
      } else {
        expeditions.push(expedition);
      }
      await AsyncStorage.setItem('expeditions', JSON.stringify(expeditions));
      return;
    }

    if (!this.db) throw new Error('Database not initialized');

    await this.db.runAsync(
      `INSERT OR REPLACE INTO expeditions (
        id, reference_number, status, date_creation, date_departure, eta,
        date_arrival, date_delivery, transporter, vehicle_info, destination_address,
        destination_contact, destination_phone, notes, otp_code, otp_expiry,
        palette_count, grossiste_id, driver_id, created_by_id, created_at, updated_at, synced
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
      [
        expedition.id,
        expedition.referenceNumber,
        expedition.status,
        expedition.dateCreation,
        expedition.dateDeparture || null,
        expedition.eta || null,
        expedition.dateArrival || null,
        expedition.dateDelivery || null,
        expedition.transporter || null,
        expedition.vehicleInfo || null,
        expedition.destinationAddress,
        expedition.destinationContact || null,
        expedition.destinationPhone || null,
        expedition.notes || null,
        expedition.otpCode || null,
        expedition.otpExpiry || null,
        expedition.paletteCount || 0,
        expedition.grossisteId || null,
        expedition.driverId || null,
        expedition.createdById,
        expedition.createdAt,
        expedition.updatedAt,
        0, // synced = false
      ]
    );
  }

  async getExpedition(id: string): Promise<any | null> {
    if (Platform.OS === 'web') {
      const AsyncStorage = require('@react-native-async-storage/async-storage').default;
      const expeditions = JSON.parse((await AsyncStorage.getItem('expeditions')) || '[]');
      return expeditions.find((e: any) => e.id === id) || null;
    }

    if (!this.db) throw new Error('Database not initialized');

    const result = await this.db.getFirstAsync<any>(
      'SELECT * FROM expeditions WHERE id = ?',
      [id]
    );
    return result || null;
  }

  async getAllExpeditions(): Promise<any[]> {
    if (Platform.OS === 'web') {
      const AsyncStorage = require('@react-native-async-storage/async-storage').default;
      return JSON.parse((await AsyncStorage.getItem('expeditions')) || '[]');
    }

    if (!this.db) throw new Error('Database not initialized');

    return await this.db.getAllAsync<any>('SELECT * FROM expeditions ORDER BY updated_at DESC');
  }

  // Méthodes pour la queue de sync
  async addToSyncQueue(item: {
    action: string;
    entity: string;
    entityId?: string;
    data: any;
  }): Promise<void> {
    if (Platform.OS === 'web') {
      const AsyncStorage = require('@react-native-async-storage/async-storage').default;
      const queue = JSON.parse((await AsyncStorage.getItem('sync_queue')) || '[]');
      const queueItem = {
        id: `sync_${Date.now()}_${Math.random()}`,
        ...item,
        timestamp: Date.now(),
        retryCount: 0,
        status: 'PENDING',
      };
      queue.push(queueItem);
      await AsyncStorage.setItem('sync_queue', JSON.stringify(queue));
      return;
    }

    if (!this.db) throw new Error('Database not initialized');

    const id = `sync_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    await this.db.runAsync(
      `INSERT INTO sync_queue (id, action, entity, entity_id, data, timestamp, status)
       VALUES (?, ?, ?, ?, ?, ?, ?)`,
      [
        id,
        item.action,
        item.entity,
        item.entityId || null,
        JSON.stringify(item.data),
        Date.now(),
        'PENDING',
      ]
    );
  }

  async getSyncQueue(status: string = 'PENDING'): Promise<any[]> {
    if (Platform.OS === 'web') {
      const AsyncStorage = require('@react-native-async-storage/async-storage').default;
      const queue = JSON.parse((await AsyncStorage.getItem('sync_queue')) || '[]');
      return queue.filter((item: any) => item.status === status).map((item: any) => ({
        ...item,
        data: typeof item.data === 'string' ? JSON.parse(item.data) : item.data,
      }));
    }

    if (!this.db) throw new Error('Database not initialized');

    const results = await this.db.getAllAsync<any>(
      'SELECT * FROM sync_queue WHERE status = ? ORDER BY timestamp ASC',
      [status]
    );
    return results.map((item) => ({
      ...item,
      data: JSON.parse(item.data),
    }));
  }

  async updateSyncQueueItem(id: string, updates: { status?: string; retryCount?: number; errorMessage?: string }): Promise<void> {
    if (Platform.OS === 'web') {
      const AsyncStorage = require('@react-native-async-storage/async-storage').default;
      const queue = JSON.parse((await AsyncStorage.getItem('sync_queue')) || '[]');
      const index = queue.findIndex((item: any) => item.id === id);
      if (index !== -1) {
        queue[index] = { ...queue[index], ...updates };
        await AsyncStorage.setItem('sync_queue', JSON.stringify(queue));
      }
      return;
    }

    if (!this.db) throw new Error('Database not initialized');

    const setClause: string[] = [];
    const values: any[] = [];

    if (updates.status !== undefined) {
      setClause.push('status = ?');
      values.push(updates.status);
    }
    if (updates.retryCount !== undefined) {
      setClause.push('retry_count = ?');
      values.push(updates.retryCount);
    }
    if (updates.errorMessage !== undefined) {
      setClause.push('error_message = ?');
      values.push(updates.errorMessage);
    }

    if (setClause.length > 0) {
      values.push(id);
      await this.db.runAsync(
        `UPDATE sync_queue SET ${setClause.join(', ')} WHERE id = ?`,
        values
      );
    }
  }

  async removeFromSyncQueue(id: string): Promise<void> {
    if (Platform.OS === 'web') {
      const AsyncStorage = require('@react-native-async-storage/async-storage').default;
      const queue = JSON.parse((await AsyncStorage.getItem('sync_queue')) || '[]');
      const filtered = queue.filter((item: any) => item.id !== id);
      await AsyncStorage.setItem('sync_queue', JSON.stringify(filtered));
      return;
    }

    if (!this.db) throw new Error('Database not initialized');

    await this.db.runAsync('DELETE FROM sync_queue WHERE id = ?', [id]);
  }

  async markAsSynced(table: string, id: string): Promise<void> {
    if (Platform.OS === 'web') {
      // No-op sur le web
      return;
    }

    if (!this.db) throw new Error('Database not initialized');

    await this.db.runAsync(`UPDATE ${table} SET synced = 1 WHERE id = ?`, [id]);
  }

  getDatabase(): any {
    return this.db;
  }
}

export const database = new Database();

