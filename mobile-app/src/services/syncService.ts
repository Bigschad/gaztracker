import { database } from '../storage/database';
import { useAppDispatch } from '../redux/hooks';
import { paletteApi } from '../api/paletteApi';
import { expeditionApi } from '../api/expeditionApi';
import { rfidApi } from '../api/rfidApi';
import { updateSyncQueueItem, removeFromSyncQueue, setSyncing, setLastSyncTime } from '../redux/slices/offlineSlice';
import { MAX_SYNC_RETRIES } from '../config/constants';

class SyncService {
  private isSyncing = false;

  async syncQueue(): Promise<{ success: number; failed: number }> {
    if (this.isSyncing) {
      return { success: 0, failed: 0 };
    }

    this.isSyncing = true;
    let successCount = 0;
    let failedCount = 0;

    try {
      const queueItems = await database.getSyncQueue('PENDING');

      for (const item of queueItems) {
        try {
          await this.processSyncItem(item);
          await database.removeFromSyncQueue(item.id);
          successCount++;
        } catch (error: any) {
          const retryCount = (item.retry_count || 0) + 1;

          if (retryCount >= MAX_SYNC_RETRIES) {
            // Marquer comme échoué après max tentatives
            await database.updateSyncQueueItem(item.id, {
              status: 'FAILED',
              retryCount,
              errorMessage: error.message || 'Max retries reached',
            });
            failedCount++;
          } else {
            // Réessayer plus tard
            await database.updateSyncQueueItem(item.id, {
              status: 'PENDING',
              retryCount,
              errorMessage: error.message,
            });
            failedCount++;
          }
        }
      }
    } finally {
      this.isSyncing = false;
    }

    return { success: successCount, failed: failedCount };
  }

  private async processSyncItem(item: any): Promise<void> {
    const { action, entity, data } = item;

    switch (entity) {
      case 'PALETTE':
        await this.syncPalette(action, data);
        break;
      case 'EXPEDITION':
        await this.syncExpedition(action, data);
        break;
      case 'RFID_TAG':
        await this.syncRfidTag(action, data);
        break;
      case 'SCAN':
        await this.syncScan(action, data);
        break;
      default:
        throw new Error(`Unknown entity: ${entity}`);
    }
  }

  private async syncPalette(action: string, data: any): Promise<void> {
    switch (action) {
      case 'CREATE':
        await paletteApi.create(data);
        break;
      case 'UPDATE':
        // TODO: Implémenter update palette API
        break;
      case 'SCAN':
        await paletteApi.scan(data);
        break;
      default:
        throw new Error(`Unknown action for PALETTE: ${action}`);
    }
  }

  private async syncExpedition(action: string, data: any): Promise<void> {
    switch (action) {
      case 'ASSIGN_PALETTES':
        await expeditionApi.assignPalettes(data.expeditionId, data.paletteIds);
        break;
      default:
        throw new Error(`Unknown action for EXPEDITION: ${action}`);
    }
  }

  private async syncRfidTag(action: string, data: any): Promise<void> {
    switch (action) {
      case 'CREATE':
        await rfidApi.create(data);
        break;
      default:
        throw new Error(`Unknown action for RFID_TAG: ${action}`);
    }
  }

  private async syncScan(action: string, data: any): Promise<void> {
    if (action === 'CREATE') {
      await paletteApi.scan(data);
    }
  }

  async syncAll(): Promise<void> {
    // Sync les données non synchronisées
    const palettes = await database.getAllPalettes();
    const unsyncedPalettes = palettes.filter((p) => !p.synced);

    for (const palette of unsyncedPalettes) {
      try {
        await paletteApi.create(palette);
        await database.markAsSynced('palettes', palette.id);
      } catch (error) {
        console.error('Error syncing palette:', error);
      }
    }

    const expeditions = await database.getAllExpeditions();
    const unsyncedExpeditions = expeditions.filter((e) => !e.synced);

    for (const expedition of unsyncedExpeditions) {
      try {
        // TODO: Sync expedition
        await database.markAsSynced('expeditions', expedition.id);
      } catch (error) {
        console.error('Error syncing expedition:', error);
      }
    }

    // Sync la queue
    await this.syncQueue();
  }
}

export const syncService = new SyncService();

