import httpx
from bs4 import BeautifulSoup
import random
import time
from typing import List, Dict, Any, Optional
import json

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
]

class LamudiScraper:
    def __init__(self):
        self.base_url = "https://www.lamudi.com.mx"
        self.client = httpx.AsyncClient(timeout=30.0)

    async def get_headers(self):
        return {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "es-MX,es;q=0.9,en;q=0.8",
            "Referer": "https://www.google.com/",
        }

    async def scrape_listings(self, location_slug: str, limit: int = 10) -> List[Dict[str, Any]]:
        # Example URL: https://www.lamudi.com.mx/casa/venta/distrito-federal/mexico-city/
        search_url = f"{self.base_url}/{location_slug}/"
        properties = []
        
        try:
            response = await self.client.get(search_url, headers=await self.get_headers())
            if response.status_code != 200:
                print(f"Error fetching Lamudi listings: {response.status_code}")
                return []

            soup = BeautifulSoup(response.text, "html.parser")
            # Lamudi listings usually have a JSON-LD or specific classes
            # This is a simplified version, real implementation needs to match their current DOM
            Listing_items = soup.select(".Listing-cell")[:limit]
            
            for item in Listing_items:
                # Add delay to avoid detection
                time.sleep(random.uniform(1.0, 2.5))
                
                # Basic data extraction (placeholders for specific selectors)
                name = item.select_one(".listing-card__title").text.strip() if item.select_one(".listing-card__title") else "N/A"
                address = item.select_one(".listing-card__address").text.strip() if item.select_one(".listing-card__address") else "N/A"
                price = item.select_one(".listing-card__price").text.strip() if item.select_one(".listing-card__price") else "N/A"
                link = item.select_one("a")["href"] if item.select_one("a") else None
                
                full_link = self.base_url + link if link and not link.startswith("http") else link
                
                # Fetch individual page for agent info if available
                agent_info = await self.scrape_listing_details(full_link) if full_link else {}
                
                properties.append({
                    "name": name,
                    "address": address,
                    "price": price,
                    **agent_info
                })
                
                if len(properties) >= limit:
                    break
                    
        except Exception as e:
            print(f"Scraping error: {e}")
            
        return properties

    async def scrape_listing_details(self, url: str) -> Dict[str, Any]:
        try:
            time.sleep(random.uniform(2.0, 4.0)) # Politeness delay
            response = await self.client.get(url, headers=await self.get_headers())
            if response.status_code != 200:
                return {}

            soup = BeautifulSoup(response.text, "html.parser")
            
            # Extract JSON-LD if present (highly recommended for Lamudi)
            scripts = soup.find_all("script", type="application/ld+json")
            details = {}
            for script in scripts:
                try:
                    data = json.loads(script.string)
                    if isinstance(data, dict):
                        # Extract agent info, coords from JSON-LD
                        if data.get("@type") == "RealEstateListing":
                            details["agent"] = data.get("author", {}).get("name")
                            details["lat"] = data.get("geo", {}).get("latitude")
                            details["lng"] = data.get("geo", {}).get("longitude")
                except:
                    continue
            
            # Fallback to selectors if JSON-LD fails
            if not details.get("agent"):
                details["agent"] = soup.select_one(".agent-name").text.strip() if soup.select_one(".agent-name") else "N/A"
            
            return details
        except:
            return {}

    async def close(self):
        await self.client.aclose()
