import { Card, CardHeader, CardTitle, CardContent } from '../../components/common';
import { useAuth } from '../../hooks/useAuth';
import { Mail, Phone, Shield, Calendar } from 'lucide-react';
import { formatDate } from '../../utils/formatters';

const ProfilePage = () => {
  const { user } = useAuth();

  if (!user) {
    return <div>Chargement...</div>;
  }

  const getRoleLabel = (role: string) => {
    const roleLabels: Record<string, string> = {
      ADMIN: 'Administrateur Système',
      RESPONSABLE_LOGISTIQUE: 'Responsable Logistique',
      OPERATEUR_USINE: 'Opérateur Usine',
      CHAUFFEUR: 'Chauffeur',
      GROSSISTE: 'Grossiste',
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
    </div>
  );
};

export default ProfilePage;

