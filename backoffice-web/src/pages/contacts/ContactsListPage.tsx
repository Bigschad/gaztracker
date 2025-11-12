import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Link, useSearchParams } from 'react-router-dom';
import { contactService, partnerService } from '../../services/api';
import { Card, CardContent, Button, ConfirmDialog } from '../../components/common';
import { Plus, Eye, Edit, Trash2 } from 'lucide-react';
import { formatDate } from '../../utils/formatters';

const ContactsListPage = () => {
  const [page, setPage] = useState(1);
  const [deleteContactId, setDeleteContactId] = useState<string | null>(null);
  const [searchParams] = useSearchParams();
  const partnerIdFilter = searchParams.get('partner_id') || '';
  const queryClient = useQueryClient();

  const { data, isLoading, error } = useQuery({
    queryKey: ['contacts', page, partnerIdFilter],
    queryFn: () => contactService.list({
      page,
      page_size: 20,
      partner_id: partnerIdFilter || undefined,
    }),
    retry: 1,
  });

  const { data: partnersData } = useQuery({
    queryKey: ['partners', 'all'],
    queryFn: () => partnerService.list({ page: 1, page_size: 100 }),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => contactService.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['contacts'] });
      setDeleteContactId(null);
    },
  });

  const getPartnerName = (partnerId: string) => {
    const partner = partnersData?.items.find(p => p.id === partnerId);
    return partner?.name || partnerId;
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold">Contacts</h1>
          <p className="text-muted-foreground">Gérer les contacts des partenaires</p>
        </div>
        <Link to={`/contacts/new${partnerIdFilter ? `?partner_id=${partnerIdFilter}` : ''}`}>
          <Button>
            <Plus className="h-4 w-4 mr-2" />
            Nouveau contact
          </Button>
        </Link>
      </div>

      {/* Filter */}
      {partnersData && (
        <div className="mb-4">
          <select
            value={partnerIdFilter}
            onChange={(e) => {
              const newParams = new URLSearchParams();
              if (e.target.value) {
                newParams.set('partner_id', e.target.value);
              }
              window.history.pushState({}, '', `/contacts?${newParams.toString()}`);
              setPage(1);
            }}
            className="px-3 py-2 border rounded-lg"
          >
            <option value="">Tous les partenaires</option>
            {partnersData.items.map((partner) => (
              <option key={partner.id} value={partner.id}>
                {partner.name}
              </option>
            ))}
          </select>
        </div>
      )}

      <Card>
        <CardContent className="p-0">
          {isLoading ? (
            <div className="p-8 text-center">Chargement...</div>
          ) : error ? (
            <div className="p-8 text-center">
              <div className="text-red-600 mb-2">Erreur lors du chargement des contacts</div>
              <div className="text-sm text-muted-foreground">
                {error instanceof Error ? error.message : 'Une erreur est survenue'}
              </div>
            </div>
          ) : !data || !data.items || data.items.length === 0 ? (
            <div className="p-8 text-center text-muted-foreground">
              Aucun contact trouvé
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="px-4 py-3 text-left text-sm font-medium">Nom</th>
                    <th className="px-4 py-3 text-left text-sm font-medium">Partenaire</th>
                    <th className="px-4 py-3 text-left text-sm font-medium">Poste</th>
                    <th className="px-4 py-3 text-left text-sm font-medium">Email</th>
                    <th className="px-4 py-3 text-left text-sm font-medium">Téléphone</th>
                    <th className="px-4 py-3 text-left text-sm font-medium">Principal</th>
                    <th className="px-4 py-3 text-left text-sm font-medium">Date création</th>
                    <th className="px-4 py-3 text-right text-sm font-medium">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {data.items.map((contact) => (
                    <tr key={contact.id} className="border-b hover:bg-accent/50">
                      <td className="px-4 py-3 font-medium">
                        {contact.first_name} {contact.last_name}
                      </td>
                      <td className="px-4 py-3 text-sm">
                        <Link to={`/partners/${contact.partner_id}`} className="text-blue-600 hover:underline">
                          {getPartnerName(contact.partner_id)}
                        </Link>
                      </td>
                      <td className="px-4 py-3 text-sm">{contact.position || '-'}</td>
                      <td className="px-4 py-3 text-sm">{contact.email || '-'}</td>
                      <td className="px-4 py-3 text-sm">{contact.phone || '-'}</td>
                      <td className="px-4 py-3">
                        {contact.is_primary ? (
                          <span className="inline-flex px-2 py-1 text-xs font-semibold rounded bg-blue-100 text-blue-800">
                            Oui
                          </span>
                        ) : (
                          <span className="text-sm text-gray-400">-</span>
                        )}
                      </td>
                      <td className="px-4 py-3 text-sm">{formatDate(contact.created_at)}</td>
                      <td className="px-4 py-3 text-right">
                        <div className="flex items-center justify-end space-x-1">
                          <Link to={`/contacts/${contact.id}`}>
                            <Button variant="ghost" size="sm" title="Voir les détails">
                              <Eye className="h-4 w-4" />
                            </Button>
                          </Link>
                          <Link to={`/contacts/${contact.id}/edit`}>
                            <Button variant="ghost" size="sm" title="Modifier">
                              <Edit className="h-4 w-4" />
                            </Button>
                          </Link>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => setDeleteContactId(contact.id)}
                            className="text-red-600 hover:text-red-700"
                            title="Supprimer"
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>

              {data && data.total_pages > 1 && (
                <div className="flex items-center justify-between px-4 py-3 border-t">
                  <p className="text-sm text-muted-foreground">
                    Page {data.page} sur {data.total_pages} ({data.total} résultats)
                  </p>
                  <div className="flex space-x-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setPage(p => Math.max(1, p - 1))}
                      disabled={page === 1}
                    >
                      Précédent
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setPage(p => p + 1)}
                      disabled={page >= data.total_pages}
                    >
                      Suivant
                    </Button>
                  </div>
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      <ConfirmDialog
        isOpen={!!deleteContactId}
        onClose={() => setDeleteContactId(null)}
        onConfirm={() => deleteContactId && deleteMutation.mutate(deleteContactId)}
        title="Supprimer le contact"
        message="Êtes-vous sûr de vouloir supprimer ce contact ? Cette action est irréversible."
        confirmText="Supprimer"
        cancelText="Annuler"
        variant="danger"
        isLoading={deleteMutation.isPending}
      />
    </div>
  );
};

export default ContactsListPage;

