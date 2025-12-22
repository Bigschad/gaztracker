/**
 * GAZTRACKER MOBILE - MOCK DATA
 * 
 * Données fictives pour développement mobile en mode offline.
 * À utiliser pendant que l'API backend n'est pas encore disponible.
 * 
 * Usage:
 * import { MOCK_USER, MOCK_BONS, MOCK_PALETTES, MOCK_TAGS } from './MOBILE_MOCK_DATA';
 */

// ============================================================================
// USER (CHAUFFEUR)
// ============================================================================

export const MOCK_USER = {
  id: "550e8400-e29b-41d4-a716-446655440001",
  name: "Koné Seydou",
  email: "chauffeur1@transport.ci",
  role: "CHAUFFEUR",
  phone: "+225 07 90 00 00 01",
  avatar_url: null,
  is_active: true
};

export const MOCK_LOGIN_RESPONSE = {
  access_token: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.mock_token",
  token_type: "bearer",
  expires_in: 3600,
  user: MOCK_USER
};

// ============================================================================
// TAGS RFID
// ============================================================================

export const MOCK_TAGS = [
  {
    id: "650e8400-e29b-41d4-a716-446655440001",
    tag_id: "RFID0001",
    label: "Tag Palette #0001",
    status: "ACTIVE",
    assigned_to_palette: true,
    palette_id: "750e8400-e29b-41d4-a716-446655440001",
    created_at: "2024-11-20T08:00:00Z",
    last_scanned_at: "2024-11-25T10:30:00Z"
  },
  {
    id: "650e8400-e29b-41d4-a716-446655440002",
    tag_id: "RFID0002",
    label: "Tag Palette #0002",
    status: "ACTIVE",
    assigned_to_palette: true,
    palette_id: "750e8400-e29b-41d4-a716-446655440002",
    created_at: "2024-11-20T08:05:00Z",
    last_scanned_at: "2024-11-25T09:15:00Z"
  },
  {
    id: "650e8400-e29b-41d4-a716-446655440003",
    tag_id: "RFID0003",
    label: "Tag Palette #0003",
    status: "ACTIVE",
    assigned_to_palette: true,
    palette_id: "750e8400-e29b-41d4-a716-446655440003",
    created_at: "2024-11-20T08:10:00Z",
    last_scanned_at: "2024-11-24T16:00:00Z"
  },
  {
    id: "650e8400-e29b-41d4-a716-446655440004",
    tag_id: "RFID0004",
    label: "Tag Palette #0004",
    status: "ACTIVE",
    assigned_to_palette: true,
    palette_id: "750e8400-e29b-41d4-a716-446655440004",
    created_at: "2024-11-20T08:15:00Z",
    last_scanned_at: "2024-11-25T08:00:00Z"
  },
  {
    id: "650e8400-e29b-41d4-a716-446655440005",
    tag_id: "RFID0005",
    label: "Tag Palette #0005",
    status: "ACTIVE",
    assigned_to_palette: true,
    palette_id: "750e8400-e29b-41d4-a716-446655440005",
    created_at: "2024-11-20T08:20:00Z",
    last_scanned_at: "2024-11-25T07:45:00Z"
  },
  {
    id: "650e8400-e29b-41d4-a716-446655440050",
    tag_id: "RFID0050",
    label: "Tag Palette Vide #0050",
    status: "ACTIVE",
    assigned_to_palette: true,
    palette_id: "750e8400-e29b-41d4-a716-446655440050",
    created_at: "2024-11-20T08:00:00Z",
    last_scanned_at: "2024-11-24T18:00:00Z"
  },
  {
    id: "650e8400-e29b-41d4-a716-446655440051",
    tag_id: "RFID0051",
    label: "Tag Palette Vide #0051",
    status: "ACTIVE",
    assigned_to_palette: true,
    palette_id: "750e8400-e29b-41d4-a716-446655440051",
    created_at: "2024-11-20T08:00:00Z",
    last_scanned_at: "2024-11-24T18:05:00Z"
  },
  {
    id: "650e8400-e29b-41d4-a716-446655440052",
    tag_id: "RFID0052",
    label: "Tag Palette Vide #0052",
    status: "ACTIVE",
    assigned_to_palette: true,
    palette_id: "750e8400-e29b-41d4-a716-446655440052",
    created_at: "2024-11-20T08:00:00Z",
    last_scanned_at: "2024-11-24T18:10:00Z"
  },
  {
    id: "650e8400-e29b-41d4-a716-446655449998",
    tag_id: "RFID9998",
    label: "Tag Libre #9998",
    status: "ACTIVE",
    assigned_to_palette: false,
    palette_id: null,
    created_at: "2024-11-20T08:00:00Z",
    last_scanned_at: null
  },
  {
    id: "650e8400-e29b-41d4-a716-446655449999",
    tag_id: "RFID9999",
    label: "Tag Libre #9999",
    status: "ACTIVE",
    assigned_to_palette: false,
    palette_id: null,
    created_at: "2024-11-20T08:00:00Z",
    last_scanned_at: null
  }
];

// ============================================================================
// PALETTES
// ============================================================================

export const MOCK_PALETTES = [
  // Palettes pleines au centre (disponibles pour chargement)
  {
    id: "750e8400-e29b-41d4-a716-446655440001",
    serial_number: "PAL-2025-00001",
    reference_code: "REF-0001",
    type: "B12",
    capacity: 24,
    status: "AU_CENTRE",
    is_full: true,
    rfid_tag_id: "RFID0001",
    current_location: {
      type: "CENTRE",
      name: "Centre Remplisseur Yopougon"
    },
    last_updated: "2024-11-25T10:00:00Z"
  },
  {
    id: "750e8400-e29b-41d4-a716-446655440002",
    serial_number: "PAL-2025-00002",
    reference_code: "REF-0002",
    type: "B12",
    capacity: 24,
    status: "AU_CENTRE",
    is_full: true,
    rfid_tag_id: "RFID0002",
    current_location: {
      type: "CENTRE",
      name: "Centre Remplisseur Yopougon"
    },
    last_updated: "2024-11-25T10:00:00Z"
  },
  {
    id: "750e8400-e29b-41d4-a716-446655440003",
    serial_number: "PAL-2025-00003",
    reference_code: "REF-0003",
    type: "B28",
    capacity: 12,
    status: "AU_CENTRE",
    is_full: true,
    rfid_tag_id: "RFID0003",
    current_location: {
      type: "CENTRE",
      name: "Centre Remplisseur Yopougon"
    },
    last_updated: "2024-11-25T10:00:00Z"
  },
  {
    id: "750e8400-e29b-41d4-a716-446655440004",
    serial_number: "PAL-2025-00004",
    reference_code: "REF-0004",
    type: "B6",
    capacity: 48,
    status: "AU_CENTRE",
    is_full: true,
    rfid_tag_id: "RFID0004",
    current_location: {
      type: "CENTRE",
      name: "Centre Remplisseur Yopougon"
    },
    last_updated: "2024-11-25T10:00:00Z"
  },
  {
    id: "750e8400-e29b-41d4-a716-446655440005",
    serial_number: "PAL-2025-00005",
    reference_code: "REF-0005",
    type: "B12",
    capacity: 24,
    status: "AU_CENTRE",
    is_full: true,
    rfid_tag_id: "RFID0005",
    current_location: {
      type: "CENTRE",
      name: "Centre Remplisseur Yopougon"
    },
    last_updated: "2024-11-25T10:00:00Z"
  },
  // Palettes vides au dépôt (pour collecte)
  {
    id: "750e8400-e29b-41d4-a716-446655440050",
    serial_number: "PAL-2025-00050",
    reference_code: "REF-0050",
    type: "B12",
    capacity: 24,
    status: "AU_DEPOT",
    is_full: false,
    rfid_tag_id: "RFID0050",
    current_location: {
      type: "DEPOT",
      name: "Dépôt Principal GAZ PLUS Adjamé"
    },
    last_updated: "2024-11-24T18:00:00Z"
  },
  {
    id: "750e8400-e29b-41d4-a716-446655440051",
    serial_number: "PAL-2025-00051",
    reference_code: "REF-0051",
    type: "B28",
    capacity: 12,
    status: "AU_DEPOT",
    is_full: false,
    rfid_tag_id: "RFID0051",
    current_location: {
      type: "DEPOT",
      name: "Dépôt Principal GAZ PLUS Adjamé"
    },
    last_updated: "2024-11-24T18:05:00Z"
  },
  {
    id: "750e8400-e29b-41d4-a716-446655440052",
    serial_number: "PAL-2025-00052",
    reference_code: "REF-0052",
    type: "B6",
    capacity: 48,
    status: "AU_DEPOT",
    is_full: false,
    rfid_tag_id: "RFID0052",
    current_location: {
      type: "DEPOT",
      name: "Dépôt Principal GAZ PLUS Adjamé"
    },
    last_updated: "2024-11-24T18:10:00Z"
  }
];

// ============================================================================
// BONS D'ENLÈVEMENT
// ============================================================================

export const MOCK_BONS = [
  // Bon VALIDE (prêt pour chargement)
  {
    id: "850e8400-e29b-41d4-a716-446655440001",
    numero_bon: "00000001/11",
    status: "VALIDE",
    date_creation: "2024-11-25T08:00:00Z",
    date_validation: "2024-11-25T08:30:00Z",
    otp_code: "AB12CD",
    otp_expiration: "2024-11-26T08:30:00Z",
    centre_remplisseur: {
      id: "950e8400-e29b-41d4-a716-446655440001",
      name: "Centre Remplisseur Yopougon",
      code: "CR_YOP",
      address: "Zone Industrielle, Boulevard du Gabon",
      city: "Yopougon",
      latitude: 5.3364,
      longitude: -4.0267,
      phone: "+225 27 23 50 00 00",
      contact_name: "Konan Kouassi"
    },
    grossiste: {
      id: "a50e8400-e29b-41d4-a716-446655440001",
      name: "GAZ PLUS Distribution",
      code: "GP001",
      phone: "+225 27 26 00 00 01",
      contact_name: "Moussa Diallo"
    },
    depot_principal: {
      id: "b50e8400-e29b-41d4-a716-446655440001",
      name: "Dépôt Principal GAZ PLUS Adjamé",
      code: "DP_GP_ADJ",
      address: "Adjamé Marché, Rue 12",
      city: "Adjamé",
      latitude: 5.3515,
      longitude: -4.0218,
      contact_name: "Moussa Diallo",
      contact_phone: "+225 07 80 00 00 01"
    },
    vehicule: {
      immatriculation: "AA-1234-BB",
      chauffeur_nom: "Koné Seydou",
      chauffeur_phone: "+225 07 90 00 00 01",
      chauffeur_societe: "Transport Express"
    },
    palettes_count: 0,
    palettes_to_load: 5,
    palettes: [],
    livraisons: [],
    livraisons_count: 0,
    collectes: [],
    collectes_count: 0,
    instructions_livraison: "Livraison standard. Appeler avant arrivée au dépôt."
  },
  // Bon EN_ROUTE (avec livraisons en cours)
  {
    id: "850e8400-e29b-41d4-a716-446655440002",
    numero_bon: "00000002/11",
    status: "EN_ROUTE",
    date_creation: "2024-11-24T08:00:00Z",
    date_validation: "2024-11-24T08:30:00Z",
    date_chargement: "2024-11-24T09:00:00Z",
    date_depart: "2024-11-24T10:00:00Z",
    otp_code: "XY56ZW",
    otp_expiration: "2024-11-25T10:00:00Z",
    centre_remplisseur: {
      id: "950e8400-e29b-41d4-a716-446655440001",
      name: "Centre Remplisseur Yopougon",
      code: "CR_YOP",
      address: "Zone Industrielle, Boulevard du Gabon",
      city: "Yopougon",
      latitude: 5.3364,
      longitude: -4.0267
    },
    grossiste: {
      id: "a50e8400-e29b-41d4-a716-446655440002",
      name: "SUPER GAZ IVOIRE",
      code: "SGI003",
      phone: "+225 27 26 00 00 03"
    },
    depot_principal: {
      id: "b50e8400-e29b-41d4-a716-446655440003",
      name: "Dépôt Principal SUPER GAZ Abobo",
      code: "DP_SGI_ABO",
      address: "Abobo Gare, Avenue Principale",
      city: "Abobo",
      latitude: 5.4167,
      longitude: -4.0208
    },
    vehicule: {
      immatriculation: "BB-5678-CC",
      chauffeur_nom: "Koné Seydou",
      chauffeur_phone: "+225 07 90 00 00 01",
      chauffeur_societe: "Transport Express"
    },
    palettes_count: 8,
    palettes_to_load: 8,
    livraisons_count: 3,
    livraisons: [
      {
        id: "c50e8400-e29b-41d4-a716-446655440001",
        ordre: 1,
        status: "LIVREE",
        depot: {
          id: "b50e8400-e29b-41d4-a716-446655440003",
          name: "Dépôt Principal SUPER GAZ Abobo",
          address: "Abobo Gare, Avenue Principale",
          city: "Abobo",
          latitude: 5.4167,
          longitude: -4.0208,
          contact_name: "Ibrahim Coulibaly",
          contact_phone: "+225 07 80 00 00 03"
        },
        palettes_a_livrer: 5,
        palettes_livrees_count: 5,
        date_arrivee: "2024-11-24T11:00:00Z",
        date_livraison: "2024-11-24T11:30:00Z",
        recepteur_nom: "Ibrahim Coulibaly",
        signature_url: "https://example.com/signatures/sig1.png"
      },
      {
        id: "c50e8400-e29b-41d4-a716-446655440002",
        ordre: 2,
        status: "EN_COURS",
        depot: {
          id: "b50e8400-e29b-41d4-a716-446655440004",
          name: "Espace Gaz Moderne PK18",
          address: "Abobo PK18, Carrefour Pharmacie",
          city: "Abobo",
          latitude: 5.4250,
          longitude: -4.0150,
          contact_name: "Adama Sanogo",
          contact_phone: "+225 05 00 00 00 02"
        },
        palettes_a_livrer: 3,
        palettes_livrees_count: 0,
        date_arrivee: "2024-11-24T12:15:00Z",
        date_livraison: null
      },
      {
        id: "c50e8400-e29b-41d4-a716-446655440003",
        ordre: 3,
        status: "EN_ATTENTE",
        depot: {
          id: "b50e8400-e29b-41d4-a716-446655440005",
          name: "Dépôt Secondaire SUPER GAZ Anyama",
          address: "Anyama, Carrefour Mairie",
          city: "Anyama",
          latitude: 5.4950,
          longitude: -3.9486,
          contact_name: "Saliou Touré",
          contact_phone: "+225 07 80 00 00 31"
        },
        palettes_a_livrer: 0,
        palettes_livrees_count: 0
      }
    ],
    collectes_count: 5,
    collectes: [
      {
        id: "d50e8400-e29b-41d4-a716-446655440001",
        type: "B12",
        quantite_bouteilles: 24,
        palette_serial: "PAL-2025-00080",
        rfid_tag_id: "RFID0080",
        depot_nom: "Dépôt Principal SUPER GAZ Abobo",
        date_collecte: "2024-11-24T11:25:00Z"
      },
      {
        id: "d50e8400-e29b-41d4-a716-446655440002",
        type: "B12",
        quantite_bouteilles: 24,
        palette_serial: "PAL-2025-00081",
        rfid_tag_id: "RFID0081",
        depot_nom: "Dépôt Principal SUPER GAZ Abobo",
        date_collecte: "2024-11-24T11:26:00Z"
      },
      {
        id: "d50e8400-e29b-41d4-a716-446655440003",
        type: "B28",
        quantite_bouteilles: 12,
        palette_serial: "PAL-2025-00082",
        rfid_tag_id: "RFID0082",
        depot_nom: "Dépôt Principal SUPER GAZ Abobo",
        date_collecte: "2024-11-24T11:27:00Z"
      },
      {
        id: "d50e8400-e29b-41d4-a716-446655440004",
        type: "B6",
        quantite_bouteilles: 48,
        palette_serial: "PAL-2025-00083",
        rfid_tag_id: "RFID0083",
        depot_nom: "Dépôt Principal SUPER GAZ Abobo",
        date_collecte: "2024-11-24T11:28:00Z"
      },
      {
        id: "d50e8400-e29b-41d4-a716-446655440005",
        type: "B12",
        quantite_bouteilles: 24,
        palette_serial: "PAL-2025-00084",
        rfid_tag_id: "RFID0084",
        depot_nom: "Dépôt Principal SUPER GAZ Abobo",
        date_collecte: "2024-11-24T11:29:00Z"
      }
    ],
    instructions_livraison: "Tournée multi-dépôts. Respecter l'ordre des livraisons."
  }
];

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

/**
 * Simule un délai réseau
 */
export function delay(ms = 500) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Trouve un tag RFID par son ID
 */
export function findTagByRFID(rfidTagId) {
  return MOCK_TAGS.find(tag => tag.tag_id === rfidTagId);
}

/**
 * Trouve une palette par son tag RFID
 */
export function findPaletteByRFID(rfidTagId) {
  const tag = findTagByRFID(rfidTagId);
  if (!tag || !tag.assigned_to_palette) {
    return null;
  }
  return MOCK_PALETTES.find(p => p.id === tag.palette_id);
}

/**
 * Trouve un bon d'enlèvement par ID
 */
export function findBonById(bonId) {
  return MOCK_BONS.find(bon => bon.id === bonId);
}

/**
 * Obtient les bons assignés au chauffeur par statut
 */
export function getBonsByStatus(statuses = []) {
  if (statuses.length === 0) {
    return MOCK_BONS;
  }
  return MOCK_BONS.filter(bon => statuses.includes(bon.status));
}

/**
 * Obtient les palettes disponibles au centre
 */
export function getAvailablePalettes() {
  return MOCK_PALETTES.filter(p => p.status === "AU_CENTRE" && p.is_full);
}

/**
 * Obtient les palettes vides au dépôt
 */
export function getEmptyPalettesAtDepot() {
  return MOCK_PALETTES.filter(p => p.status === "AU_DEPOT" && !p.is_full);
}

// ============================================================================
// MOCK API RESPONSES
// ============================================================================

export const MOCK_SCAN_RFID_SUCCESS = {
  success: true,
  message: "Palette PAL-2025-00001 scannée avec succès",
  tag: {
    id: "650e8400-e29b-41d4-a716-446655440001",
    tag_id: "RFID0001",
    status: "ACTIVE",
    assigned_to_palette: true
  },
  palette: MOCK_PALETTES[0],
  scan_timestamp: new Date().toISOString()
};

export const MOCK_SCAN_RFID_NOT_FOUND = {
  error: "TAG_NOT_FOUND",
  message: "Tag RFID non trouvé dans le système",
  details: {
    tag_id: "RFID9999"
  }
};

export const MOCK_ADD_PALETTE_SUCCESS = {
  success: true,
  message: "Palette PAL-2025-00001 ajoutée au chargement",
  palette: MOCK_PALETTES[0],
  bon: {
    numero_bon: "00000001/11",
    palettes_count: 1,
    palettes_to_load: 5
  },
  scan_timestamp: new Date().toISOString()
};

export const MOCK_UNLOAD_PALETTE_SUCCESS = {
  success: true,
  message: "Palette PAL-2025-00001 déchargée",
  palette: {
    serial_number: "PAL-2025-00001",
    type: "B12",
    rfid_tag_id: "RFID0001",
    status: "AU_DEPOT"
  },
  livraison: {
    ordre: 1,
    palettes_livrees: 1,
    palettes_restantes: 4,
    depot_name: "Dépôt Principal GAZ PLUS Adjamé"
  },
  scan_timestamp: new Date().toISOString()
};

export const MOCK_COLLECT_EMPTY_SUCCESS = {
  success: true,
  message: "Palette vide PAL-2025-00050 collectée",
  collecte: {
    id: "d50e8400-e29b-41d4-a716-446655440001",
    palette_serial: "PAL-2025-00050",
    type: "B12",
    quantite_bouteilles: 24,
    depot_name: "Dépôt Principal GAZ PLUS Adjamé"
  },
  total_collectes: 1,
  scan_timestamp: new Date().toISOString()
};

// ============================================================================
// EXPORT DEFAULT
// ============================================================================

export default {
  MOCK_USER,
  MOCK_LOGIN_RESPONSE,
  MOCK_TAGS,
  MOCK_PALETTES,
  MOCK_BONS,
  // Helper functions
  delay,
  findTagByRFID,
  findPaletteByRFID,
  findBonById,
  getBonsByStatus,
  getAvailablePalettes,
  getEmptyPalettesAtDepot,
  // Mock responses
  MOCK_SCAN_RFID_SUCCESS,
  MOCK_SCAN_RFID_NOT_FOUND,
  MOCK_ADD_PALETTE_SUCCESS,
  MOCK_UNLOAD_PALETTE_SUCCESS,
  MOCK_COLLECT_EMPTY_SUCCESS
};

