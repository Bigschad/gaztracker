import { useQuery } from '@tanstack/react-query';
import { userService } from '../../services/api';
import { Card } from '../../components/common';
import { formatDate } from '../../utils/formatters';

const UsersListPage = () => {
  const { data, isLoading } = useQuery({
    queryKey: ['users'],
    queryFn: () => userService.list({ page: 1, page_size: 50 }),
  });

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-3xl font-bold">Utilisateurs</h1>
        <p className="text-muted-foreground">Gérer les utilisateurs du système</p>
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
                  <th className="px-4 py-3 text-left text-sm font-medium">Rôle</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">Statut</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">Dernière connexion</th>
                </tr>
              </thead>
              <tbody>
                {data?.items.map((user) => (
                  <tr key={user.id} className="border-b hover:bg-accent/50">
                    <td className="px-4 py-3 font-medium">{user.full_name}</td>
                    <td className="px-4 py-3 text-sm">{user.email}</td>
                    <td className="px-4 py-3">
                      <span className="inline-flex px-2 py-1 text-xs font-semibold rounded bg-blue-100 text-blue-800">
                        {user.role}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded ${
                        user.is_active
                          ? 'bg-green-100 text-green-800'
                          : 'bg-gray-100 text-gray-800'
                      }`}>
                        {user.is_active ? 'Actif' : 'Inactif'}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm">{formatDate(user.last_login)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </div>
  );
};

export default UsersListPage;
