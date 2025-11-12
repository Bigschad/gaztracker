import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { contactService, partnerService } from '../../services/api';
import { Card, CardHeader, CardTitle, CardContent, Button } from '../../components/common';
import { ArrowLeft, Edit } from 'lucide-react';
import { formatDate } from '../../utils/formatters';

const ContactDetailsPage = () => {
  const { id } = useParams<{ id: string }>();

  const { data: contact, isLoading } = useQuery({
    queryKey: ['contact', id],
    queryFn: () => contactService.getById(id!),
    enabled: !!id,
  });

  const { data: partner } = useQuery({
    queryKey: ['partner', contact?.partner_id],
    queryFn: () => partnerService.getById(contact!.partner_id),
    enabled: !!contact?.partner_id,
  });


  if (isLoading) {
    return <div className="p-8 text-center">Chargement...</div>;
  }

  if (!contact) {
    return <div className="p-8 text-center text-red-600">Contact introuvable</div>;
  }

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <div>
          <Link to="/contacts">
            <Button variant="ghost" size="sm">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Retour
            </Button>
          </Link>
          <h1 className="text-3xl font-bold mt-4">
            {contact.first_name} {contact.last_name}
          </h1>
        </div>
        <Link to={`/contacts/${id}/edit`}>
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
              <p className="text-sm text-muted-foreground">Nom complet</p>
              <p className="font-semibold">
                {contact.first_name} {contact.last_name}
              </p>
            </div>
            {contact.position && (
              <div>
                <p className="text-sm text-muted-foreground">Poste</p>
                <p className="font-semibold">{contact.position}</p>
              </div>
            )}
            <div>
              <p className="text-sm text-muted-foreground">Partenaire</p>
              {partner ? (
                <Link to={`/partners/${contact.partner_id}`} className="text-blue-600 hover:underline">
                  <p className="font-semibold">{partner.name}</p>
                </Link>
              ) : (
                <p className="font-semibold">{contact.partner_id}</p>
              )}
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Contact principal</p>
              {contact.is_primary ? (
                <span className="inline-flex px-2 py-1 text-xs font-semibold rounded bg-blue-100 text-blue-800">
                  Oui
                </span>
              ) : (
                <span className="text-sm text-gray-400">Non</span>
              )}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Coordonnées</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {contact.email && (
              <div>
                <p className="text-sm text-muted-foreground">Email</p>
                <p className="font-semibold">{contact.email}</p>
              </div>
            )}
            {contact.phone && (
              <div>
                <p className="text-sm text-muted-foreground">Téléphone</p>
                <p className="font-semibold">{contact.phone}</p>
              </div>
            )}
            <div>
              <p className="text-sm text-muted-foreground">Date de création</p>
              <p className="font-semibold">{formatDate(contact.created_at)}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Dernière mise à jour</p>
              <p className="font-semibold">{formatDate(contact.updated_at)}</p>
            </div>
            {contact.notes && (
              <div>
                <p className="text-sm text-muted-foreground">Notes</p>
                <p className="text-sm">{contact.notes}</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default ContactDetailsPage;

