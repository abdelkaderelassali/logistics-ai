# Smart Logistics Route Optimizer

## 🎯 Overview

Production-grade logistics route optimization system powered by:
- **Neo4j** - Graph database for road network
- **Neo4j GDS** - Dijkstra & A* algorithms
- **Express.js** - REST API backend
- **React + Leaflet** - Interactive map frontend

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND                                 │
│  React + Leaflet Map                                            │
│  - City selection (From/To)                                     │
│  - Multi-stop routes                                            │
│  - Optimization type (Distance/Time/Cost)                       │
│  - Route visualization                                          │
└─────────────────────────┬───────────────────────────────────────┘
                          │ HTTP REST
┌─────────────────────────▼───────────────────────────────────────┐
│                         BACKEND                                  │
│  Express.js Server (Port 3001)                                  │
│  Endpoints:                                                      │
│  - GET  /api/route/shortest   - Dijkstra (distance_km)          │
│  - GET  /api/route/fastest    - Dijkstra (travel_time)          │
│  - GET  /api/route/cheapest   - Dijkstra (total_cost)           │
│  - POST /api/route/multi      - Multi-stop optimization         │
│  - GET  /api/cities           - List all cities                 │
│  - GET  /api/roads            - List all connections            │
└─────────────────────────┬───────────────────────────────────────┘
                          │ Bolt Protocol
┌─────────────────────────▼───────────────────────────────────────┐
│                         NEO4J                                    │
│  Graph Data Model:                                              │
│  (:City) -[:ROAD {distance_km, travel_time, fuel_cost}]-> (:City)│
│                                                                  │
│  GDS Projections:                                               │
│  - distanceGraph (weight: distance_km)                          │
│  - timeGraph (weight: travel_time)                              │
│  - costGraph (weight: total_cost)                               │
└─────────────────────────────────────────────────────────────────┘
```

## 📦 Installation

### 1. Neo4j Setup

```bash
# Install Neo4j Desktop or use Docker
docker run -d \
  --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/123456789 \
  -e NEO4J_PLUGINS='["graph-data-science"]' \
  neo4j:5
```

### 2. Load Data into Neo4j

Open Neo4j Browser (http://localhost:7474) and run these scripts in order:

1. `neo4j/01_schema.cypher` - Create constraints & indexes
2. `neo4j/02_morocco_cities.cypher` - Create City nodes
3. `neo4j/03_road_network.cypher` - Create ROAD relationships
4. `neo4j/04_gds_projections.cypher` - Create GDS graph projections

### 3. Backend Setup

```bash
cd backend
npm install
node server.js
```

### 4. Frontend Setup

```bash
cd frontend
npm install
npm start
```

## 🗺️ Neo4j Data Model

### Node: City
```cypher
(:City {
  name: "Casablanca",
  lat: 33.5731,
  lng: -7.5898,
  population: 3359000,
  is_port: true,
  is_airport: true
})
```

### Relationship: ROAD
```cypher
[:ROAD {
  distance_km: 87,
  speed_limit: 120,
  travel_time: 44,      // minutes
  fuel_cost: 83.52,     // MAD
  toll_cost: 20,        // MAD
  road_type: "highway",
  road_name: "A3"
}]
```

## 🔌 API Reference

### GET /api/route/shortest
Find shortest distance route.

```bash
curl "http://localhost:3001/api/route/shortest?from=Casablanca&to=Tanger"
```

Response:
```json
{
  "success": true,
  "optimizedFor": "shortest_distance",
  "route": {
    "path": ["Casablanca", "Rabat", "Tanger"],
    "coordinates": [[33.57, -7.58], [34.02, -6.84], [35.75, -5.83]],
    "segments": [...]
  },
  "totals": {
    "distance_km": 337,
    "time_minutes": 169,
    "fuel_cost_mad": 323.52,
    "toll_cost_mad": 85,
    "total_cost_mad": 408.52
  }
}
```

### POST /api/route/multi
Calculate multi-stop route.

```bash
curl -X POST "http://localhost:3001/api/route/multi" \
  -H "Content-Type: application/json" \
  -d '{"stops": ["Casablanca", "Rabat", "Fes", "Marrakech"], "optimize": "distance"}'
```

## 🚀 Usage

1. Open http://localhost:3000
2. Select **From** city (green marker)
3. Select **To** city (red marker)
4. Choose optimization: Shortest / Fastest / Cheapest
5. Click **Find Route**
6. View route on map with detailed costs

## 📊 Optimization Algorithms

| Type | Algorithm | Weight Property | Use Case |
|------|-----------|-----------------|----------|
| Shortest | Dijkstra | distance_km | Minimize kilometers |
| Fastest | Dijkstra | travel_time | Minimize time |
| Cheapest | Dijkstra | total_cost | Minimize fuel + tolls |

## 🛠️ Configuration

### Backend Environment Variables
```bash
PORT=3001
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=123456789
```

### Fuel Cost Calculation
```javascript
CONFIG = {
  fuelConsumptionPer100Km: 8,  // Liters
  fuelPricePerLiter: 12,       // MAD
}
// fuel_cost = (distance_km / 100) * 8 * 12
```

## 📁 Project Structure

```
LogisticsApp/
├── backend/
│   ├── server.js          # Express API server
│   └── package.json
├── frontend/
│   ├── src/
│   │   ├── App.js         # Main React component
│   │   └── index.js
│   ├── public/
│   │   └── index.html
│   └── package.json
├── neo4j/
│   ├── 01_schema.cypher
│   ├── 02_morocco_cities.cypher
│   ├── 03_road_network.cypher
│   ├── 04_gds_projections.cypher
│   └── 05_sample_queries.cypher
└── README.md
```

## 🔧 Troubleshooting

### "No path found"
1. Check city names match exactly (case-insensitive)
2. Verify cities are connected via ROAD relationships
3. Run `/api/cities` to see available cities

### GDS Errors
```bash
# Refresh all graph projections
curl -X POST http://localhost:3001/api/graph/refresh
```

### Connection Issues
```bash
# Verify Neo4j is running
curl http://localhost:3001/api/health
```

## 📈 Future Enhancements

- [ ] Import real OSM data via osm2neo4j
- [ ] Real-time traffic integration
- [ ] Vehicle capacity constraints
- [ ] Time windows for deliveries
- [ ] Multiple vehicle routing (VRP)
- [ ] Historical route analytics

---

Built for DHL / FedEx scale logistics optimization 🚚
