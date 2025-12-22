import { Dialog } from '../common';
import { User, UserRole } from '../../types';
import { formatDate } from '../../utils/formatters';

interface UserDetailsDialogProps {
  isOpen: boolean;
  onClose: () => void;
  user: User | null;
}

const getRoleLabel = (role: UserRole): string => {
  const roleLabels: Partial<Record<UserRole, string>> = {
    [UserRole.ADMIN]: 'Administrateur',
    [UserRole.RESPONSABLE_LOGISTIQUE]: 'Responsable Logistique',
    [UserRole.OPERATEUR_USINE]: 'Opérateur Usine',
    [UserRole.CHAUFFEUR]: 'Chauffeur',
  };
  return roleLabels[role] || role;
};

export const UserDetailsDialog = ({ isOpen, onClose, user }: UserDetailsDialogProps) => {
  if (!user) return null;

  return (
    <Dialog isOpen={isOpen} onClose={onClose} title="Détails de l'utilisateur" size="lg">
      <div className="space-y-6">
        {/* Header avec nom et statut */}
        <div className="flex items-start justify-between">
          <div>
            <h3 className="text-2xl font-bold text-gray-900">
              {user.first_name} {user.last_name}
            </h3>
            <p className="text-sm text-gray-500 mt-1">{user.email}</p>
          </div>
          <div className="flex flex-col gap-2">
            <span
              className={`inline-flex px-3 py-1 text-xs font-semibold rounded-full ${
                user.is_active
                  ? 'bg-green-100 text-green-800'
                  : 'bg-gray-100 text-gray-800'
              }`}
            >
              {user.is_active ? 'Actif' : 'Inactif'}
            </span>
            {user.is_verified && (
              <span className="inline-flex px-3 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800">
                Vérifié
              </span>
            )}
          </div>
        </div>

        {/* Informations personnelles */}
        <div>
          <h4 className="text-lg font-semibold text-gray-900 mb-4">
            Informations personnelles
          </h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-500 mb-1">
                Prénom
              </label>
              <p className="text-base text-gray-900">{user.first_name}</p>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-500 mb-1">
                Nom
              </label>
              <p className="text-base text-gray-900">{user.last_name}</p>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-500 mb-1">
                Email
              </label>
              <p className="text-base text-gray-900">{user.email}</p>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-500 mb-1">
                Téléphone
              </label>
              <p className="text-base text-gray-900">
                {user.phone_number || '-'}
              </p>
            </div>
            {user.company_name && (
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-500 mb-1">
                  Entreprise
                </label>
                <p className="text-base text-gray-900">{user.company_name}</p>
              </div>
            )}
          </div>
        </div>

        {/* Informations de compte */}
        <div>
          <h4 className="text-lg font-semibold text-gray-900 mb-4">
            Informations de compte
          </h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-500 mb-1">
                Rôle
              </label>
              <span className="inline-flex px-3 py-1 text-sm font-semibold rounded-md bg-blue-100 text-blue-800">
                {getRoleLabel(user.role)}
              </span>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-500 mb-1">
                ID Utilisateur
              </label>
              <p className="text-sm text-gray-900 font-mono">{user.id}</p>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-500 mb-1">
                Date de création
              </label>
              <p className="text-base text-gray-900">
                {formatDate(user.created_at)}
              </p>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-500 mb-1">
                Dernière modification
              </label>
              <p className="text-base text-gray-900">
                {formatDate(user.updated_at)}
              </p>
            </div>
          </div>
        </div>

        {/* Permissions et accès */}
        <div>
          <h4 className="text-lg font-semibold text-gray-900 mb-4">
            Permissions et accès
          </h4>
          <div className="space-y-2">
            <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <span className="text-sm text-gray-700">Compte actif</span>
              <span
                className={`font-medium ${
                  user.is_active ? 'text-green-600' : 'text-red-600'
                }`}
              >
                {user.is_active ? 'Oui' : 'Non'}
              </span>
            </div>
            <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <span className="text-sm text-gray-700">Email vérifié</span>
              <span
                className={`font-medium ${
                  user.is_verified ? 'text-green-600' : 'text-orange-600'
                }`}
              >
                {user.is_verified ? 'Oui' : 'Non'}
              </span>
            </div>
          </div>
        </div>
      </div>
    </Dialog>
  );
};
