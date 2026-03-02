from fastapi import FastAPI, Query, HTTPException
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
import uvicorn
import asyncio
from scrapers.lamudi import LamudiScraper
from scrapers.inmuebles24 import Inmuebles24Scraper
from utils.google_maps import GoogleMapsUtility

app = FastAPI(title="Real Estate & Commercial Search API")

class Property(BaseModel):
    name: str
    agent: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: str
    lat: Optional[float] = None
    lng: Optional[float] = None
    price: Optional[str] = None
    source: str

class CommercialPlace(BaseModel):
    name: str
    type: str
    address: str
    lat: float
    lng: float

@app.get("/")
def read_root():
    return {"message": "Welcome to the Real Estate & Commercial Search API"}

@app.get("/search", response_model=List[Property])
async def search_properties(
    location: str, 
    limit: int = Query(10, gt=0, le=50),
    source: str = Query("lamudi", regex="^(lamudi|inmuebles24|all)$")
):
    results = []
    
    if source in ["lamudi", "all"]:
        lamudi = LamudiScraper()
        # Note: mapping location names to slugs would be needed for a prod app
        # For now, we assume 'location' is a slug like 'distrito-federal/mexico-city'
        lamudi_results = await lamudi.scrape_listings(location, limit=limit)
        for res in lamudi_results:
            results.append({**res, "source": "lamudi"})
        await lamudi.close()

    if source in ["inmuebles24", "all"]:
        i24 = Inmuebles24Scraper()
        i24_results = await i24.scrape_listings(location, limit=limit)
        for res in i24_results:
            results.append({**res, "source": "inmuebles24"})

    return results[:limit]

@app.get("/nearby-commercial", response_model=List[CommercialPlace])
async def get_nearby_commercial(lat: float, lng: float, radius: int = 5000):
    gmaps = GoogleMapsUtility()
    if not gmaps.api_key:
        # For demo purposes, we can return some mock data if no API key is present
        return [
            {"name": "Mock Supermarket", "type": "supermarket", "address": "Calle Ficticia 123", "lat": lat + 0.001, "lng": lng + 0.001}
        ]
    
    results = []
    types = ["supermarket", "restaurant", "gym", "school"]
    for t in types:
        results.extend(gmaps.find_nearby_commercial(lat, lng, radius, t))
    
    return results

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
