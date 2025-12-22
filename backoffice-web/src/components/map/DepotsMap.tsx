import { useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Fix for default marker icons in React-Leaflet
// @ts-ignore - Leaflet image imports
import icon from 'leaflet/dist/images/marker-icon.png';
// @ts-ignore - Leaflet image imports
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

const DefaultIcon = L.icon({
  iconUrl: icon,
  shadowUrl: iconShadow,
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
});

L.Marker.prototype.options.icon = DefaultIcon;

// Interface for depot data with location
interface DepotWithLocation {
  id: string;
  name: string;
  address?: string;
  city?: string;
  latitude: number;
  longitude: number;
  paletteCount: number;
}

// Demo data for Abidjan depots
const demoDepots: DepotWithLocation[] = [
  {
    id: '1',
    name: 'Dépôt Cocody',
    address: 'Boulevard de la République, Cocody',
    city: 'Abidjan',
    latitude: 5.3364,
    longitude: -4.0267,
    paletteCount: 45,
  },
  {
    id: '2',
    name: 'Dépôt Yopougon',
    address: 'Avenue principale, Yopougon',
    city: 'Abidjan',
    latitude: 5.3167,
    longitude: -4.0833,
    paletteCount: 32,
  },
  {
    id: '3',
    name: 'Dépôt Marcory',
    address: 'Zone industrielle, Marcory',
    city: 'Abidjan',
    latitude: 5.2833,
    longitude: -4.0167,
    paletteCount: 28,
  },
  {
    id: '4',
    name: 'Dépôt Adjamé',
    address: 'Gare routière, Adjamé',
    city: 'Abidjan',
    latitude: 5.3667,
    longitude: -4.0167,
    paletteCount: 67,
  },
  {
    id: '5',
    name: 'Dépôt Plateau',
    address: 'Centre-ville, Plateau',
    city: 'Abidjan',
    latitude: 5.3167,
    longitude: -4.0333,
    paletteCount: 23,
  },
  {
    id: '6',
    name: 'Dépôt Abobo',
    address: 'Avenue principale, Abobo',
    city: 'Abidjan',
    latitude: 5.4167,
    longitude: -4.1333,
    paletteCount: 54,
  },
];

// Component to handle map view updates
function MapViewUpdater({ center }: { center: [number, number] }) {
  const map = useMap();
  
  useEffect(() => {
    map.setView(center, map.getZoom());
  }, [center, map]);
  
  return null;
}

interface DepotsMapProps {
  height?: string;
}

export const DepotsMap: React.FC<DepotsMapProps> = ({ height = '500px' }) => {
  // Center on Abidjan
  const abidjanCenter: [number, number] = [5.3167, -4.0333];

  // Custom marker icon with palette count
  const createCustomIcon = (count: number) => {
    const isHighStock = count > 50;
    const color = isHighStock ? '#22c55e' : count > 30 ? '#f59e0b' : '#ef4444';
    
    return L.divIcon({
      className: 'custom-marker',
      html: `
        <div style="
          background-color: ${color};
          width: 40px;
          height: 40px;
          border-radius: 50%;
          border: 3px solid white;
          box-shadow: 0 2px 8px rgba(0,0,0,0.3);
          display: flex;
          align-items: center;
          justify-content: center;
          color: white;
          font-weight: bold;
          font-size: 14px;
        ">
          ${count}
        </div>
      `,
      iconSize: [40, 40],
      iconAnchor: [20, 20],
      popupAnchor: [0, -20],
    });
  };

  return (
    <div style={{ height, width: '100%', borderRadius: '8px', overflow: 'hidden' }}>
      <MapContainer
        center={abidjanCenter}
        zoom={12}
        style={{ height: '100%', width: '100%' }}
        scrollWheelZoom={true}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <MapViewUpdater center={abidjanCenter} />
        
        {demoDepots.map((depot) => (
          <Marker
            key={depot.id}
            position={[depot.latitude, depot.longitude]}
            icon={createCustomIcon(depot.paletteCount)}
          >
            <Popup>
              <div style={{ minWidth: '200px' }}>
                <h3 style={{ margin: '0 0 8px 0', fontWeight: 'bold', fontSize: '16px' }}>
                  {depot.name}
                </h3>
                {depot.address && (
                  <p style={{ margin: '4px 0', fontSize: '14px', color: '#666' }}>
                    📍 {depot.address}
                  </p>
                )}
                <p style={{ margin: '8px 0 0 0', fontSize: '14px', fontWeight: '600' }}>
                  📦 Palettes: <span style={{ color: '#2563eb' }}>{depot.paletteCount}</span>
                </p>
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>
      
      <style>{`
        .custom-marker {
          background: transparent !important;
          border: none !important;
        }
        .leaflet-popup-content-wrapper {
          border-radius: 8px;
        }
        .leaflet-popup-content {
          margin: 12px;
        }
      `}</style>
    </div>
  );
};
