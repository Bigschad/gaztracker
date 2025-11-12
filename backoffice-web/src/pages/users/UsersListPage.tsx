import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { userService } from '../../services/api';
import { Card, Button, ConfirmDialog } from '../../components/common';
import { UserFormDialog } from '../../components/users/UserFormDialog';
import { UserDetailsDialog } from '../../components/users/UserDetailsDialog';
import { User } from '../../types';
import { Plus, Pencil, Trash2, Eye } from 'lucide-react';

const UsersListPage = () => {
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [isDetailsOpen, setIsDetailsOpen] = useState(false);
  const [selectedUser, setSelectedUser] = useState<User | undefined>();
  const [userToView, setUserToView] = useState<User | null>(null);
  const [userToDelete, setUserToDelete] = useState<User | null>(null);
  const queryClient = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ['users'],
    queryFn: () => userService.list({ page: 1, page_size: 50 }),
  });

  const deleteMutation = useMutation({
    mutationFn: (userId: string) => userService.delete(userId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
      setUserToDelete(null);
    },
  });

  const handleCreateUser = () => {
    setSelectedUser(undefined);
    setIsFormOpen(true);
  };

  const handleViewUser = (user: User) => {
    setUserToView(user);
    setIsDetailsOpen(true);
  };

  const handleEditUser = (user: User) => {
    setSelectedUser(user);
    setIsFormOpen(true);
  };

  const handleDeleteClick = (user: User) => {
    setUserToDelete(user);
  };

  const handleConfirmDelete = () => {
    if (userToDelete) {
      deleteMutation.mutate(userToDelete.id);
    }
  };

  const getRoleLabel = (role: string) => {
    const roleLabels: Record<string, string> = {
      ADMIN: 'Administrateur',
      RESPONSABLE_LOGISTIQUE: 'Responsable Logistique',
      OPERATEUR_USINE: 'Opérateur Usine',
      CHAUFFEUR: 'Chauffeur',
      GROSSISTE: 'Grossiste',
    };
    return roleLabels[role] || role;
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold">Utilisateurs</h1>
          <p className="text-muted-foreground">Gérer les utilisateurs du système</p>
        </div>
        <Button onClick={handleCreateUser}>
          <Plus className="h-4 w-4 mr-2" />
          Nouvel utilisateur
        </Button>
      </div>

      <Card>
        {isLoading ? (
          <div className="p-8 text-center">Chargement...</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b">
                  <th className="px-4 py-3 text-left text-sm font-medium">Nom</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">Email</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">Téléphone</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">Entreprise</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">Rôle</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">Statut</th>
                  <th className="px-4 py-3 text-right text-sm font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {data?.items.map((user) => (
                  <tr key={user.id} className="border-b hover:bg-accent/50">
                    <td className="px-4 py-3 font-medium">
                      {user.first_name} {user.last_name}
                    </td>
                    <td className="px-4 py-3 text-sm">{user.email}</td>
                    <td className="px-4 py-3 text-sm">
                      {user.phone_number || '-'}
                    </td>
                    <td className="px-4 py-3 text-sm">
                      {user.company_name || '-'}
                    </td>
                    <td className="px-4 py-3">
                      <span className="inline-flex px-2 py-1 text-xs font-semibold rounded bg-blue-100 text-blue-800">
                        {getRoleLabel(user.role)}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex flex-col gap-1">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded ${
                          user.is_active
                            ? 'bg-green-100 text-green-800'
                            : 'bg-gray-100 text-gray-800'
                        }`}>
                          {user.is_active ? 'Actif' : 'Inactif'}
                        </span>
                        {user.is_verified && (
                          <span className="inline-flex px-2 py-1 text-xs font-semibold rounded bg-blue-100 text-blue-800">
                            Vérifié
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex justify-end space-x-2">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleViewUser(user)}
                          title="Voir les détails"
                        >
                          <Eye className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleEditUser(user)}
                          title="Modifier"
                        >
                          <Pencil className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleDeleteClick(user)}
                          title="Supprimer"
                          className="text-red-600 hover:text-red-700 hover:bg-red-50"
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>

      <UserFormDialog
        isOpen={isFormOpen}
        onClose={() => setIsFormOpen(false)}
        user={selectedUser}
      />

      <UserDetailsDialog
        isOpen={isDetailsOpen}
        onClose={() => setIsDetailsOpen(false)}
        user={userToView}
      />

      <ConfirmDialog
        isOpen={!!userToDelete}
        onClose={() => setUserToDelete(null)}
        onConfirm={handleConfirmDelete}
        title="Confirmer la suppression"
        message={`Êtes-vous sûr de vouloir supprimer l'utilisateur "${userToDelete?.first_name} ${userToDelete?.last_name}" ? Cette action désactivera le compte de l'utilisateur.`}
        confirmText="Supprimer"
        variant="danger"
        isLoading={deleteMutation.isPending}
      />
    </div>
  );
};

export default UsersListPage;
