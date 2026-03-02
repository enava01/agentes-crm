from playwright.async_api import async_playwright
from playwright_stealth import stealth_async
import random
import asyncio
from typing import List, Dict, Any, Optional

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
]

class Inmuebles24Scraper:
    def __init__(self):
        self.base_url = "https://www.inmuebles24.com"

    async def scrape_listings(self, location_slug: str, limit: int = 10) -> List[Dict[str, Any]]:
        properties = []
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent=random.choice(USER_AGENTS),
                viewport={'width': 1280, 'height': 800}
            )
            page = await context.new_page()
            await stealth_async(page)
            
            # Example search URL
            search_url = f"{self.base_url}/casas-en-venta-en-{location_slug}.html"
            
            try:
                await page.goto(search_url, wait_until="networkidle", timeout=60000)
                # Wait for listings to load
                await page.wait_for_selector(".post-container", timeout=10000)
                
                listings = await page.query_selector_all(".post-container")
                for listing in listings[:limit]:
                    data = {}
                    # Extraction logic (based on Inmuebles24 structure)
                    title_element = await listing.query_selector(".posting-title")
                    data["name"] = await title_element.inner_text() if title_element else "N/A"
                    
                    address_element = await listing.query_selector(".posting-location")
                    data["address"] = await address_element.inner_text() if address_element else "N/A"
                    
                    price_element = await listing.query_selector(".posting-price")
                    data["price"] = await price_element.inner_text() if price_element else "N/A"
                    
                    # For agent and more details, we might need to click or visit the link
                    # But often it's in the listing card or can be inferred
                    properties.append(data)
                    
            except Exception as e:
                print(f"Inmuebles24 scraping error: {e}")
            
            await browser.close()
        return properties
