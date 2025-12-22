import { useState, useEffect } from 'react';
import { useNavigate, useParams, Link } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Card, CardContent, Button, Tabs } from '../../components/common';
import { bonEnlevementService } from '../../services/api';
import { BonEnlevementUpdate, BonEnlevementStatus } from '../../types';
import { ArrowLeft } from 'lucide-react';

const EditBonEnlevementPage = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState('transport');

  // Fetch bon data
  const { data: bon, isLoading } = useQuery({
    queryKey: ['bon-enlevement', id],
    queryFn: () => bonEnlevementService.getById(id!),
    enabled: !!id,
  });

  const [formData, setFormData] = useState<Partial<BonEnlevementUpdate>>({
    reference: '',
    vehicule_immatriculation: '',
    chauffeur_nom: '',
    chauffeur_societe: '',
    chauffeur_phone: '',
    date_heure_livraison: '',
    observations: '',
    instructions_livraison: '',
  });

  // Load bon data into form
  useEffect(() => {
    if (bon) {
      // Check if bon can be edited
      if (bon.status !== BonEnlevementStatus.CREATION) {
        // Redirect to details page if not editable
        navigate(`/bons-enlevement/${id}`);
        return;
      }

      // Format date_heure_livraison for datetime-local input
      let dateTimeLocal = '';
      if (bon.date_heure_livraison) {
        const date = new Date(bon.date_heure_livraison);
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        const hours = String(date.getHours()).padStart(2, '0');
        const minutes = String(date.getMinutes()).padStart(2, '0');
        dateTimeLocal = `${year}-${month}-${day}T${hours}:${minutes}`;
      }

      setFormData({
        reference: bon.reference || '',
        vehicule_immatriculation: bon.vehicule_immatriculation || '',
        chauffeur_nom: bon.chauffeur_nom || '',
        chauffeur_societe: bon.chauffeur_societe || '',
        chauffeur_phone: bon.chauffeur_phone || '',
        date_heure_livraison: dateTimeLocal,
        observations: bon.observations || '',
        instructions_livraison: bon.instructions_livraison || '',
      });
    }
  }, [bon, id, navigate]);

  const updateMutation = useMutation({
    mutationFn: (data: BonEnlevementUpdate) => {
      // Convert datetime-local to ISO string
      const updateData: BonEnlevementUpdate = { ...data };
      if (updateData.date_heure_livraison) {
        const date = new Date(updateData.date_heure_livraison);
        updateData.date_heure_livraison = date.toISOString();
      }
      return bonEnlevementService.update(id!, updateData);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['bon-enlevement', id] });
      queryClient.invalidateQueries({ queryKey: ['bons-enlevement'] });
      navigate(`/bons-enlevement/${id}`);
    },
    onError: (error: any) => {
      console.error('Error updating bon:', error);
      const errorMessage = error.response?.data?.detail || error.message || 'Erreur lors de la modification du bon';
      alert(errorMessage);
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    updateMutation.mutate(formData as BonEnlevementUpdate);
  };

  if (isLoading) {
    return <div className="p-8 text-center">Chargement...</div>;
  }

  if (!bon) {
    return <div className="p-8 text-center">Bon d'enlèvement non trouvé</div>;
  }

  if (bon.status !== BonEnlevementStatus.CREATION) {
    return (
      <div className="p-8 text-center">
        <p className="text-red-600 mb-4">Ce bon d'enlèvement ne peut pas être modifié (statut: {bon.status})</p>
        <Link to={`/bons-enlevement/${id}`}>
          <Button>Retour aux détails</Button>
        </Link>
      </div>
    );
  }

  const tabs = [
    {
      id: 'transport',
      label: 'Transport',
      content: (
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">Immatriculation du véhicule</label>
            <input
              type="text"
              value={formData.vehicule_immatriculation || ''}
              onChange={(e) => setFormData({ ...formData, vehicule_immatriculation: e.target.value })}
              className="w-full px-3 py-2 border rounded-lg"
              placeholder="Ex: AB-123-CD"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Nom du chauffeur</label>
            <input
              type="text"
              value={formData.chauffeur_nom || ''}
              onChange={(e) => setFormData({ ...formData, chauffeur_nom: e.target.value })}
              className="w-full px-3 py-2 border rounded-lg"
              placeholder="Nom complet du chauffeur"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Société du chauffeur</label>
            <input
              type="text"
              value={formData.chauffeur_societe || ''}
              onChange={(e) => setFormData({ ...formData, chauffeur_societe: e.target.value })}
              className="w-full px-3 py-2 border rounded-lg"
              placeholder="Nom de la société de transport"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Téléphone du chauffeur</label>
            <input
              type="tel"
              value={formData.chauffeur_phone || ''}
              onChange={(e) => setFormData({ ...formData, chauffeur_phone: e.target.value })}
              className="w-full px-3 py-2 border rounded-lg"
              placeholder="Ex: +225 07 00 00 00 00"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Date et heure de livraison</label>
            <input
              type="datetime-local"
              value={formData.date_heure_livraison || ''}
              onChange={(e) => setFormData({ ...formData, date_heure_livraison: e.target.value })}
              className="w-full px-3 py-2 border rounded-lg"
            />
          </div>
        </div>
      ),
    },
    {
      id: 'notes',
      label: 'Notes & Observations',
      content: (
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">Référence</label>
            <input
              type="text"
              value={formData.reference || ''}
              onChange={(e) => setFormData({ ...formData, reference: e.target.value })}
              className="w-full px-3 py-2 border rounded-lg"
              placeholder="Référence optionnelle"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Instructions de livraison</label>
            <textarea
              value={formData.instructions_livraison || ''}
              onChange={(e) => setFormData({ ...formData, instructions_livraison: e.target.value })}
              className="w-full px-3 py-2 border rounded-lg"
              rows={4}
              placeholder="Instructions spéciales pour la livraison..."
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Observations</label>
            <textarea
              value={formData.observations || ''}
              onChange={(e) => setFormData({ ...formData, observations: e.target.value })}
              className="w-full px-3 py-2 border rounded-lg"
              rows={4}
              placeholder="Observations diverses..."
            />
          </div>
        </div>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Link to={`/bons-enlevement/${id}`}>
          <Button variant="secondary">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Retour
          </Button>
        </Link>
        <div>
          <h1 className="text-3xl font-bold">Modifier le Bon d'Enlèvement {bon.numero_bon}</h1>
          <p className="text-gray-600">Modifier les informations du bon d'enlèvement</p>
        </div>
      </div>

      {/* Form */}
      <form onSubmit={handleSubmit}>
        <div className="space-y-6">
          {/* Main form section */}
          <Card>
            <CardContent>
              <div className="space-y-6">
                <div>
                  <h2 className="text-xl font-semibold mb-4">Informations modifiables</h2>
                  <p className="text-sm text-muted-foreground mb-4">
                    Seuls certains champs peuvent être modifiés lorsque le bon est en statut "Création".
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Additional sections with tabs */}
          <Card>
            <CardContent>
              <div className="space-y-6">
                <Tabs tabs={tabs} activeTab={activeTab} onTabChange={setActiveTab} />
              </div>
            </CardContent>
          </Card>

          {/* Actions */}
          <div className="flex justify-end gap-4">
            <Link to={`/bons-enlevement/${id}`}>
              <Button
                type="button"
                variant="secondary"
                disabled={updateMutation.isPending}
              >
                Annuler
              </Button>
            </Link>
            <Button type="submit" disabled={updateMutation.isPending}>
              {updateMutation.isPending ? 'Enregistrement...' : 'Enregistrer les modifications'}
            </Button>
          </div>
        </div>
      </form>
    </div>
  );
};

export default EditBonEnlevementPage;
