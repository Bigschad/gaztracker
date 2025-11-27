import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Card, CardContent, Button, Tabs } from '../../components/common';
import { bonReceptionRetourService, centreRemplisseurService, partnerService, depotService } from '../../services/api';
import { BonReceptionRetourCreate } from '../../types';
import { ArrowLeft } from 'lucide-react';

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type AnyItem = any;

const CreateBonReceptionRetourPage = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState('documents');

  const [formData, setFormData] = useState<BonReceptionRetourCreate>({
    numero_bl: '',
    numero_reception: '',
    grossiste_id: '',
    depot_depart_id: '',
    centre_remplisseur_id: '',
    vehicule_immatriculation: '',
    transporteur_nom: '',
  });

  // Fetch data
  const { data: centres } = useQuery({
    queryKey: ['centres-remplisseurs'],
    queryFn: () => centreRemplisseurService.list({ limit: 100 }),
  });

  const { data: grossistes } = useQuery({
    queryKey: ['partners'],
    queryFn: () => partnerService.list({ page: 1, page_size: 100, type: 'GROSSISTE', is_active: true }),
  });

  const { data: depots } = useQuery({
    queryKey: ['depots'],
    queryFn: () => depotService.list({ limit: 100 }),
  });

  const createMutation = useMutation({
    mutationFn: bonReceptionRetourService.create,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['bons-reception-retour'] });
      alert('Bon de réception retour créé avec succès');
      navigate(`/bons-reception-retour/${data.id}`);
    },
    onError: (error: any) => {
      alert(error.response?.data?.detail || 'Erreur lors de la création');
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.numero_bl || !formData.numero_reception || !formData.grossiste_id ||
        !formData.depot_depart_id || !formData.centre_remplisseur_id || 
        !formData.vehicule_immatriculation || !formData.transporteur_nom) {
      alert('Veuillez remplir tous les champs obligatoires');
      return;
    }

    createMutation.mutate(formData);
  };

  const tabs = [
    {
      id: 'documents',
      label: 'Documents',
      content: (
        <div className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <div>
              <label className="block text-sm font-medium mb-2">Numéro de BL *</label>
              <input
                type="text"
                value={formData.numero_bl}
                onChange={(e) => setFormData({ ...formData, numero_bl: e.target.value })}
                className="w-full px-3 py-2 border rounded-lg"
                placeholder="BL N°75 du 13.08.25"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Numéro de Réception *</label>
              <input
                type="text"
                value={formData.numero_reception}
                onChange={(e) => setFormData({ ...formData, numero_reception: e.target.value })}
                className="w-full px-3 py-2 border rounded-lg"
                placeholder="0001320/08 MB"
                required
              />
            </div>
          </div>
        </div>
      ),
    },
    {
      id: 'entities',
      label: 'Entités',
      content: (
        <div className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <div>
              <label className="block text-sm font-medium mb-2">Grossiste *</label>
              <select
                value={formData.grossiste_id}
                onChange={(e) => setFormData({ ...formData, grossiste_id: e.target.value })}
                className="w-full px-3 py-2 border rounded-lg"
                required
              >
                <option value="">Sélectionner...</option>
                {grossistes?.items?.map((grossiste: AnyItem) => (
                  <option key={grossiste.id} value={grossiste.id}>{grossiste.name} ({grossiste.code})</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Dépôt de Départ *</label>
              <select
                value={formData.depot_depart_id}
                onChange={(e) => setFormData({ ...formData, depot_depart_id: e.target.value })}
                className="w-full px-3 py-2 border rounded-lg"
                required
              >
                <option value="">Sélectionner...</option>
                {depots?.map((depot: AnyItem) => (
                  <option key={depot.id} value={depot.id}>{depot.name} ({depot.code})</option>
                ))}
              </select>
            </div>

            <div className="md:col-span-2">
              <label className="block text-sm font-medium mb-2">Centre Remplisseur (Destination) *</label>
              <select
                value={formData.centre_remplisseur_id}
                onChange={(e) => setFormData({ ...formData, centre_remplisseur_id: e.target.value })}
                className="w-full px-3 py-2 border rounded-lg"
                required
              >
                <option value="">Sélectionner...</option>
                {centres?.map((centre: AnyItem) => (
                  <option key={centre.id} value={centre.id}>{centre.name} ({centre.code})</option>
                ))}
              </select>
            </div>
          </div>
        </div>
      ),
    },
    {
      id: 'transport',
      label: 'Transport',
      content: (
        <div className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <div>
              <label className="block text-sm font-medium mb-2">Immatriculation du véhicule *</label>
              <input
                type="text"
                value={formData.vehicule_immatriculation}
                onChange={(e) => setFormData({ ...formData, vehicule_immatriculation: e.target.value })}
                className="w-full px-3 py-2 border rounded-lg"
                placeholder="AA-1234-BB"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Nom du transporteur *</label>
              <input
                type="text"
                value={formData.transporteur_nom}
                onChange={(e) => setFormData({ ...formData, transporteur_nom: e.target.value })}
                className="w-full px-3 py-2 border rounded-lg"
                placeholder="Jean Dupont"
                required
              />
            </div>

            <div className="md:col-span-2">
              <label className="block text-sm font-medium mb-2">Société du transporteur</label>
              <input
                type="text"
                value={formData.transporteur_societe || ''}
                onChange={(e) => setFormData({ ...formData, transporteur_societe: e.target.value || undefined })}
                className="w-full px-3 py-2 border rounded-lg"
                placeholder="Transport Express"
              />
            </div>
          </div>
        </div>
      ),
    },
    {
      id: 'notes',
      label: 'Observations',
      content: (
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">Observations</label>
            <textarea
              value={formData.observations || ''}
              onChange={(e) => setFormData({ ...formData, observations: e.target.value || undefined })}
              className="w-full px-3 py-2 border rounded-lg"
              rows={6}
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
        <Button variant="secondary" onClick={() => navigate('/bons-reception-retour')}>
          <ArrowLeft className="h-4 w-4 mr-2" />
          Retour
        </Button>
        <div>
          <h1 className="text-3xl font-bold">Nouveau Bon de Réception Retour</h1>
          <p className="text-gray-600">Créer un nouveau bon pour un retour de palettes vides</p>
        </div>
      </div>

      {/* Form with Tabs */}
      <form onSubmit={handleSubmit}>
        <Card>
          <CardContent>
            <div className="space-y-6">
              <Tabs tabs={tabs} activeTab={activeTab} onTabChange={setActiveTab} />

              {/* Actions */}
              <div className="flex justify-end gap-4 border-t pt-6">
                <Button
                  type="button"
                  variant="secondary"
                  onClick={() => navigate('/bons-reception-retour')}
                  disabled={createMutation.isPending}
                >
                  Annuler
                </Button>
                <Button type="submit" disabled={createMutation.isPending}>
                  {createMutation.isPending ? 'Création...' : 'Créer le bon'}
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </form>
    </div>
  );
};

export default CreateBonReceptionRetourPage;
