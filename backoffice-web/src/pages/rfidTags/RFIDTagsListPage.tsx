import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { rfidTagService } from '../../services/api';
import { Card, Button, ConfirmDialog, Select } from '../../components/common';
import { RFIDTagFormDialog } from '../../components/rfidTags/RFIDTagFormDialog';
import { RFIDTagDetailsDialog } from '../../components/rfidTags/RFIDTagDetailsDialog';
import { BulkImportDialog } from '../../components/rfidTags/BulkImportDialog';
import { RFIDTag, RFIDTagStatus, RFIDTagDetail } from '../../types';
import { Plus, Pencil, Trash2, Eye, Upload, Filter, Power, PowerOff } from 'lucide-react';

const RFIDTagsListPage = () => {
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [isDetailsOpen, setIsDetailsOpen] = useState(false);
  const [isBulkImportOpen, setIsBulkImportOpen] = useState(false);
  const [selectedTag, setSelectedTag] = useState<RFIDTag | undefined>();
  const [tagToView, setTagToView] = useState<RFIDTagDetail | null>(null);
  const [tagToDelete, setTagToDelete] = useState<RFIDTag | null>(null);
  const [deleteError, setDeleteError] = useState<string | null>(null);

  // Filters
  const [statusFilter, setStatusFilter] = useState<RFIDTagStatus | ''>('');
  const [activeFilter, setActiveFilter] = useState<'all' | 'active' | 'inactive'>('all');

  const queryClient = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ['rfid-tags', statusFilter, activeFilter],
    queryFn: () =>
      rfidTagService.list({
        status: statusFilter || undefined,
        is_active: activeFilter === 'all' ? undefined : activeFilter === 'active',
        page: 1,
        page_size: 50,
      }),
  });

  const deleteMutation = useMutation({
    mutationFn: (tagId: string) => rfidTagService.delete(tagId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['rfid-tags'] });
      setTagToDelete(null);
      setDeleteError(null);
    },
    onError: (error: any) => {
      // Extraire le message d'erreur de différentes structures possibles
      let errorMessage = 'Erreur lors de la suppression du tag RFID';
      
      if (error.response?.data) {
        // FastAPI retourne souvent {detail: "message"}
        if (error.response.data.detail) {
          errorMessage = error.response.data.detail;
        } else if (error.response.data.message) {
          errorMessage = error.response.data.message;
        } else if (typeof error.response.data === 'string') {
          errorMessage = error.response.data;
        }
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      setDeleteError(errorMessage);
      console.error('Error deleting RFID tag:', error);
    },
  });

  const toggleActiveMutation = useMutation({
    mutationFn: ({ tagId, isActive }: { tagId: string; isActive: boolean }) =>
      rfidTagService.update(tagId, { is_active: !isActive }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['rfid-tags'] });
    },
    onError: (error: any) => {
      console.error('Error toggling tag active status:', error);
      // Vous pouvez ajouter une notification d'erreur ici si nécessaire
    },
  });

  const handleCreateTag = () => {
    setSelectedTag(undefined);
    setIsFormOpen(true);
  };

  const handleViewTag = async (tag: RFIDTag) => {
    // Fetch full details including palette info
    try {
      const fullTag = await rfidTagService.getById(tag.id);
      setTagToView(fullTag);
      setIsDetailsOpen(true);
    } catch (error) {
      console.error('Error fetching tag details:', error);
    }
  };

  const handleEditTag = (tag: RFIDTag) => {
    setSelectedTag(tag);
    setIsFormOpen(true);
  };

  const handleEditFromDetails = () => {
    if (tagToView) {
      setIsDetailsOpen(false);
      setSelectedTag(tagToView);
      setIsFormOpen(true);
    }
  };

  const handleDeleteClick = (tag: RFIDTag) => {
    setTagToDelete(tag);
    setDeleteError(null);
  };

  const handleConfirmDelete = () => {
    if (tagToDelete) {
      setDeleteError(null);
      deleteMutation.mutate(tagToDelete.id);
    }
  };

  const handleToggleActive = (tag: RFIDTag) => {
    toggleActiveMutation.mutate({ tagId: tag.id, isActive: tag.is_active });
  };

  const getStatusLabel = (status: RFIDTagStatus) => {
    const statusLabels: Record<RFIDTagStatus, string> = {
      [RFIDTagStatus.NOT_ASSIGNED]: 'Non assigné',
      [RFIDTagStatus.ASSIGNED]: 'Assigné',
      [RFIDTagStatus.LOST]: 'Perdu',
      [RFIDTagStatus.DAMAGED]: 'Endommagé',
    };
    return statusLabels[status];
  };

  const getStatusColor = (status: RFIDTagStatus) => {
    const statusColors: Record<RFIDTagStatus, string> = {
      [RFIDTagStatus.NOT_ASSIGNED]: 'bg-gray-100 text-gray-800',
      [RFIDTagStatus.ASSIGNED]: 'bg-green-100 text-green-800',
      [RFIDTagStatus.LOST]: 'bg-red-100 text-red-800',
      [RFIDTagStatus.DAMAGED]: 'bg-orange-100 text-orange-800',
    };
    return statusColors[status];
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold">Tags RFID</h1>
          <p className="text-muted-foreground">Gérer les tags RFID du système</p>
        </div>
        <div className="flex space-x-3">
          <Button variant="outline" onClick={() => setIsBulkImportOpen(true)}>
            <Upload className="h-4 w-4 mr-2" />
            Import CSV
          </Button>
          <Button onClick={handleCreateTag}>
            <Plus className="h-4 w-4 mr-2" />
            Nouveau tag
          </Button>
        </div>
      </div>

      {/* Filters */}
      <Card className="mb-6">
        <div className="p-4">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <Filter className="h-5 w-5 text-gray-500" />
              <span className="text-sm font-medium text-gray-700">Filtres:</span>
            </div>
            <div className="flex-1 grid grid-cols-1 md:grid-cols-2 gap-4">
              <Select
                label=""
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value as RFIDTagStatus | '')}
                options={[
                  { value: '', label: 'Tous les statuts' },
                  { value: RFIDTagStatus.NOT_ASSIGNED, label: 'Non assigné' },
                  { value: RFIDTagStatus.ASSIGNED, label: 'Assigné' },
                  { value: RFIDTagStatus.LOST, label: 'Perdu' },
                  { value: RFIDTagStatus.DAMAGED, label: 'Endommagé' },
                ]}
              />
              <Select
                label=""
                value={activeFilter}
                onChange={(e) =>
                  setActiveFilter(e.target.value as 'all' | 'active' | 'inactive')
                }
                options={[
                  { value: 'all', label: 'Tous' },
                  { value: 'active', label: 'Actifs uniquement' },
                  { value: 'inactive', label: 'Inactifs uniquement' },
                ]}
              />
            </div>
          </div>
        </div>
      </Card>

      {/* Tags list */}
      <Card>
        {isLoading ? (
          <div className="p-8 text-center">Chargement...</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b">
                  <th className="px-4 py-3 text-left text-sm font-medium">Numéro de tag</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">Libellé</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">Statut</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">État</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">Notes</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">Date création</th>
                  <th className="px-4 py-3 text-right text-sm font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {data?.items.map((tag) => (
                  <tr key={tag.id} className="border-b hover:bg-accent/50">
                    <td className="px-4 py-3 font-medium font-mono text-sm">
                      {tag.tag_number}
                    </td>
                    <td className="px-4 py-3 text-sm">
                      {tag.label || '-'}
                    </td>
                    <td className="px-4 py-3">
                      <span
                        className={`inline-flex px-2 py-1 text-xs font-semibold rounded ${getStatusColor(
                          tag.status
                        )}`}
                      >
                        {getStatusLabel(tag.status)}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <span
                        className={`inline-flex px-2 py-1 text-xs font-semibold rounded ${
                          tag.is_active
                            ? 'bg-green-100 text-green-800'
                            : 'bg-gray-100 text-gray-800'
                        }`}
                      >
                        {tag.is_active ? 'Actif' : 'Inactif'}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm max-w-xs truncate">
                      {tag.notes || '-'}
                    </td>
                    <td className="px-4 py-3 text-sm">
                      {new Date(tag.created_at).toLocaleDateString('fr-FR')}
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex justify-end space-x-2">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleViewTag(tag)}
                          title="Voir les détails"
                        >
                          <Eye className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleEditTag(tag)}
                          title="Modifier"
                        >
                          <Pencil className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleToggleActive(tag)}
                          title={tag.is_active ? 'Désactiver' : 'Activer'}
                          className={
                            tag.is_active
                              ? 'text-green-600 hover:text-green-700 hover:bg-green-50'
                              : 'text-gray-600 hover:text-gray-700 hover:bg-gray-50'
                          }
                          disabled={toggleActiveMutation.isPending}
                        >
                          {tag.is_active ? (
                            <Power className="h-4 w-4" />
                          ) : (
                            <PowerOff className="h-4 w-4" />
                          )}
                        </Button>
                        {tag.status === RFIDTagStatus.NOT_ASSIGNED && (
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleDeleteClick(tag)}
                            title="Supprimer définitivement"
                            className="text-red-600 hover:text-red-700 hover:bg-red-50"
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            {data?.items.length === 0 && (
              <div className="p-8 text-center text-gray-500">
                Aucun tag RFID trouvé
              </div>
            )}
          </div>
        )}
      </Card>

      {/* Dialogs */}
      <RFIDTagFormDialog
        isOpen={isFormOpen}
        onClose={() => setIsFormOpen(false)}
        tag={selectedTag}
      />

      <RFIDTagDetailsDialog
        isOpen={isDetailsOpen}
        onClose={() => setIsDetailsOpen(false)}
        tag={tagToView}
        onEdit={handleEditFromDetails}
      />

      <BulkImportDialog
        isOpen={isBulkImportOpen}
        onClose={() => setIsBulkImportOpen(false)}
      />

      <ConfirmDialog
        isOpen={!!tagToDelete}
        onClose={() => {
          setTagToDelete(null);
          setDeleteError(null);
        }}
        onConfirm={handleConfirmDelete}
        title="Confirmer la suppression"
        message={
          deleteError ? (
            <div className="space-y-2">
              <p>
                Êtes-vous sûr de vouloir supprimer définitivement le tag RFID "{tagToDelete?.tag_number}" ? Cette action est irréversible et ne peut être annulée.
              </p>
              <div className="p-3 bg-red-50 border border-red-200 text-red-700 rounded-lg text-sm mt-2">
                {deleteError}
              </div>
            </div>
          ) : (
            `Êtes-vous sûr de vouloir supprimer définitivement le tag RFID "${tagToDelete?.tag_number}" ? Cette action est irréversible et ne peut être annulée.`
          )
        }
        confirmText="Supprimer"
        variant="danger"
        isLoading={deleteMutation.isPending}
      />
    </div>
  );
};

export default RFIDTagsListPage;
