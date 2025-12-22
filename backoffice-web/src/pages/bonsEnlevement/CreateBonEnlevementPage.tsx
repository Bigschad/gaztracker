import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Card, CardContent, Button, Tabs } from '../../components/common';
import { bonEnlevementService, centreRemplisseurService, partnerService, depotService, userService, paletteService, groupeService } from '../../services/api';
import { BonEnlevementCreate } from '../../types';
import { UserRole } from '../../types/user';
import { PaletteStatus } from '../../types/palette';
import { ArrowLeft } from 'lucide-react';
import { useAuth } from '../../hooks/useAuth';

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type AnyItem = any;

const CreateBonEnlevementPage = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('transport');

  // Get current date/time in local timezone for datetime-local input
  const getCurrentDateTimeLocal = () => {
    const now = new Date();
    // Format as YYYY-MM-DDTHH:mm for datetime-local input
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const day = String(now.getDate()).padStart(2, '0');
    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');
    return `${year}-${month}-${day}T${hours}:${minutes}`;
  };

  const [formData, setFormData] = useState<Partial<BonEnlevementCreate>>({
    centre_remplisseur_id: '',
    grossiste_id: '',
    vehicule_immatriculation: '',
    chauffeur_nom: '',
    chauffeur_societe: '',
    palette_ids: [],
    date_heure_livraison: new Date().toISOString(), // Default to current date/time
  });

  // Local state for selected chauffeur user ID (not part of BonEnlevementCreate)
  const [chauffeurUserId, setChauffeurUserId] = useState<string>('');
  
  // Local state for distributeur (separate from grossiste)
  const [distributeurId, setDistributeurId] = useState<string>('');

  // Fetch data
  const { data: centres } = useQuery({
    queryKey: ['centres-remplisseurs'],
    queryFn: () => centreRemplisseurService.list({ limit: 100 }),
  });

  // Get active group from user
  // For ADMIN: company_name stores groupe_id, or fetch first active groupe
  // For other roles: try to get groupe from their company_name if it's a valid UUID
  const getActiveGroupeId = () => {
    if (!user) return null;
    
    // Check if company_name is a valid UUID (groupe_id)
    if (user.company_name) {
      const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
      if (uuidRegex.test(user.company_name)) {
        return user.company_name;
      }
    }
    
    // For ADMIN, if company_name is not a valid UUID, we'll fetch the first active groupe
    if (user.role === UserRole.ADMIN) {
      // Return a special marker to indicate we need to fetch the first active groupe
      return user.company_name || 'FETCH_FIRST_ACTIVE';
    }
    
    return null;
  };

  const activeGroupeIdFromUser = getActiveGroupeId();

  // Fetch all active groupes (for ADMIN if no groupe_id is detected)
  const { data: groupesData } = useQuery({
    queryKey: ['groupes', 'active'],
    queryFn: () => groupeService.list({ limit: 100, is_active: true }),
    enabled: user?.role === UserRole.ADMIN && activeGroupeIdFromUser === 'FETCH_FIRST_ACTIVE',
  });

  // Determine the actual active groupe ID
  const activeGroupeId = activeGroupeIdFromUser === 'FETCH_FIRST_ACTIVE' 
    ? (groupesData && groupesData.length > 0 ? groupesData[0].id : null)
    : activeGroupeIdFromUser;

  // Debug: Log the active groupe detection
  useEffect(() => {
    if (user) {
      console.log('User info:', {
        role: user.role,
        company_name: user.company_name,
        activeGroupeIdFromUser: activeGroupeIdFromUser,
        activeGroupeId: activeGroupeId,
        firstGroupeId: groupesData && groupesData.length > 0 ? groupesData[0].id : null,
        isUUID: activeGroupeId ? /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(activeGroupeId) : false
      });
    }
  }, [user, activeGroupeIdFromUser, activeGroupeId, groupesData]);

  // Fetch active groupe details
  const { data: activeGroupe } = useQuery({
    queryKey: ['groupe', activeGroupeId],
    queryFn: () => groupeService.getById(activeGroupeId!),
    enabled: !!activeGroupeId && activeGroupeId !== 'FETCH_FIRST_ACTIVE',
  });

  // Fetch distributeurs filtered by active groupe
  // Allow fetching even without groupe_id to show all active distributeurs
  const { data: distributeurs, isLoading: isLoadingDistributeurs } = useQuery({
    queryKey: ['partners', 'distributeurs', activeGroupeId],
    queryFn: () => partnerService.list({ 
      page: 1, 
      page_size: 100, 
      type: 'DISTRIBUTEUR', 
      groupe_id: (activeGroupeId && activeGroupeId !== 'FETCH_FIRST_ACTIVE') ? activeGroupeId : undefined,
      is_active: true 
    }),
    enabled: true, // Always fetch, filter by groupe_id if available
  });

  // Debug: Log distributeurs data
  useEffect(() => {
    console.log('Distributeurs data:', {
      isLoading: isLoadingDistributeurs,
      hasData: !!distributeurs,
      itemsCount: distributeurs?.items?.length || 0,
      activeGroupeId: activeGroupeId,
      distributeurs: distributeurs?.items?.map((d: AnyItem) => ({ id: d.id, name: d.name, groupe: d.groupe?.name })) || []
    });
  }, [distributeurs, isLoadingDistributeurs, activeGroupeId]);


  // Fetch grossistes (partners of type GROSSISTE)
  const { data: grossistes, isLoading: isLoadingGrossistes } = useQuery({
    queryKey: ['partners', 'grossistes'],
    queryFn: () => partnerService.list({ 
      page: 1, 
      page_size: 100, 
      type: 'GROSSISTE', 
      is_active: true 
    }),
    enabled: true,
  });

  // Fetch depots filtered by grossiste (not distributeur)
  const { data: depots } = useQuery({
    queryKey: ['depots', formData.grossiste_id],
    queryFn: () => depotService.list({ 
      limit: 100,
      partner_id: formData.grossiste_id && formData.grossiste_id.trim() ? formData.grossiste_id.trim() : undefined,
      is_active: true, // Only show active depots
    }),
    enabled: !!formData.grossiste_id && formData.grossiste_id.trim() !== '', // Only fetch when grossiste is selected
  });

  // Fetch transport partners
  const { data: transporteurs } = useQuery({
    queryKey: ['partners', 'transporteur'],
    queryFn: () => partnerService.list({ page: 1, page_size: 100, type: 'TRANSPORTEUR', is_active: true }),
  });

  // Fetch chauffeurs (users with CHAUFFEUR role) filtered by selected transporteur
  const { data: chauffeursData } = useQuery({
    queryKey: ['users', 'chauffeurs', formData.chauffeur_societe],
    queryFn: () => userService.list({ page: 1, page_size: 100 }),
    enabled: true, // Always fetch, we'll filter in the component
  });

  // Fetch available palettes (CREATION or AU_CENTRE, full) filtered by selected centre remplisseur
  // Note: We fetch all palettes and filter by status in the component since the API doesn't support multiple status values
  const { data: palettesData } = useQuery({
    queryKey: ['palettes', 'available', formData.centre_remplisseur_id],
    queryFn: () => paletteService.list({ 
      page: 1, 
      page_size: 100,
      current_centre_remplisseur_id: formData.centre_remplisseur_id,
    }),
    enabled: !!formData.centre_remplisseur_id,
  });

  const createMutation = useMutation({
    mutationFn: bonEnlevementService.create,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['bons-enlevement'] });
      alert('Bon d\'enlèvement créé avec succès');
      navigate(`/bons-enlevement/${data.id}`);
      window.location.reload();
    },
    onError: (error: any) => {
      alert(error.response?.data?.detail || 'Erreur lors de la création');
    },
  });

  // Filter chauffeurs by selected transporteur
  const chauffeurs = chauffeursData?.items?.filter((user: AnyItem) => 
    user.role === UserRole.CHAUFFEUR && 
    user.is_active &&
    (!formData.chauffeur_societe || user.company_name === formData.chauffeur_societe)
  ) || [];

  // Filter available palettes (CREATION or AU_CENTRE, full, and not assigned)
  const availablePalettes = palettesData?.items?.filter((palette: AnyItem) => {
    const isAvailableStatus = palette.status === PaletteStatus.CREATION || palette.status === PaletteStatus.AU_CENTRE;
    const isFull = palette.is_full === true;
    const isNotAssigned = !palette.bon_enlevement_actuel_id; // Not already assigned to another bon
    return isAvailableStatus && isFull && isNotAssigned;
  }) || [];

  // Reset depot when grossiste changes
  useEffect(() => {
    if (!formData.grossiste_id) {
      // Clear depot if no grossiste selected
      if (formData.depot_principal_id) {
        setFormData(prev => ({ ...prev, depot_principal_id: undefined }));
      }
    } else if (formData.depot_principal_id && depots) {
      // Check if current depot still belongs to the selected grossiste
      const currentDepot = depots.find((d: AnyItem) => d.id === formData.depot_principal_id);
      if (!currentDepot || currentDepot.partner_id !== formData.grossiste_id) {
        setFormData(prev => ({ ...prev, depot_principal_id: undefined }));
      }
    }
  }, [formData.grossiste_id, formData.depot_principal_id, depots]);

  // Reset depot when distributeur changes (depot should not depend on distributeur)
  useEffect(() => {
    // Depot is now independent of distributeur, so we don't need to reset it
  }, [distributeurId]);

  // Reset chauffeur when transporteur changes
  useEffect(() => {
    if (!formData.chauffeur_societe) {
      if (chauffeurUserId || formData.chauffeur_nom || formData.chauffeur_phone) {
        setChauffeurUserId('');
        setFormData(prev => ({ 
          ...prev, 
          chauffeur_nom: '',
          chauffeur_phone: undefined 
        }));
      }
    } else if (chauffeurUserId && chauffeurs) {
      // Check if current chauffeur still belongs to the selected transporteur
      const currentChauffeur = chauffeurs.find((c: AnyItem) => c.id === chauffeurUserId);
      if (!currentChauffeur || currentChauffeur.company_name !== formData.chauffeur_societe) {
        setChauffeurUserId('');
        setFormData(prev => ({ 
          ...prev, 
          chauffeur_nom: '',
          chauffeur_phone: undefined 
        }));
      }
    }
  }, [formData.chauffeur_societe, chauffeurUserId, chauffeurs]);

  // Handle chauffeur selection - auto-fill name and phone
  const handleChauffeurChange = (userId: string) => {
    const selectedChauffeur = chauffeurs.find((c: AnyItem) => c.id === userId);
    if (selectedChauffeur) {
      setChauffeurUserId(userId);
      setFormData(prev => ({
        ...prev,
        chauffeur_nom: `${selectedChauffeur.first_name} ${selectedChauffeur.last_name}`,
        chauffeur_phone: selectedChauffeur.phone_number || undefined,
      }));
    } else {
      setChauffeurUserId('');
      setFormData(prev => ({
        ...prev,
        chauffeur_nom: '',
        chauffeur_phone: undefined,
      }));
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.centre_remplisseur_id || !distributeurId || !formData.grossiste_id || 
        !formData.depot_principal_id ||
        !formData.vehicule_immatriculation || !formData.chauffeur_nom ||
        !formData.chauffeur_societe || !formData.date_heure_livraison) {
      alert('Veuillez remplir tous les champs obligatoires');
      return;
    }

    // Prepare data for submission
    const submitData: BonEnlevementCreate = {
      ...formData,
      date_heure_livraison: formData.date_heure_livraison || new Date().toISOString(),
      palette_ids: formData.palette_ids && formData.palette_ids.length > 0 
        ? formData.palette_ids 
        : undefined,
    } as BonEnlevementCreate;

    createMutation.mutate(submitData);
  };

  // Entities section content (main form body)
  const entitiesContent = (
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
          <label className="block text-sm font-medium mb-2">
            Distributeur *
            {activeGroupe && (
              <span className="text-xs text-muted-foreground ml-2">
                (Groupe: {activeGroupe.name})
              </span>
            )}
            {distributeurs && distributeurs.items && distributeurs.items.length > 0 && (
              <span className="text-xs text-muted-foreground ml-2">
                ({distributeurs.items.length} distributeur{distributeurs.items.length > 1 ? 's' : ''} disponible{distributeurs.items.length > 1 ? 's' : ''})
              </span>
            )}
          </label>
          <select
            value={distributeurId}
            onChange={(e) => setDistributeurId(e.target.value)}
            className={`w-full px-3 py-2 border rounded-lg ${
              isLoadingDistributeurs ? 'bg-gray-50' : ''
            }`}
            required
            disabled={isLoadingDistributeurs}
          >
            <option value="">
              {isLoadingDistributeurs
                ? 'Chargement des distributeurs...'
                : (distributeurs && distributeurs.items && distributeurs.items.length === 0)
                ? (activeGroupeId 
                    ? `Aucun distributeur disponible pour le groupe ${activeGroupe?.name || ''}`
                    : 'Aucun distributeur actif disponible')
                : 'Sélectionner un distributeur...'}
            </option>
            {distributeurs?.items?.map((distributeur: AnyItem) => (
              <option key={distributeur.id} value={distributeur.id}>
                {distributeur.name}{distributeur.groupe ? ` (${distributeur.groupe.name})` : ''}
              </option>
            ))}
          </select>
          {isLoadingDistributeurs && (
            <p className="mt-1 text-xs text-muted-foreground">
              Chargement des distributeurs...
            </p>
          )}
          {!isLoadingDistributeurs && distributeurs && distributeurs.items && distributeurs.items.length === 0 && (
            <p className="mt-1 text-xs text-amber-600">
              {activeGroupeId 
                ? `Aucun distributeur actif trouvé pour le groupe ${activeGroupe?.name || ''}`
                : 'Aucun distributeur actif disponible'}
            </p>
          )}
          {!activeGroupeId && !isLoadingDistributeurs && distributeurs && distributeurs.items && distributeurs.items.length > 0 && (
            <p className="mt-1 text-xs text-blue-600">
              Affichage de tous les distributeurs actifs (aucun groupe actif dans votre session)
            </p>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">
            Grossiste *
            {grossistes && grossistes.items && grossistes.items.length > 0 && (
              <span className="text-xs text-muted-foreground ml-2">
                ({grossistes.items.length} grossiste{grossistes.items.length > 1 ? 's' : ''} disponible{grossistes.items.length > 1 ? 's' : ''})
              </span>
            )}
          </label>
          <select
            value={formData.grossiste_id}
            onChange={(e) => setFormData({ ...formData, grossiste_id: e.target.value })}
            className={`w-full px-3 py-2 border rounded-lg ${
              isLoadingGrossistes ? 'bg-gray-50' : ''
            }`}
            required
            disabled={isLoadingGrossistes}
          >
            <option value="">
              {isLoadingGrossistes
                ? 'Chargement des grossistes...'
                : (grossistes && grossistes.items && grossistes.items.length === 0)
                ? 'Aucun grossiste actif disponible'
                : 'Sélectionner un grossiste...'}
            </option>
            {grossistes?.items?.map((grossiste: AnyItem) => (
              <option key={grossiste.id} value={grossiste.id}>
                {grossiste.name}
              </option>
            ))}
          </select>
          {isLoadingGrossistes && (
            <p className="mt-1 text-xs text-muted-foreground">
              Chargement des grossistes...
            </p>
          )}
          {!isLoadingGrossistes && grossistes && grossistes.items && grossistes.items.length === 0 && (
            <p className="mt-1 text-xs text-amber-600">
              Aucun grossiste actif disponible
            </p>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">
            Dépôt *
            {formData.grossiste_id && depots && depots.length > 0 && (
              <span className="text-xs text-muted-foreground ml-2">
                ({depots.length} dépôt{depots.length > 1 ? 's' : ''} disponible{depots.length > 1 ? 's' : ''})
              </span>
            )}
          </label>
          <select
            value={formData.depot_principal_id || ''}
            onChange={(e) => setFormData({ ...formData, depot_principal_id: e.target.value || undefined })}
            className={`w-full px-3 py-2 border rounded-lg ${
              !formData.grossiste_id ? 'bg-gray-100 cursor-not-allowed' : ''
            }`}
            required
            disabled={!formData.grossiste_id}
          >
            <option value="">
              {!formData.grossiste_id 
                ? 'Sélectionnez d\'abord un grossiste' 
                : depots && depots.length === 0
                ? 'Aucun dépôt disponible pour ce grossiste'
                : 'Sélectionner un dépôt...'}
            </option>
            {depots?.map((depot: AnyItem) => (
              <option key={depot.id} value={depot.id}>
                {depot.name} ({depot.code})
                {depot.is_main_depot && ' - Principal'}
              </option>
            ))}
          </select>
          {!formData.grossiste_id && (
            <p className="mt-1 text-xs text-muted-foreground">
              Veuillez d'abord sélectionner un grossiste
            </p>
          )}
          {formData.grossiste_id && depots && depots.length === 0 && (
            <p className="mt-1 text-xs text-amber-600">
              Aucun dépôt actif trouvé pour ce grossiste
            </p>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">Référence (optionnelle)</label>
          <input
            type="text"
            value={formData.reference || ''}
            onChange={(e) => setFormData({ ...formData, reference: e.target.value })}
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                e.preventDefault(); // Prevent form submission on Enter
              }
            }}
            className="w-full px-3 py-2 border rounded-lg"
            placeholder="REF-2024-001"
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">Date et heure de livraison *</label>
          <input
            type="datetime-local"
            value={formData.date_heure_livraison 
              ? new Date(formData.date_heure_livraison).toISOString().slice(0, 16)
              : getCurrentDateTimeLocal()}
            onChange={(e) => {
              // Convert datetime-local value to ISO string
              const localDateTime = e.target.value;
              if (localDateTime) {
                const date = new Date(localDateTime);
                setFormData({ ...formData, date_heure_livraison: date.toISOString() });
              } else {
                setFormData({ ...formData, date_heure_livraison: undefined });
              }
            }}
            className="w-full px-3 py-2 border rounded-lg"
            required
          />
          <p className="mt-1 text-xs text-muted-foreground">
            Date et heure prévues pour la livraison
          </p>
        </div>
      </div>
    </div>
  );

  const tabs = [
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
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault(); // Prevent form submission on Enter
                  }
                }}
                className="w-full px-3 py-2 border rounded-lg"
                placeholder="AA-1234-BB"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Société du chauffeur (Transporteur) *</label>
              <select
                value={formData.chauffeur_societe || ''}
                onChange={(e) => {
                  setChauffeurUserId('');
                  setFormData({ 
                    ...formData, 
                    chauffeur_societe: e.target.value || undefined,
                    chauffeur_nom: '',
                    chauffeur_phone: undefined,
                  });
                }}
                className="w-full px-3 py-2 border rounded-lg"
                required
              >
                <option value="">Sélectionner un transporteur...</option>
                {transporteurs?.items?.map((transporteur: AnyItem) => (
                  <option key={transporteur.id} value={transporteur.id}>
                    {transporteur.name}{transporteur.code ? ` (${transporteur.code})` : ''}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">
                Nom du chauffeur *
                {formData.chauffeur_societe && chauffeurs && chauffeurs.length > 0 && (
                  <span className="text-xs text-muted-foreground ml-2">
                    ({chauffeurs.length} chauffeur{chauffeurs.length > 1 ? 's' : ''} disponible{chauffeurs.length > 1 ? 's' : ''})
                  </span>
                )}
              </label>
              <select
                value={chauffeurUserId || ''}
                onChange={(e) => handleChauffeurChange(e.target.value)}
                className={`w-full px-3 py-2 border rounded-lg ${
                  !formData.chauffeur_societe ? 'bg-gray-100 cursor-not-allowed' : ''
                }`}
                required
                disabled={!formData.chauffeur_societe}
              >
                <option value="">
                  {!formData.chauffeur_societe 
                    ? 'Sélectionnez d\'abord un transporteur' 
                    : chauffeurs && chauffeurs.length === 0
                    ? 'Aucun chauffeur disponible pour ce transporteur'
                    : 'Sélectionner un chauffeur...'}
                </option>
                {chauffeurs.map((chauffeur: AnyItem) => (
                  <option key={chauffeur.id} value={chauffeur.id}>
                    {chauffeur.first_name} {chauffeur.last_name}
                    {chauffeur.email ? ` (${chauffeur.email})` : ''}
                  </option>
                ))}
              </select>
              {!formData.chauffeur_societe && (
                <p className="mt-1 text-xs text-muted-foreground">
                  Veuillez d'abord sélectionner un transporteur
                </p>
              )}
              {formData.chauffeur_societe && chauffeurs && chauffeurs.length === 0 && (
                <p className="mt-1 text-xs text-amber-600">
                  Aucun chauffeur actif trouvé pour ce transporteur
                </p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Téléphone du chauffeur</label>
              <input
                type="text"
                value={formData.chauffeur_phone || ''}
                onChange={(e) => setFormData({ ...formData, chauffeur_phone: e.target.value })}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault(); // Prevent form submission on Enter
                  }
                }}
                className="w-full px-3 py-2 border rounded-lg bg-gray-50"
                placeholder="+225 07 00 00 00 00"
                readOnly
              />
              <p className="mt-1 text-xs text-muted-foreground">
                Rempli automatiquement à partir du profil du chauffeur
              </p>
            </div>
          </div>
        </div>
      ),
    },
    {
      id: 'palettes',
      label: 'Palettes',
      content: (
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">
              Palettes disponibles
              {formData.centre_remplisseur_id && availablePalettes && (
                <span className="text-xs text-muted-foreground ml-2">
                  ({availablePalettes.length} palette{availablePalettes.length > 1 ? 's' : ''} disponible{availablePalettes.length > 1 ? 's' : ''})
                </span>
              )}
            </label>
            {!formData.centre_remplisseur_id ? (
              <p className="text-sm text-muted-foreground">
                Veuillez d'abord sélectionner un centre remplisseur dans la section principale ci-dessus
              </p>
            ) : palettesData && palettesData.items && palettesData.items.length === 0 ? (
              <p className="text-sm text-amber-600">
                Aucune palette avec le statut "AU_CENTRE" trouvée au centre remplisseur sélectionné
              </p>
            ) : availablePalettes.length === 0 && palettesData && palettesData.items && palettesData.items.length > 0 ? (
              <div className="text-sm text-amber-600 space-y-1">
                <p>Aucune palette disponible (pleine et non assignée) au centre remplisseur sélectionné.</p>
                <p className="text-xs text-muted-foreground">
                  {palettesData.items.length} palette(s) trouvée(s) mais aucune ne répond aux critères :
                  <ul className="list-disc list-inside mt-1">
                    <li>Statut: CREATION ou AU_CENTRE</li>
                    <li>Pleine (is_full = true)</li>
                    <li>Non assignée à un autre bon d'enlèvement</li>
                  </ul>
                </p>
              </div>
            ) : availablePalettes.length === 0 ? (
              <p className="text-sm text-amber-600">
                Aucune palette disponible au centre remplisseur sélectionné
              </p>
            ) : (
              <div className="border rounded-lg p-4 max-h-96 overflow-y-auto">
                <div className="space-y-2">
                  {availablePalettes.map((palette: AnyItem) => (
                    <label
                      key={palette.id}
                      className="flex items-center space-x-3 p-3 border rounded-lg hover:bg-accent cursor-pointer"
                      onClick={(e) => {
                        // Prevent form submission when clicking on label
                        if (e.target !== e.currentTarget) {
                          e.preventDefault();
                        }
                      }}
                    >
                      <input
                        type="checkbox"
                        checked={formData.palette_ids?.includes(palette.id) || false}
                        onChange={(e) => {
                          e.stopPropagation(); // Prevent event bubbling
                          const currentIds = formData.palette_ids || [];
                          if (e.target.checked) {
                            setFormData({
                              ...formData,
                              palette_ids: [...currentIds, palette.id],
                            });
                          } else {
                            setFormData({
                              ...formData,
                              palette_ids: currentIds.filter((id: string) => id !== palette.id),
                            });
                          }
                        }}
                        onClick={(e) => e.stopPropagation()} // Prevent form submission on click
                        className="h-4 w-4 text-blue-600 rounded focus:ring-blue-500"
                      />
                      <div className="flex-1">
                        <div className="flex items-center justify-between">
                          <span className="font-medium">
                            {palette.reference_code || palette.serial_number}
                          </span>
                          <span className="text-xs px-2 py-1 rounded bg-blue-100 text-blue-800">
                            {palette.type}
                          </span>
                        </div>
                        {palette.rfid_tag && (
                          <p className="text-xs text-muted-foreground mt-1">
                            RFID: {palette.rfid_tag.tag_number}
                          </p>
                        )}
                      </div>
                    </label>
                  ))}
                </div>
              </div>
            )}
            {formData.palette_ids && formData.palette_ids.length > 0 && (
              <p className="mt-2 text-sm text-green-600">
                {formData.palette_ids.length} palette{formData.palette_ids.length > 1 ? 's' : ''} sélectionnée{formData.palette_ids.length > 1 ? 's' : ''}
              </p>
            )}
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
              onKeyDown={(e) => {
                if (e.key === 'Enter' && e.ctrlKey) {
                  // Allow Ctrl+Enter to submit, but prevent simple Enter
                  return;
                }
                if (e.key === 'Enter') {
                  e.preventDefault(); // Prevent form submission on Enter
                }
              }}
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
              onKeyDown={(e) => {
                if (e.key === 'Enter' && e.ctrlKey) {
                  // Allow Ctrl+Enter to submit, but prevent simple Enter
                  return;
                }
                if (e.key === 'Enter') {
                  e.preventDefault(); // Prevent form submission on Enter
                }
              }}
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

      {/* Form */}
      <form onSubmit={handleSubmit}>
        <div className="space-y-6">
          {/* Main form section - Entities */}
          <Card>
            <CardContent>
              <div className="space-y-6">
                <div>
                  <h2 className="text-xl font-semibold mb-4">Informations principales</h2>
                  {entitiesContent}
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
      </form>
    </div>
  );
};

export default CreateBonEnlevementPage;
