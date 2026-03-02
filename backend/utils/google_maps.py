import googlemaps
import os
from typing import List, Dict, Any, Optional

class GoogleMapsUtility:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GOOGLE_MAPS_API_KEY")
        if not self.api_key:
            print("Warning: GOOGLE_MAPS_API_KEY not found in environment.")
        self.gmaps = googlemaps.Client(key=self.api_key) if self.api_key else None

    def geocode_address(self, address: str) -> Dict[str, Optional[float]]:
        if not self.gmaps:
            return {"lat": None, "lng": None}
        
        try:
            geocode_result = self.gmaps.geocode(address)
            if geocode_result:
                location = geocode_result[0]["geometry"]["location"]
                return {"lat": location["lat"], "lng": location["lng"]}
        except Exception as e:
            print(f"Geocoding error: {e}")
        
        return {"lat": None, "lng": None}

    def find_nearby_commercial(self, lat: float, lng: float, radius: int = 5000, place_type: str = "supermarket") -> List[Dict[str, Any]]:
        if not self.gmaps:
            return []
        
        try:
            # common types: supermarket, restaurant, cafe, shopping_mall, store
            places_result = self.gmaps.places_nearby(
                location=(lat, lng),
                radius=radius,
                type=place_type
            )
            
            results = []
            for place in places_result.get("results", []):
                results.append({
                    "name": place.get("name"),
                    "address": place.get("vicinity"),
                    "type": place_type,
                    "lat": place["geometry"]["location"]["lat"],
                    "lng": place["geometry"]["location"]["lng"]
                })
            return results
        except Exception as e:
            print(f"Places API error: {e}")
            return []
