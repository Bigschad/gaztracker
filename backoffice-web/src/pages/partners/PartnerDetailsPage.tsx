import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { partnerService, contactService } from '../../services/api';
import { Card, CardHeader, CardTitle, CardContent, Button } from '../../components/common';
import { ArrowLeft, Edit, Plus } from 'lucide-react';
import { formatDate } from '../../utils/formatters';
import { PartnerType } from '../../types';

const PartnerDetailsPage = () => {
  const { id } = useParams<{ id: string }>();

  const { data: partner, isLoading } = useQuery({
    queryKey: ['partner', id],
    queryFn: () => partnerService.getById(id!),
    enabled: !!id,
  });

  const { data: contacts } = useQuery({
    queryKey: ['contacts', 'partner', id],
    queryFn: () => contactService.list({ partner_id: id!, page: 1, page_size: 100 }),
    enabled: !!id,
  });

  const getTypeLabel = (type: PartnerType) => {
    const labels: Record<PartnerType, string> = {
      GROSSISTE: 'Grossiste',
      DISTRIBUTEUR: 'Distributeur',
      TRANSPORTEUR: 'Transporteur',
      AUTRE: 'Autre',
    };
    return labels[type] || type;
  };

  if (isLoading) {
    return <div className="p-8 text-center">Chargement...</div>;
  }

  if (!partner) {
    return <div className="p-8 text-center text-red-600">Partenaire introuvable</div>;
  }

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <div>
          <Link to="/partners">
            <Button variant="ghost" size="sm">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Retour
            </Button>
          </Link>
          <h1 className="text-3xl font-bold mt-4">{partner.name}</h1>
        </div>
        <Link to={`/partners/${id}/edit`}>
          <Button>
            <Edit className="h-4 w-4 mr-2" />
            Modifier
          </Button>
        </Link>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Informations générales</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div>
              <p className="text-sm text-muted-foreground">Nom</p>
              <p className="font-semibold">{partner.name}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Type</p>
              <span className="inline-flex px-2 py-1 text-xs font-semibold rounded bg-blue-100 text-blue-800">
                {getTypeLabel(partner.type)}
              </span>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Statut</p>
              <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded ${
                partner.is_active
                  ? 'bg-green-100 text-green-800'
                  : 'bg-gray-100 text-gray-800'
              }`}>
                {partner.is_active ? 'Actif' : 'Inactif'}
              </span>
            </div>
            {partner.address && (
              <div>
                <p className="text-sm text-muted-foreground">Adresse</p>
                <p className="font-semibold">{partner.address}</p>
              </div>
            )}
            {(partner.city || partner.postal_code) && (
              <div>
                <p className="text-sm text-muted-foreground">Ville / Code postal</p>
                <p className="font-semibold">
                  {partner.city || ''} {partner.postal_code || ''}
                </p>
              </div>
            )}
            {partner.country && (
              <div>
                <p className="text-sm text-muted-foreground">Pays</p>
                <p className="font-semibold">{partner.country}</p>
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Coordonnées</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {partner.email && (
              <div>
                <p className="text-sm text-muted-foreground">Email</p>
                <p className="font-semibold">{partner.email}</p>
              </div>
            )}
            {partner.phone && (
              <div>
                <p className="text-sm text-muted-foreground">Téléphone</p>
                <p className="font-semibold">{partner.phone}</p>
              </div>
            )}
            <div>
              <p className="text-sm text-muted-foreground">Date de création</p>
              <p className="font-semibold">{formatDate(partner.created_at)}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Dernière mise à jour</p>
              <p className="font-semibold">{formatDate(partner.updated_at)}</p>
            </div>
            {partner.notes && (
              <div>
                <p className="text-sm text-muted-foreground">Notes</p>
                <p className="text-sm">{partner.notes}</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Contacts Section */}
      <Card className="mt-6">
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Contacts</CardTitle>
          <Link to={`/contacts/new?partner_id=${id}`}>
            <Button size="sm">
              <Plus className="h-4 w-4 mr-2" />
              Ajouter un contact
            </Button>
          </Link>
        </CardHeader>
        <CardContent>
          {contacts && contacts.items && contacts.items.length > 0 ? (
            <div className="space-y-2">
              {contacts.items.map((contact) => (
                <div key={contact.id} className="flex items-center justify-between p-3 border rounded">
                  <div>
                    <p className="font-semibold">
                      {contact.first_name} {contact.last_name}
                      {contact.is_primary && (
                        <span className="ml-2 text-xs px-2 py-0.5 rounded bg-blue-100 text-blue-800">
                          Principal
                        </span>
                      )}
                    </p>
                    {contact.position && (
                      <p className="text-sm text-muted-foreground">{contact.position}</p>
                    )}
                    <div className="flex gap-4 mt-1 text-sm">
                      {contact.email && <span>{contact.email}</span>}
                      {contact.phone && <span>{contact.phone}</span>}
                    </div>
                  </div>
                  <Link to={`/contacts/${contact.id}`}>
                    <Button variant="ghost" size="sm">
                      Voir
                    </Button>
                  </Link>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-muted-foreground">
              Aucun contact enregistré
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default PartnerDetailsPage;

