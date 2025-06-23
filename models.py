# models.py
from pydantic import BaseModel
from typing import List

# FastAPI automatically converts snake_case to camelCase in JSON responses,
# so our Nuxt app can consume it without changes.

class Volume(BaseModel):
    h24: float

class PriceChange(BaseModel):
    h24: float

class Token(BaseModel):
    id: str  # The pair address
    tokenAddress: str
    name: str
    symbol: str
    marketCap: float
    priceUsd: float
    volume: Volume
    priceChange: PriceChange
    pairAge: str

class TrendingResponse(BaseModel):
    tokens: List[Token]