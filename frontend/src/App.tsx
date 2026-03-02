import { useState, useEffect } from 'react';
import { APIProvider, Map, Marker, InfoWindow } from '@vis.gl/react-google-maps';
import { Search, MapPin, Building2, Phone, Mail, User, Info, Loader2 } from 'lucide-react';

interface Property {
    name: string;
    agent?: string;
    phone?: string;
    email?: string;
    address: string;
    lat?: number;
    lng?: number;
    price?: string;
    source: string;
}

interface CommercialPlace {
    name: string;
    type: string;
    address: string;
    lat: number;
    lng: number;
}

const GOOGLE_MAPS_API_KEY = import.meta.env.VITE_GOOGLE_MAPS_API_KEY || '';

export default function App() {
    const [location, setLocation] = useState('distrito-federal/mexico-city');
    const [limit, setLimit] = useState(10);
    const [loading, setLoading] = useState(false);
    const [properties, setProperties] = useState<Property[]>([]);
    const [selectedProperty, setSelectedProperty] = useState<Property | null>(null);
    const [nearbyPlaces, setNearbyPlaces] = useState<CommercialPlace[]>([]);
    const [loadingPlaces, setLoadingPlaces] = useState(false);

    const handleSearch = async () => {
        setLoading(true);
        try {
            const response = await fetch(`http://localhost:8000/search?location=${location}&limit=${limit}&source=all`);
            const data = await response.json();
            setProperties(data);
        } catch (error) {
            console.error('Search error:', error);
        } finally {
            setLoading(false);
        }
    };

    const fetchNearby = async (lat: number, lng: number) => {
        setLoadingPlaces(true);
        try {
            const response = await fetch(`http://localhost:8000/nearby-commercial?lat=${lat}&lng=${lng}`);
            const data = await response.json();
            setNearbyPlaces(data);
        } catch (error) {
            console.error('Nearby error:', error);
        } finally {
            setLoadingPlaces(false);
        }
    };

    useEffect(() => {
        if (selectedProperty?.lat && selectedProperty?.lng) {
            fetchNearby(selectedProperty.lat, selectedProperty.lng);
        }
    }, [selectedProperty]);

    return (
        <div className="flex flex-col h-screen w-screen bg-gray-900 text-white overflow-hidden">
            {/* Header */}
            <header className="p-4 bg-gray-800 border-b border-gray-700 flex items-center justify-between shadow-lg z-10">
                <div className="flex items-center gap-2">
                    <Building2 className="text-blue-400" />
                    <h1 className="text-xl font-bold bg-gradient-to-r from-blue-400 to-teal-400 bg-clip-text text-transparent">
                        RECSearch
                    </h1>
                </div>
                <div className="flex items-center gap-4">
                    <div className="flex items-center bg-gray-700 rounded-lg px-3 py-1 border border-gray-600">
                        <Search size={18} className="text-gray-400 mr-2" />
                        <input
                            type="text"
                            value={location}
                            onChange={(e) => setLocation(e.target.value)}
                            placeholder="Ubicación (slug)"
                            className="bg-transparent border-none focus:ring-0 text-sm w-48"
                        />
                    </div>
                    <div className="flex items-center bg-gray-700 rounded-lg px-3 py-1 border border-gray-600">
                        <span className="text-xs text-gray-400 mr-2">Límite:</span>
                        <input
                            type="number"
                            value={limit}
                            onChange={(e) => setLimit(parseInt(e.target.value) || 1)}
                            className="bg-transparent border-none focus:ring-0 text-sm w-12"
                        />
                    </div>
                    <button
                        onClick={handleSearch}
                        disabled={loading}
                        className="bg-blue-600 hover:bg-blue-500 disabled:opacity-50 px-4 py-1 rounded-lg font-medium transition-colors flex items-center gap-2"
                    >
                        {loading ? <Loader2 className="animate-spin" size={18} /> : 'Buscar'}
                    </button>
                </div>
            </header>

            <div className="flex flex-1 overflow-hidden">
                {/* Sidebar */}
                <div className="w-1/3 min-w-[350px] bg-gray-800 border-r border-gray-700 overflow-y-auto p-4 custom-scrollbar">
                    <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                        <Info size={18} className="text-blue-400" />
                        Resultados ({properties.length})
                    </h2>

                    <div className="space-y-4">
                        {properties.map((prop, idx) => (
                            <div
                                key={idx}
                                onClick={() => setSelectedProperty(prop)}
                                className={`p-4 rounded-xl border transition-all cursor-pointer ${selectedProperty === prop
                                    ? 'bg-blue-900/30 border-blue-500 shadow-[0_0_15px_rgba(59,130,246,0.3)]'
                                    : 'bg-gray-700/50 border-gray-600 hover:border-gray-500'
                                    }`}
                            >
                                <h3 className="font-bold text-lg mb-1">{prop.name}</h3>
                                <p className="text-gray-400 text-sm mb-3 flex items-start gap-1">
                                    <MapPin size={14} className="mt-1 flex-shrink-0" />
                                    {prop.address}
                                </p>

                                <div className="grid grid-cols-1 gap-2 border-t border-gray-600/50 pt-3">
                                    <div className="flex items-center gap-2 text-sm">
                                        <User size={14} className="text-teal-400" />
                                        <span>{prop.agent || 'No especificado'}</span>
                                    </div>
                                    {prop.phone && (
                                        <div className="flex items-center gap-2 text-sm text-blue-300">
                                            <Phone size={14} />
                                            <span>{prop.phone}</span>
                                        </div>
                                    )}
                                    {prop.email && (
                                        <div className="flex items-center gap-2 text-sm text-blue-300">
                                            <Mail size={14} />
                                            <span className="truncate">{prop.email}</span>
                                        </div>
                                    )}
                                </div>

                                <div className="mt-3 flex justify-between items-center">
                                    <span className="text-xs bg-gray-600 px-2 py-0.5 rounded uppercase tracking-wider text-gray-300">
                                        {prop.source}
                                    </span>
                                    <span className="text-teal-400 font-bold">{prop.price}</span>
                                </div>
                            </div>
                        ))}

                        {!loading && properties.length === 0 && (
                            <div className="text-center py-12 text-gray-500 italic">
                                Usa el buscador para encontrar propiedades
                            </div>
                        )}
                    </div>
                </div>

                {/* Map Area */}
                <div className="flex-1 relative">
                    <APIProvider apiKey={GOOGLE_MAPS_API_KEY}>
                        <Map
                            defaultCenter={{ lat: 19.4326, lng: -99.1332 }}
                            defaultZoom={11}
                            mapId="bf50a91341416e8"
                            style={{ width: '100%', height: '100%' }}
                            colorScheme="DARK"
                        >
                            {properties.map((prop, idx) => (
                                prop.lat && prop.lng && (
                                    <Marker
                                        key={idx}
                                        position={{ lat: prop.lat, lng: prop.lng }}
                                        onClick={() => setSelectedProperty(prop)}
                                    />
                                )
                            ))}

                            {selectedProperty?.lat && selectedProperty?.lng && (
                                <InfoWindow
                                    position={{ lat: selectedProperty.lat, lng: selectedProperty.lng }}
                                    onCloseClick={() => setSelectedProperty(null)}
                                >
                                    <div className="text-gray-900 p-1">
                                        <h4 className="font-bold">{selectedProperty.name}</h4>
                                        <p className="text-xs">{selectedProperty.address}</p>
                                    </div>
                                </InfoWindow>
                            )}

                            {/* Nearby Commercial Places */}
                            {nearbyPlaces.map((place, idx) => (
                                <Marker
                                    key={`place-${idx}`}
                                    position={{ lat: place.lat, lng: place.lng }}
                                    icon={{
                                        path: 0, // Circle
                                        scale: 6,
                                        fillColor: '#10b981',
                                        fillOpacity: 1,
                                        strokeWeight: 2,
                                        strokeColor: '#ffffff'
                                    }}
                                />
                            ))}
                        </Map>
                    </APIProvider>

                    {/* Map Overlay Summary */}
                    {selectedProperty && (
                        <div className="absolute top-4 right-4 bg-gray-800/90 backdrop-blur-md p-4 rounded-xl border border-gray-700 shadow-2xl max-w-xs animate-in fade-in slide-in-from-right-4 duration-300">
                            <h4 className="font-bold text-blue-400 mb-2">Locales comerciales (5km)</h4>
                            <div className="max-h-64 overflow-y-auto custom-scrollbar">
                                {loadingPlaces ? (
                                    <div className="flex items-center justify-center py-4">
                                        <Loader2 className="animate-spin" size={20} />
                                    </div>
                                ) : nearbyPlaces.length > 0 ? (
                                    <div className="space-y-2">
                                        {nearbyPlaces.map((place, idx) => (
                                            <div key={idx} className="text-sm border-b border-gray-700/50 pb-2">
                                                <div className="font-medium">{place.name}</div>
                                                <div className="text-xs text-gray-400">{place.type} • {place.address}</div>
                                            </div>
                                        ))}
                                    </div>
                                ) : (
                                    <p className="text-xs text-gray-500 italic">No se encontraron locales cercanos</p>
                                )}
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
