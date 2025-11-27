import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Card, CardContent, Button, Tabs } from '../../components/common';
import { bonEnlevementService, centreRemplisseurService, partnerService, depotService } from '../../services/api';
import { BonEnlevementCreate } from '../../types';
import { ArrowLeft } from 'lucide-react';

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type AnyItem = any;

const CreateBonEnlevementPage = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState('entities');

  const [formData, setFormData] = useState<Partial<BonEnlevementCreate>>({
    centre_remplisseur_id: '',
    grossiste_id: '',
    vehicule_immatriculation: '',
    chauffeur_nom: '',
    chauffeur_societe: '',
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
    mutationFn: bonEnlevementService.create,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['bons-enlevement'] });
      alert('Bon d\'enlèvement créé avec succès');
      navigate(`/bons-enlevement/${data.id}`);
    },
    onError: (error: any) => {
      alert(error.response?.data?.detail || 'Erreur lors de la création');
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.centre_remplisseur_id || !formData.grossiste_id || 
        !formData.vehicule_immatriculation || !formData.chauffeur_nom) {
      alert('Veuillez remplir tous les champs obligatoires');
      return;
    }

    createMutation.mutate(formData as BonEnlevementCreate);
  };

  const tabs = [
    {
      id: 'entities',
      label: 'Entités',
      content: (
        <div className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <div>
              <label className="block text-sm font-medium mb-2">Centre Remplisseur *</label>
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
              <label className="block text-sm font-medium mb-2">Dépôt Principal (optionnel)</label>
              <select
                value={formData.depot_principal_id || ''}
                onChange={(e) => setFormData({ ...formData, depot_principal_id: e.target.value || undefined })}
                className="w-full px-3 py-2 border rounded-lg"
              >
                <option value="">Aucun</option>
                {depots?.map((depot: AnyItem) => (
                  <option key={depot.id} value={depot.id}>{depot.name} ({depot.code})</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Référence (optionnelle)</label>
              <input
                type="text"
                value={formData.reference || ''}
                onChange={(e) => setFormData({ ...formData, reference: e.target.value })}
                className="w-full px-3 py-2 border rounded-lg"
                placeholder="REF-2024-001"
              />
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
              <label className="block text-sm font-medium mb-2">Nom du chauffeur *</label>
              <input
                type="text"
                value={formData.chauffeur_nom}
                onChange={(e) => setFormData({ ...formData, chauffeur_nom: e.target.value })}
                className="w-full px-3 py-2 border rounded-lg"
                placeholder="Jean Dupont"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Société du chauffeur</label>
              <input
                type="text"
                value={formData.chauffeur_societe}
                onChange={(e) => setFormData({ ...formData, chauffeur_societe: e.target.value })}
                className="w-full px-3 py-2 border rounded-lg"
                placeholder="Transport Express"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Téléphone du chauffeur</label>
              <input
                type="text"
                value={formData.chauffeur_phone || ''}
                onChange={(e) => setFormData({ ...formData, chauffeur_phone: e.target.value })}
                className="w-full px-3 py-2 border rounded-lg"
                placeholder="+225 07 00 00 00 00"
              />
            </div>
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
        <Button variant="secondary" onClick={() => navigate('/bons-enlevement')}>
          <ArrowLeft className="h-4 w-4 mr-2" />
          Retour
        </Button>
        <div>
          <h1 className="text-3xl font-bold">Nouveau Bon d'Enlèvement</h1>
          <p className="text-gray-600">Créer un nouveau bon pour une livraison</p>
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
                  onClick={() => navigate('/bons-enlevement')}
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

export default CreateBonEnlevementPage;
