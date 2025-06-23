# main.py
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from cachetools import TTLCache
from dotenv import load_dotenv

from models import TrendingResponse, Token
from scraper import scrape_trending_tokens

load_dotenv()

# --- NEW: Read allowed origins from environment variables ---
# We'll set this in Render's dashboard.
# It should be a comma-separated string like:
# "http://localhost:3000,https://your-production-site.com"
allowed_origins_str = os.getenv("ALLOWED_ORIGINS", "")
allowed_origins = [origin.strip() for origin in allowed_origins_str.split(',')]

# If no origins are specified, default to a safe value or log a warning.
# For development, you might want a default:
if not allowed_origins_str:
    print("WARNING: ALLOWED_ORIGINS environment variable not set. Defaulting to localhost.")
    allowed_origins = ["http://localhost:3000"]


app = FastAPI(
    title="CoinWorld Scraper API",
    description="API to scrape trending token data from Dexscreener.",
    version="1.0.0"
)

# --- UPDATED: Use the specific list of origins ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Hardcoded wildcard
    allow_credentials=False, # Set to False to make wildcard valid
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory cache: maxsize=10 (for 10 chains), ttl=1800s (30 minutes)
CACHE_TTL = int(os.getenv("CACHE_TTL_SECONDS", 1800))
cache = TTLCache(maxsize=10, ttl=CACHE_TTL)

@app.get(
    "/trending/{chain}",
    response_model=TrendingResponse,
    tags=["Tokens"],
    summary="Get trending tokens for a specific chain"
)
async def get_trending_tokens(chain: str):
    """
    Retrieves trending tokens for a given blockchain (e.g., 'solana').
    Results are cached for 30 minutes to avoid excessive scraping.
    """
    if chain in cache:
        print(f"Serving '{chain}' from cache.")
        return cache[chain]

    print(f"Cache miss for '{chain}'. Initiating scrape...")
    scraped_data = scrape_trending_tokens(chain)

    if not scraped_data:
        raise HTTPException(
            status_code=500,
            detail="Failed to scrape token data. The site structure may have changed or the service is temporarily unavailable."
        )

    # Validate and structure data using Pydantic models
    response = TrendingResponse(tokens=[Token(**data) for data in scraped_data])
    
    # Store the successful response in the cache
    cache[chain] = response
    print(f"Successfully scraped and cached data for '{chain}'.")
    
    return response

@app.get("/", tags=["Health"])
async def root():
    return {"message": "CoinWorld Scraper API is running."}