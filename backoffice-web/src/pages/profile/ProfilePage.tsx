import { Card, CardHeader, CardTitle, CardContent } from '../../components/common';
import { useAuth } from '../../hooks/useAuth';
import { Mail, Phone, Shield, Calendar, Building2 } from 'lucide-react';
import { formatDate } from '../../utils/formatters';
import { useQuery } from '@tanstack/react-query';
import { groupeService } from '../../services/api/groupeService';
import { centreRemplisseurService } from '../../services/api/centreRemplisseurService';
import { partnerService } from '../../services/api/partnerService';
import { UserRole } from '../../types/user';

const ProfilePage = () => {
  const { user } = useAuth();

  // Fetch data based on user role
  const { data: groupes } = useQuery({
    queryKey: ['groupes', 'user-profile'],
    queryFn: () => groupeService.list({ limit: 100, is_active: true }),
    enabled: user?.role === UserRole.ADMIN,
  });

  const { data: centres } = useQuery({
    queryKey: ['centres-remplisseurs', 'user-profile'],
    queryFn: () => centreRemplisseurService.list({ limit: 100, is_active: true }),
    enabled: user?.role === UserRole.OPERATEUR_USINE || user?.role === UserRole.RESPONSABLE_LOGISTIQUE,
  });

  const { data: partnersData } = useQuery({
    queryKey: ['partners', 'user-profile', 'transporteur'],
    queryFn: () => partnerService.list({ page: 1, page_size: 100, type: 'TRANSPORTEUR', is_active: true }),
    enabled: user?.role === UserRole.CHAUFFEUR,
  });

  if (!user) {
    return <div>Chargement...</div>;
  }

  const getRoleLabel = (role: string) => {
    const roleLabels: Record<string, string> = {
      ADMIN: 'Administrateur Système',
      RESPONSABLE_LOGISTIQUE: 'Responsable Logistique',
      OPERATEUR_USINE: 'Opérateur Usine',
      CHAUFFEUR: 'Chauffeur',
    };
    return roleLabels[role] || role;
  };

  return (
    <div className="space-y-6 max-w-4xl">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold">Mon Profil</h1>
        <p className="text-muted-foreground">Informations de votre compte</p>
      </div>

      {/* Profile Card */}
      <Card>
        <CardHeader>
          <CardTitle>Informations personnelles</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-6">
            {/* Avatar */}
            <div className="flex items-center gap-4">
              <div className="flex h-20 w-20 items-center justify-center rounded-full bg-primary text-primary-foreground text-2xl font-bold">
                {user.first_name?.[0]}{user.last_name?.[0]}
              </div>
              <div>
                <h2 className="text-2xl font-bold">
                  {user.first_name} {user.last_name}
                </h2>
                <p className="text-muted-foreground">{getRoleLabel(user.role)}</p>
              </div>
            </div>

            {/* Details */}
            <div className="grid gap-4 md:grid-cols-2">
              <div className="flex items-center gap-3 p-3 border rounded-lg">
                <Mail className="h-5 w-5 text-muted-foreground" />
                <div>
                  <p className="text-sm text-muted-foreground">Email</p>
                  <p className="font-medium">{user.email}</p>
                </div>
              </div>

              {(user as any).phone && (
                <div className="flex items-center gap-3 p-3 border rounded-lg">
                  <Phone className="h-5 w-5 text-muted-foreground" />
                  <div>
                    <p className="text-sm text-muted-foreground">Téléphone</p>
                    <p className="font-medium">{(user as any).phone}</p>
                  </div>
                </div>
              )}

              <div className="flex items-center gap-3 p-3 border rounded-lg">
                <Shield className="h-5 w-5 text-muted-foreground" />
                <div>
                  <p className="text-sm text-muted-foreground">Rôle</p>
                  <p className="font-medium">{getRoleLabel(user.role)}</p>
                </div>
              </div>

              {user.created_at && (
                <div className="flex items-center gap-3 p-3 border rounded-lg">
                  <Calendar className="h-5 w-5 text-muted-foreground" />
                  <div>
                    <p className="text-sm text-muted-foreground">Membre depuis</p>
                    <p className="font-medium">{formatDate(user.created_at)}</p>
                  </div>
                </div>
              )}
            </div>

            {/* Status */}
            <div className="flex items-center gap-2">
              <div className={`h-2 w-2 rounded-full ${user.is_active ? 'bg-green-500' : 'bg-red-500'}`} />
              <span className="text-sm text-muted-foreground">
                {user.is_active ? 'Compte actif' : 'Compte inactif'}
              </span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Security Card */}
      <Card>
        <CardHeader>
          <CardTitle>Sécurité</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center justify-between p-3 border rounded-lg">
              <div>
                <p className="font-medium">Mot de passe</p>
                <p className="text-sm text-muted-foreground">
                  Dernière modification il y a 30 jours
                </p>
              </div>
              <button className="px-4 py-2 border rounded-lg hover:bg-accent transition-colors text-sm">
                Modifier
              </button>
            </div>

            <div className="flex items-center justify-between p-3 border rounded-lg">
              <div>
                <p className="font-medium">Authentification à deux facteurs</p>
                <p className="text-sm text-muted-foreground">
                  Sécurisez votre compte avec 2FA
                </p>
              </div>
              <button className="px-4 py-2 border rounded-lg hover:bg-accent transition-colors text-sm opacity-50 cursor-not-allowed" disabled>
                À venir
              </button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Company/Enterprise Card */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Building2 className="h-5 w-5" />
            Entreprise
          </CardTitle>
        </CardHeader>
        <CardContent>
          {/* Admin: Show Groups */}
          {user.role === UserRole.ADMIN && (
            <div>
              <h3 className="font-medium mb-3">Groupes</h3>
              {groupes && groupes.length > 0 ? (
                <div className="space-y-2">
                  {groupes.map((groupe) => (
                    <div key={groupe.id} className="p-3 border rounded-lg hover:bg-accent transition-colors">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="font-medium">{groupe.name}</p>
                          <p className="text-sm text-muted-foreground">{groupe.code}</p>
                        </div>
                        <div className={`h-2 w-2 rounded-full ${groupe.is_active ? 'bg-green-500' : 'bg-gray-300'}`} />
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-muted-foreground">Aucun groupe disponible</p>
              )}
            </div>
          )}

          {/* Factory Operator & Logistics Manager: Show Filling Centers */}
          {(user.role === UserRole.OPERATEUR_USINE || user.role === UserRole.RESPONSABLE_LOGISTIQUE) && (
            <div>
              <h3 className="font-medium mb-3">Centres de Remplissage</h3>
              {centres && centres.length > 0 ? (
                <div className="space-y-2">
                  {centres.map((centre) => (
                    <div key={centre.id} className="p-3 border rounded-lg hover:bg-accent transition-colors">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="font-medium">{centre.name}</p>
                          <p className="text-sm text-muted-foreground">{centre.code} • {centre.city}</p>
                        </div>
                        <div className={`h-2 w-2 rounded-full ${centre.is_active ? 'bg-green-500' : 'bg-gray-300'}`} />
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-muted-foreground">Aucun centre de remplissage disponible</p>
              )}
            </div>
          )}

          {/* Driver: Show Transport Partners */}
          {user.role === UserRole.CHAUFFEUR && (
            <div>
              <h3 className="font-medium mb-3">Partenaires Transporteurs</h3>
              {partnersData?.items && partnersData.items.length > 0 ? (
                <div className="space-y-2">
                  {partnersData.items.map((partner) => (
                    <div key={partner.id} className="p-3 border rounded-lg hover:bg-accent transition-colors">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="font-medium">{partner.name}</p>
                          <p className="text-sm text-muted-foreground">{partner.code ? `${partner.code} • ` : ''}{partner.city || 'N/A'}</p>
                        </div>
                        <div className={`h-2 w-2 rounded-full ${partner.is_active ? 'bg-green-500' : 'bg-gray-300'}`} />
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-muted-foreground">Aucun partenaire transporteur disponible</p>
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default ProfilePage;

