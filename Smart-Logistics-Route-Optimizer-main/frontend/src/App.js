import { useEffect, useState, useCallback } from 'react';
import axios from 'axios';
import { MapContainer, TileLayer, Polyline, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import './App.css';

// Fix default marker icons
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
});

const API_BASE = 'http://localhost:8000/api';
const AI_API_BASE = 'http://localhost:8000/api';

// Custom marker icons
const createIcon = (color) => new L.Icon({
  iconUrl: `https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-${color}.png`,
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});

const startIcon = createIcon('green');
const endIcon = createIcon('red');
const waypointIcon = createIcon('violet');

// Component to fit map bounds
function FitBounds({ coordinates }) {
  const map = useMap();
  useEffect(() => {
    if (coordinates && coordinates.length > 0) {
      const bounds = L.latLngBounds(coordinates);
      map.fitBounds(bounds, { padding: [50, 50] });
    }
  }, [coordinates, map]);
  return null;
}

function App() {
  const [cities, setCities] = useState([]);
  const [fromCity, setFromCity] = useState('Casablanca');
  const [toCity, setToCity] = useState('Tanger');
  const [optimizeBy, setOptimizeBy] = useState('distance');
  const [routeData, setRouteData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [multiStops, setMultiStops] = useState(['Casablanca', '', 'Tanger']);
  const [activeTab, setActiveTab] = useState('routing');
  const [aiRequest, setAiRequest] = useState('');
  const [aiResponse, setAiResponse] = useState(null);
  const [aiLoading, setAiLoading] = useState(false);
  const [aiError, setAiError] = useState('');

  // Fetch available cities
  useEffect(() => {
    const fetchCities = async () => {
      try {
        const { data } = await axios.get(`${API_BASE}/cities`);
        setCities(data.cities || []);
      } catch (err) {
        console.error('Failed to fetch cities:', err);
      }
    };
    fetchCities();
  }, []);

  // Calculate route
  const calculateRoute = useCallback(async () => {
    setLoading(true);
    setError('');
    setRouteData(null);

    try {
      const { data } = await axios.get(
        `${API_BASE}/route/${optimizeBy}?from=${encodeURIComponent(fromCity)}&to=${encodeURIComponent(toCity)}`
      );
      
      setRouteData(data);
    } catch (err) {
      const message = err.response?.data?.error || 'Failed to calculate route';
      setError(message);
      if (err.response?.data?.availableCities) {
        setError(`${message}. Available: ${err.response.data.availableCities.join(', ')}`);
      }
    } finally {
      setLoading(false);
    }
  }, [fromCity, toCity, optimizeBy]);

  // Calculate multi-stop route
  const calculateMultiRoute = useCallback(async () => {
    const validStops = multiStops.filter(s => s.trim());
    if (validStops.length < 2) {
      setError('Please enter at least 2 stops');
      return;
    }

    setLoading(true);
    setError('');
    setRouteData(null);

    try {
      const { data } = await axios.post(`${API_BASE}/route/multi`, {
        stops: validStops,
        optimize: optimizeBy,
      });
      setRouteData(data);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to calculate route');
    } finally {
      setLoading(false);
    }
  }, [multiStops, optimizeBy]);

  // Add/remove stops
  const addStop = () => setMultiStops([...multiStops.slice(0, -1), '', multiStops[multiStops.length - 1]]);
  const removeStop = (index) => setMultiStops(multiStops.filter((_, i) => i !== index));
  const updateStop = (index, value) => {
    const updated = [...multiStops];
    updated[index] = value;
    setMultiStops(updated);
  };

  const routeColor = {
    distance: '#00f0ff',
    time: '#00ff88',
    cost: '#ffaa00',
  };

  const handleAiSubmit = async () => {
    if (!aiRequest.trim() || aiRequest.length < 10) {
      setAiError('Please enter a longer request (at least 10 characters).');
      return;
    }
    setAiLoading(true);
    setAiError('');
    setAiResponse(null);
    try {
      const { data } = await axios.post(`${AI_API_BASE}/process`, {
        request: aiRequest
      }, { timeout: 120000 }); // 120s — the 4-agent pipeline takes ~30-40s
      setAiResponse(data);
      if (data.ai_route) {
        setRouteData(data.ai_route);
      }
    } catch (err) {
      setAiError(err.response?.data?.detail || err.message || 'Failed to process AI request');
    } finally {
      setAiLoading(false);
    }
  };

  return (
    <>
      {/* Ambient Background */}
      <div className="ambient-bg">
        <div className="orb orb-1"></div>
        <div className="orb orb-2"></div>
        <div className="orb orb-3"></div>
      </div>
      <div className="grid-overlay"></div>

      <div className="app-container">
        {/* Header */}
        <header className="app-header">
          <div className="header-content">
            <div className="logo-icon">SL</div>
            <div>
              <h1 className="header-title">Smart Logistics</h1>
              <p className="header-subtitle">LangChain Multi-Agents • LlamaIndex RAG • Groq LLM</p>
            </div>
          </div>
        </header>

        <div className="main-content">
          {/* Sidebar */}
          <aside className="sidebar">
            <div className="tabs">
              <button 
                className={`tab-btn ${activeTab === 'routing' ? 'active' : ''}`}
                onClick={() => setActiveTab('routing')}
              >
                Routing
              </button>
              <button 
                className={`tab-btn ${activeTab === 'ai' ? 'active' : ''}`}
                onClick={() => setActiveTab('ai')}
              >
                AI Assistant
              </button>
            </div>

            {activeTab === 'routing' ? (
              <>
                {/* Optimization Type Buttons */}
            <div className="optimize-buttons">
              <button
                onClick={() => setOptimizeBy('distance')}
                className={`optimize-btn ${optimizeBy === 'distance' ? 'active distance' : ''}`}
              >
                Shortest
              </button>
              <button
                onClick={() => setOptimizeBy('time')}
                className={`optimize-btn ${optimizeBy === 'time' ? 'active time' : ''}`}
              >
                Fastest
              </button>
              <button
                onClick={() => setOptimizeBy('cost')}
                className={`optimize-btn ${optimizeBy === 'cost' ? 'active cost' : ''}`}
              >
                Cheapest
              </button>
            </div>

            {/* Point to Point */}
            <div className="glass-card">
              <h3 className="card-title">Point to Point</h3>
              
              <div className="form-group">
                <label className="form-label">Origin</label>
                <select
                  value={fromCity}
                  onChange={(e) => setFromCity(e.target.value)}
                  className="form-select start-select"
                >
                  {cities.map((c) => (
                    <option key={c.name} value={c.name}>{c.name}</option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Destination</label>
                <select
                  value={toCity}
                  onChange={(e) => setToCity(e.target.value)}
                  className="form-select end-select"
                >
                  {cities.map((c) => (
                    <option key={c.name} value={c.name}>{c.name}</option>
                  ))}
                </select>
              </div>

              <button
                onClick={calculateRoute}
                disabled={loading}
                className={`btn-primary ${loading ? 'loading' : ''}`}
              >
                {loading ? 'Calculating...' : 'Find Route'}
              </button>
            </div>

            {/* Multi-Stop Route */}
            <div className="glass-card">
              <h3 className="card-title">Multi-Stop Route</h3>
              
              {multiStops.map((stop, index) => (
                <div key={index} className="stop-row">
                  <span className={`stop-number ${index === 0 ? 'start' : index === multiStops.length - 1 ? 'end' : ''}`}>
                    {index + 1}
                  </span>
                  <select
                    value={stop}
                    onChange={(e) => updateStop(index, e.target.value)}
                    className={`form-select ${index === 0 ? 'start-select' : index === multiStops.length - 1 ? 'end-select' : 'waypoint-select'}`}
                  >
                    <option value="">-- Stop {index + 1} --</option>
                    {cities.map((c) => (
                      <option key={c.name} value={c.name}>{c.name}</option>
                    ))}
                  </select>
                  {multiStops.length > 2 && index !== 0 && index !== multiStops.length - 1 && (
                    <button
                      onClick={() => removeStop(index)}
                      className="btn-danger"
                    >
                      ✕
                    </button>
                  )}
                </div>
              ))}
              
              <div className="multi-actions">
                <button onClick={addStop} className="btn-secondary">
                  + Add Stop
                </button>
                <button
                  onClick={calculateMultiRoute}
                  disabled={loading}
                  className={`btn-primary ${loading ? 'loading' : ''}`}
                >
                  {loading ? '...' : 'Calculate'}
                </button>
              </div>
            </div>

            {/* Error Display */}
            {error && (
              <div className="error-message">
                <span>{error}</span>
              </div>
            )}

            {/* Results */}
            {routeData && (
              <div className="results-card">
                <h3 className={`results-title ${optimizeBy}`}>Route Summary</h3>
                
                {/* Route Path */}
                <div className="route-path">
                  <div className="route-path-label">Route</div>
                  <div className="route-path-cities">
                    {routeData.route.path.map((city, i) => (
                      <span key={i}>
                        {i > 0 && <span className={`route-arrow ${optimizeBy}`}> → </span>}
                        <span className={`route-city ${i === 0 ? 'start' : i === routeData.route.path.length - 1 ? 'end' : ''}`}>
                          {city}
                        </span>
                      </span>
                    ))}
                  </div>
                </div>

                {/* Stats Grid */}
                <div className="stats-grid">
                  <div className="stat-card distance">
                    <div className="stat-value">{routeData.totals.distance_km} km</div>
                    <div className="stat-label">Distance</div>
                  </div>
                  
                  <div className="stat-card time">
                    <div className="stat-value">{routeData.totals.time_hours}h</div>
                    <div className="stat-label">Time</div>
                  </div>
                  
                  <div className="stat-card fuel">
                    <div className="stat-value">{routeData.totals.fuel_cost_mad}</div>
                    <div className="stat-label">Fuel (MAD)</div>
                  </div>
                  
                  <div className="stat-card toll">
                    <div className="stat-value">{routeData.totals.toll_cost_mad}</div>
                    <div className="stat-label">Tolls (MAD)</div>
                  </div>
                </div>

                {/* Total Cost */}
                <div className={`total-cost-banner ${optimizeBy}`}>
                  <div className="total-cost-label">Total Cost</div>
                  <div className="total-cost-value">
                    {routeData.totals.total_cost_mad} MAD
                  </div>
                </div>

                {/* Segments */}
                {routeData.route.segments && routeData.route.segments.length > 0 && (
                  <div className="segments-section">
                    <h4 className="segments-title">Route Details</h4>
                    <div className="segments-list">
                      {routeData.route.segments.map((seg, i) => (
                        <div key={i} className="segment-item">
                          <div className="segment-route">
                            {seg.from} → {seg.to}
                          </div>
                          <div className="segment-details">
                            {seg.distance}km • {seg.travelTime}min
                            <span className="segment-badge">{seg.roadType}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
            </>
            ) : (
              <div className="glass-card ai-assistant">
                <h3 className="card-title">AI Assistant</h3>
                <p className="ai-description">
                  Describe your logistics needs. Our <strong>LangGraph Multi-Agent</strong> system (4 specialized agents) will use <strong>RAG via LlamaIndex</strong> to query private fleet & regulation data and return a professional logistics plan.
                </p>
                <textarea
                  value={aiRequest}
                  onChange={(e) => setAiRequest(e.target.value)}
                  placeholder="e.g. Transport 15 tons of medical supplies from Rabat to Casablanca arriving before 14:00."
                  className="ai-textarea"
                  rows={4}
                />
                <button
                  onClick={handleAiSubmit}
                  disabled={aiLoading}
                  className={`btn-primary ${aiLoading ? 'loading' : ''}`}
                >
                  {aiLoading ? '4 agents working — please wait...' : 'Process Request'}
                </button>

                {aiLoading && (
                  <p style={{ fontSize: '0.8rem', color: 'rgba(255,255,255,0.5)', marginTop: '8px' }}>
                    The AI pipeline runs 4 agents sequentially. This takes 30–60 seconds.
                  </p>
                )}
                
                {aiError && (
                  <div className="error-message" style={{ marginTop: '10px' }}>
                    <span>{aiError}</span>
                  </div>
                )}

                {aiResponse && (
                  <div className="ai-results">
                    <h4 className="ai-results-title">System Output</h4>
                    <div className="ai-stage">
                      <h5>Agent Recherche (RAG)</h5>
                      <p>{aiResponse.rag_context}</p>
                    </div>
                    <div className="ai-stage">
                      <h5>Agent Analyse</h5>
                      <p>{aiResponse.analysis_plan}</p>
                    </div>
                    <div className="ai-stage">
                      <h5>Agent Validation</h5>
                      <p>{aiResponse.validation_report}</p>
                    </div>
                    <div className="ai-stage final-stage">
                      <h5>Final Response</h5>
                      <p>{aiResponse.final_response}</p>
                    </div>
                  </div>
                )}
              </div>
            )}
          </aside>

          {/* Map */}
          <main className="map-container">
            <MapContainer 
              center={[32.0, -6.0]} 
              zoom={6} 
              style={{ height: '100%', width: '100%' }}
            >
              <TileLayer
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              />

              {/* Route polyline */}
              {routeData && routeData.route.coordinates && (
                <>
                  <Polyline
                    positions={routeData.route.coordinates}
                    color={routeColor[optimizeBy]}
                    weight={5}
                    opacity={0.9}
                  />
                  <FitBounds coordinates={routeData.route.coordinates} />
                  
                  {/* Markers */}
                  {routeData.route.coordinates.map((coord, idx) => {
                    const isStart = idx === 0;
                    const isEnd = idx === routeData.route.coordinates.length - 1;
                    const cityName = routeData.route.path[idx];
                    
                    return (
                      <Marker
                        key={`${coord[0]}-${coord[1]}-${idx}`}
                        position={coord}
                        icon={isStart ? startIcon : isEnd ? endIcon : waypointIcon}
                      >
                        <Popup>
                          <strong style={{ color: '#00f0ff' }}>{cityName}</strong>
                          <br />
                          {isStart ? 'Start' : isEnd ? 'End' : 'Waypoint'}
                        </Popup>
                      </Marker>
                    );
                  })}
                </>
              )}

              {/* Show all cities when no route */}
              {!routeData && cities.map((city) => (
                <Marker
                  key={city.name}
                  position={[city.lat, city.lng]}
                >
                  <Popup>
                    <strong style={{ color: '#00f0ff' }}>{city.name}</strong>
                    <br />
                    <span style={{ color: 'rgba(255,255,255,0.7)' }}>
                      {city.isPort && 'Port '}
                      {city.isAirport && 'Airport'}
                    </span>
                  </Popup>
                </Marker>
              ))}
            </MapContainer>
          </main>
        </div>
      </div>
    </>
  );
}

export default App;
