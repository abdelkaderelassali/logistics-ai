import math

CITIES = [
    {"name": "Casablanca", "lat": 33.5731, "lng": -7.5898, "isPort": True, "isAirport": True},
    {"name": "Rabat", "lat": 34.0209, "lng": -6.8416, "isPort": True, "isAirport": True},
    {"name": "Tanger", "lat": 35.7595, "lng": -5.8340, "isPort": True, "isAirport": True},
    {"name": "Fes", "lat": 34.0181, "lng": -5.0078, "isPort": False, "isAirport": True},
    {"name": "Marrakech", "lat": 31.6295, "lng": -7.9811, "isPort": False, "isAirport": True},
    {"name": "Agadir", "lat": 30.4278, "lng": -9.5981, "isPort": True, "isAirport": True},
    {"name": "Meknes", "lat": 33.8731, "lng": -5.5407, "isPort": False, "isAirport": False},
    {"name": "Oujda", "lat": 34.6867, "lng": -1.9114, "isPort": False, "isAirport": True},
    {"name": "Kenitra", "lat": 34.2610, "lng": -6.5802, "isPort": True, "isAirport": False},
    {"name": "Tetouan", "lat": 35.5889, "lng": -5.3626, "isPort": False, "isAirport": False},
]

def get_all_cities():
    return CITIES

def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2) * math.sin(dlat/2) + \
        math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * \
        math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

def find_city(name):
    for c in CITIES:
        if c["name"].lower() == name.lower():
            return c
    return None

def calculate_route(from_city, to_city, optimize_by="distance"):
    start = find_city(from_city)
    end = find_city(to_city)
    
    if not start or not end:
        return None
        
    distance = haversine(start["lat"], start["lng"], end["lat"], end["lng"]) * 1.2 # Adding 20% for road curve factor
    time_hours = distance / 80.0
    time_minutes = time_hours * 60
    fuel_cost = (distance / 100) * 8 * 12 # 8L/100km, 12 MAD/L
    toll_cost = distance * 0.4 # approx 0.4 MAD per km
    
    return {
        "success": True,
        "optimizedFor": optimize_by,
        "route": {
            "from": start["name"],
            "to": end["name"],
            "path": [start["name"], end["name"]],
            "coordinates": [[start["lat"], start["lng"]], [end["lat"], end["lng"]]],
            "segments": [{
                "from": start["name"],
                "to": end["name"],
                "distance": round(distance, 1),
                "travelTime": round(time_minutes),
                "fuelCost": round(fuel_cost),
                "tollCost": round(toll_cost),
                "roadType": "Highway",
                "roadName": "A1/A3"
            }]
        },
        "totals": {
            "distance_km": round(distance, 1),
            "time_minutes": round(time_minutes),
            "time_hours": round(time_hours, 1),
            "fuel_cost_mad": round(fuel_cost, 2),
            "toll_cost_mad": round(toll_cost, 2),
            "total_cost_mad": round(fuel_cost + toll_cost, 2)
        }
    }
