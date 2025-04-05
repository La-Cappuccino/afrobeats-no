"""
Afrobeats.no Agent System API

This module provides the FastAPI server for the Afrobeats.no Agent System,
handling query processing, caching, and interaction with the LLM-powered agent graph.

Key components:
- FastAPI server with CORS support and error handling
- Cache management for query responses
- AI provider management (Google Gemini and OpenAI)
- Health check and diagnostics endpoints
- Logging and monitoring

Author: Afrobeats.no Team
License: Proprietary and confidential
"""

#!/usr/bin/env python3
import os
import json
import logging
import uvicorn
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends, Request, Header, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from agent_graph import run_agent_graph, available_apis, ENABLE_CACHE, CACHE_EXPIRY_MINUTES
from pathlib import Path

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("api.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# API configuration
API_KEY = os.getenv("API_KEY")
PORT = int(os.getenv("PORT", "8000"))
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# Initialize FastAPI app
app = FastAPI(
    title="Afrobeats.no API",
    description="API for the Afrobeats.no multi-agent system",
    version="1.1.0"
)

# CORS configuration
origins = [
    "http://localhost:3000",   # Next.js development server
    "https://afrobeats.no",    # Production domain
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Models
class QueryRequest(BaseModel):
    query: str
    context: Optional[Dict[str, Any]] = None
    prefer_api: Optional[str] = Field(None, description="Preferred API to use: 'gemini', 'openrouter', 'perplexity', or 'openai'")
    bypass_cache: Optional[bool] = Field(False, description="Whether to bypass the cache and force a new API call")
    enable_search: Optional[bool] = Field(True, description="Whether to use Perplexity's search capabilities for up-to-date information")

class BookingRequest(BaseModel):
    dj_name: str
    date: str
    time: str
    hours: int
    venue: str
    details: Optional[str] = None

class EventRequest(BaseModel):
    title: str
    date: str
    time: str
    venue: str
    location: str
    description: str
    genres: List[str]
    ticket_price: Optional[float] = None
    ticket_link: Optional[str] = None
    featured: bool = False

class SystemInfoResponse(BaseModel):
    status: str
    timestamp: str
    environment: str
    available_apis: List[str]
    cache_enabled: bool
    cache_expiry_minutes: int
    version: str = "1.1.0"

# Security dependency
async def verify_api_key(x_api_key: str = Header(None)):
    if ENVIRONMENT == "development":
        return True

    if not API_KEY:
        logger.warning("API_KEY not set in .env file")
        return True

    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return True

# Mock data (replace with database integration later)
DJS = [
    {
        "id": 1,
        "name": "DJ Afro",
        "genres": ["Afrobeats", "Amapiano"],
        "rating": 4.8,
        "image": "/images/dj1.jpg",
        "bio": "Specialized in mixing the latest Afrobeats hits with classic tracks.",
        "hourly_rate": 150,
        "availability": ["Friday", "Saturday", "Sunday"]
    },
    {
        "id": 2,
        "name": "AmapianoQueen",
        "genres": ["Amapiano", "Afro House"],
        "rating": 4.9,
        "image": "/images/dj2.jpg",
        "bio": "Known for exceptional Amapiano sets that keep the dance floor packed.",
        "hourly_rate": 180,
        "availability": ["Thursday", "Friday", "Saturday"]
    },
    {
        "id": 3,
        "name": "Oslo Beats",
        "genres": ["Afrobeats", "Dancehall", "Hip Hop"],
        "rating": 4.6,
        "image": "/images/dj3.jpg",
        "bio": "Versatile DJ bringing a fusion of African and Caribbean sounds.",
        "hourly_rate": 160,
        "availability": ["Wednesday", "Friday", "Saturday"]
    }
]

EVENTS = [
    {
        "id": 1,
        "title": "Amapiano Night",
        "date": "2023-06-15",
        "time": "22:00",
        "venue": "Blå",
        "location": "Oslo, Norway",
        "image": "/images/event1.jpg",
        "genres": ["Amapiano"],
        "description": "A night dedicated to the sounds of Amapiano with our resident DJs.",
        "ticket_price": 150,
        "ticket_link": "https://tickets.example.com/amapiano-night",
        "featured": True
    },
    {
        "id": 2,
        "title": "Afrobeats Fusion",
        "date": "2023-06-22",
        "time": "21:00",
        "venue": "Jaeger",
        "location": "Oslo, Norway",
        "image": "/images/event2.jpg",
        "genres": ["Afrobeats", "Hip Hop"],
        "description": "Blending Afrobeats with Hip Hop for a unique dance experience.",
        "ticket_price": 180,
        "ticket_link": "https://tickets.example.com/afrobeats-fusion",
        "featured": True
    }
]

# API Endpoints
@app.get("/")
async def root():
    return {"message": "Welcome to the Afrobeats.no API", "status": "operational"}

@app.get("/health", response_model=SystemInfoResponse)
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "environment": ENVIRONMENT,
        "available_apis": available_apis,
        "cache_enabled": ENABLE_CACHE,
        "cache_expiry_minutes": CACHE_EXPIRY_MINUTES,
        "version": "1.1.0"
    }

@app.post("/query", dependencies=[Depends(verify_api_key)])
async def process_query(request: QueryRequest):
    try:
        logger.info(f"Processing query: {request.query}")

        # Extract advanced options
        options = {
            "prefer_api": request.prefer_api,
            "bypass_cache": request.bypass_cache,
            "enable_search": request.enable_search
        }

        # Log options when they're specified
        if any(v is not None for v in options.values()):
            logger.info(f"Advanced options: {options}")

        # Call the multi-agent system with options
        result = run_agent_graph(request.query, options=options)

        response = {
            "response": result["final_response"],
            "timestamp": datetime.now().isoformat(),
            "processing_time": result["processing_time"],
            "agents_used": result["selected_agents"]
        }

        # Add information about whether the response came from cache
        if "from_cache" in result and result["from_cache"]:
            response["from_cache"] = True

        # Add information about which API was used if available
        if "api_used" in result:
            response["api_used"] = result["api_used"]

        return response
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@app.post("/query/no-cache", dependencies=[Depends(verify_api_key)])
async def process_query_no_cache(request: QueryRequest):
    """Endpoint that forces bypassing the cache for fresh results"""
    request.bypass_cache = True
    return await process_query(request)

@app.post("/query/realtime", dependencies=[Depends(verify_api_key)])
async def process_query_realtime(request: QueryRequest):
    """Endpoint that forces using Perplexity for up-to-date information with search enabled"""
    request.prefer_api = "perplexity"
    request.bypass_cache = True
    request.enable_search = True
    return await process_query(request)

@app.get("/djs", dependencies=[Depends(verify_api_key)])
async def get_djs(
    genres: Optional[str] = None,
    min_rating: Optional[float] = None,
    availability: Optional[str] = None
):
    try:
        filtered_djs = DJS.copy()

        # Apply filters
        if genres:
            genre_list = genres.split(',')
            filtered_djs = [dj for dj in filtered_djs if any(g in dj["genres"] for g in genre_list)]

        if min_rating:
            filtered_djs = [dj for dj in filtered_djs if dj["rating"] >= float(min_rating)]

        if availability:
            day_list = availability.split(',')
            filtered_djs = [dj for dj in filtered_djs if any(d in dj["availability"] for d in day_list)]

        return {"djs": filtered_djs}
    except Exception as e:
        logger.error(f"Error retrieving DJs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving DJs: {str(e)}")

@app.get("/djs/{dj_id}", dependencies=[Depends(verify_api_key)])
async def get_dj(dj_id: int):
    try:
        dj = next((dj for dj in DJS if dj["id"] == dj_id), None)
        if not dj:
            raise HTTPException(status_code=404, detail=f"DJ with ID {dj_id} not found")
        return dj
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving DJ: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving DJ: {str(e)}")

@app.post("/bookings", dependencies=[Depends(verify_api_key)])
async def create_booking(booking: BookingRequest):
    try:
        logger.info(f"New booking request for {booking.dj_name}")

        # TODO: Integrate with database
        # For now, simulate a successful booking

        return {
            "message": f"Booking request for {booking.dj_name} received successfully",
            "booking_id": "BK" + datetime.now().strftime("%Y%m%d%H%M%S"),
            "status": "pending",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error creating booking: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating booking: {str(e)}")

@app.get("/events", dependencies=[Depends(verify_api_key)])
async def get_events(
    genres: Optional[str] = None,
    featured: Optional[bool] = None
):
    try:
        filtered_events = EVENTS.copy()

        # Apply filters
        if genres:
            genre_list = genres.split(',')
            filtered_events = [event for event in filtered_events if any(g in event["genres"] for g in genre_list)]

        if featured is not None:
            filtered_events = [event for event in filtered_events if event["featured"] == featured]

        return {"events": filtered_events}
    except Exception as e:
        logger.error(f"Error retrieving events: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving events: {str(e)}")

@app.get("/events/{event_id}", dependencies=[Depends(verify_api_key)])
async def get_event(event_id: int):
    try:
        event = next((event for event in EVENTS if event["id"] == event_id), None)
        if not event:
            raise HTTPException(status_code=404, detail=f"Event with ID {event_id} not found")
        return event
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving event: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving event: {str(e)}")

@app.post("/events", dependencies=[Depends(verify_api_key)])
async def create_event(event: EventRequest):
    try:
        logger.info(f"New event creation request: {event.title}")

        # TODO: Integrate with database
        # For now, simulate a successful event creation

        # Generate a new event ID
        new_id = max(e["id"] for e in EVENTS) + 1

        return {
            "message": f"Event '{event.title}' created successfully",
            "event_id": new_id,
            "status": "active",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error creating event: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating event: {str(e)}")

@app.get("/cache/stats", dependencies=[Depends(verify_api_key)])
async def get_cache_stats():
    """Get information about the caching system"""
    try:
        # Get cache directory and list files
        import os
        from agent_graph import cache_directory

        if not os.path.exists(cache_directory):
            return {
                "enabled": ENABLE_CACHE,
                "expiry_minutes": CACHE_EXPIRY_MINUTES,
                "cache_count": 0,
                "cache_size_kb": 0,
                "timestamp": datetime.now().isoformat()
            }

        cache_files = [f for f in os.listdir(cache_directory) if f.endswith('.json')]
        cache_size = sum(os.path.getsize(os.path.join(cache_directory, f)) for f in cache_files) / 1024  # KB

        return {
            "enabled": ENABLE_CACHE,
            "expiry_minutes": CACHE_EXPIRY_MINUTES,
            "cache_count": len(cache_files),
            "cache_size_kb": round(cache_size, 2),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting cache stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting cache stats: {str(e)}")

@app.post("/cache/clear", dependencies=[Depends(verify_api_key)])
async def clear_cache():
    """Clear all cached responses"""
    try:
        import os
        import shutil
        from agent_graph import cache_directory

        if os.path.exists(cache_directory):
            # Count files before deletion
            cache_files = [f for f in os.listdir(cache_directory) if f.endswith('.json')]
            file_count = len(cache_files)

            # Delete all files in the cache directory
            for filename in cache_files:
                file_path = os.path.join(cache_directory, filename)
                try:
                    os.unlink(file_path)
                except Exception as e:
                    logger.error(f"Error deleting {file_path}: {str(e)}")

            return {
                "message": f"Successfully cleared {file_count} cache entries",
                "timestamp": datetime.now().isoformat()
            }
        return {
            "message": "Cache directory not found or no cache entries to clear",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error clearing cache: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error clearing cache: {str(e)}")

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"error": f"An unexpected error occurred: {str(exc)}"}
    )

# Start the server if running directly
if __name__ == "__main__":
    logger.info(f"Starting Afrobeats.no API server on port {PORT}")
    logger.info(f"Environment: {ENVIRONMENT}")
    uvicorn.run("api:app", host="0.0.0.0", port=PORT, reload=True)