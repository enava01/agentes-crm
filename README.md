# Real Estate & Commercial Search App

This is a responsive PWA that allows you to search for residential properties and identify commercial places within 5km. It includes two scrapers (Lamudi and Inmuebles24) and integrates with Google Maps APIs.

## Project Structure
- `backend/`: FastAPI server with scrapers and Google Maps utilities.
- `frontend/`: React + Vite + Tailwind CSS + PWA interface.

## Prerequisites
- Python 3.12+
- Node.js & npm
- Google Maps API Key (Geocoding & Places)

## Setup & Running

### 1. Backend
1. Go to the `backend` folder.
2. Activate the virtual environment: `source venv/bin/activate`
3. Set your Google Maps API Key: `export GOOGLE_MAPS_API_KEY=your_key_here`
4. Run the API: `python main.py`

### 2. Frontend
1. Go to the `frontend` folder.
2. Create a `.env` file: `echo "VITE_GOOGLE_MAPS_API_KEY=your_key_here" > .env`
3. Run the development server: `npm run dev` (or access via Docker at `http://localhost:8056`)

## Features
- **Dual Scraper**: Extracts data from Lamudi and Inmuebles24.
- **Geolocation**: identifies nearby commercial places (supermarkets, restaurants, etc.) within a 5km radius.
- **PWA**: Can be installed on mobile devices.
- **Modern UI**: Dark mode, glassmorphism, and responsive layout.
- **Anti-blocking**: Implements random delays and User-Agent rotation.
