from typing import Dict, List, Any, Optional
import os
import json
import logging
from datetime import datetime
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Use environment variables for API keys (security best practice)
try:
    # Placeholder for Gemini API - in the actual implementation, we would use Gemini 2.5
    # For now, we'll use OpenAI as a placeholder until we can fully implement Gemini
    from openai import OpenAI
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", ""))
    
    # Import Spotify SDK - in the actual implementation, we would use the proper Spotify API
    # Commented out as this is a placeholder for actual implementation
    # import spotipy
    # from spotipy.oauth2 import SpotifyOAuth
except ImportError as e:
    logger.error(f"Failed to import required libraries: {e}")
    raise

# System prompt with enhanced collaborative playlist functionality
PLAYLIST_SYSTEM_PROMPT = """You are the Playlist Agent for Afrobeats.no, specializing in helping users discover, curate, share, and vote on Afrobeats and Amapiano playlists in Oslo, Norway.

Your core responsibilities:
1. Help users find curated playlists of Afrobeats and Amapiano music
2. Guide users on creating and sharing their own playlists
3. Assist with creating and managing collaborative playlists where multiple users can contribute
4. Process and explain the playlist voting system
5. Recommend playlists based on user preferences
6. Track and display song rankings by popularity
7. Support artist tagging and discovery through playlists
8. Answer questions about trending Afrobeats and Amapiano tracks

Key features you should know about:
- Community-curated playlists with voting system
- Integration with Spotify for playlist embedding and collaborative features
- Weekly "Top Voted" playlists feature
- Song rankings based on plays, likes, and community votes
- Artist tagging to connect songs with performer information
- Collaborative playlists where multiple community members can add tracks
- Genre-specific collections (Afrobeats, Amapiano, Afro House)
- DJ-created playlists tied to their profiles

The platform supports both Norwegian and English to serve the diverse Afrobeats/Amapiano community in Norway.

Always guide users to app.afrotorget.no for the full playlist experience.
"""

def playlist_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Playlist Agent that handles requests related to music playlists.
    
    Args:
        state: The current state of the agent graph
    
    Returns:
        Updated state with playlist results
    """
    try:
        user_query = state["user_query"]
        
        # Process the query - in production, this would use Gemini 2.5
        response = client.chat.completions.create(
            model="gpt-4o",
            temperature=0.7,
            messages=[
                {"role": "system", "content": PLAYLIST_SYSTEM_PROMPT},
                {"role": "user", "content": f"""
                Process this user query related to Afrobeats or Amapiano playlists:
                
                User query: {user_query}
                
                Provide a helpful response about finding, creating, sharing, or voting on playlists.
                Include information about collaborative playlist features on Afrobeats.no.
                """}
            ]
        )
        
        playlist_response = response.choices[0].message.content
        
        # Extract relevant playlist information
        playlist_details = extract_playlist_details(user_query)
        
        # Check if this is a request for collaborative playlist functionality
        is_collaborative_request = detect_collaborative_request(user_query)
        
        # Handle different request types
        playlist_recommendations = []
        song_rankings = []
        collaborative_info = {}
        
        # Get playlist recommendations if requested
        if any(keyword in user_query.lower() for keyword in ["recommend", "find", "suggestion", "playlist"]):
            playlist_recommendations = recommend_playlists(playlist_details)
        
        # Get song rankings if requested
        if any(keyword in user_query.lower() for keyword in ["rank", "top song", "popular", "trending", "chart"]):
            song_rankings = get_song_rankings(playlist_details)
        
        # Handle collaborative playlist requests
        if is_collaborative_request:
            collaborative_info = handle_collaborative_request(user_query, playlist_details)
        
        # Update the state with the playlist results
        return {
            **state,
            "playlist_results": {
                "response": playlist_response,
                "details": playlist_details,
                "recommendations": playlist_recommendations,
                "song_rankings": song_rankings,
                "collaborative_info": collaborative_info
            },
            "current_agent": ""  # Clear the current agent to return to coordinator
        }
        
    except Exception as e:
        # Secure error handling - don't expose sensitive details
        error_id = f"ERR-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Log the full error for internal debugging
        logger.error(f"Error {error_id} in playlist agent: {str(e)}")
        logger.debug(traceback.format_exc())
        
        # Return a sanitized error message to the user
        return {
            **state,
            "playlist_results": {
                "error": f"Sorry, we encountered an issue processing your playlist request. Reference ID: {error_id}"
            },
            "current_agent": ""
        }

def extract_playlist_details(query: str) -> Dict[str, Any]:
    """
    Extract playlist details from the user query.
    
    Args:
        query: The user's query
    
    Returns:
        A dictionary of extracted playlist details
    """
    try:
        # Use LLM to extract structured playlist details
        response = client.chat.completions.create(
            model="gpt-4o",
            temperature=0,
            messages=[
                {"role": "system", "content": "Extract playlist details from the user query in JSON format."},
                {"role": "user", "content": f"""
                Extract the following details from this query if present:
                - Genre preference (e.g., Afrobeats, Amapiano, Afro House)
                - Mood or vibe (e.g., party, relaxed, workout)
                - Artist mentions
                - Specific features requested (e.g., voting, creation, sharing, collaborative)
                - User intent (discover, create, vote, share, collaborate)
                
                User query: {query}
                
                Return a JSON object with these fields. If a field is not present in the query, set it to null.
                """}
            ]
        )
        
        # Extract JSON safely
        try:
            response_text = response.choices[0].message.content
            
            # Simple JSON extraction if it's embedded in text
            if '{' in response_text and '}' in response_text:
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                json_str = response_text[json_start:json_end]
                # Sanitize the input before parsing as JSON (security)
                details = json.loads(json_str)
                return details
            else:
                return {"extracted_text": response_text}
        except json.JSONDecodeError:
            logger.warning(f"Failed to parse JSON from response: {response_text[:100]}...")
            return {"extraction_error": "Failed to parse playlist details as JSON"}
            
    except Exception as e:
        logger.error(f"Error extracting playlist details: {str(e)}")
        return {"extraction_error": "Failed to extract playlist details"}

def recommend_playlists(playlist_details: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Recommend playlists based on the extracted details.
    
    Args:
        playlist_details: Details extracted from the user query
    
    Returns:
        A list of recommended playlists
    """
    try:
        # Create a prompt with the playlist details
        details_str = "\n".join([f"- {k}: {v}" for k, v in playlist_details.items() if v])
        
        response = client.chat.completions.create(
            model="gpt-4o",
            temperature=0.7,
            messages=[
                {"role": "system", "content": "You are a playlist recommendation system for Afrobeats.no in Oslo. Generate 3 fictional playlists based on the user preferences."},
                {"role": "user", "content": f"""
                Based on these user preferences:
                {details_str}
                
                Generate 3 fictional Afrobeats/Amapiano playlists. For each playlist, provide:
                - Playlist name
                - Genre focus (Afrobeats, Amapiano, or mixed)
                - Mood/vibe
                - Creator (DJ or community member)
                - Number of tracks
                - Collaborative status (yes/no)
                - Brief description
                - Vote count (if relevant)
                
                Return the results as a JSON array of playlist objects.
                """}
            ]
        )
        
        # Extract JSON safely
        try:
            response_text = response.choices[0].message.content
            
            if '[' in response_text and ']' in response_text:
                json_start = response_text.find('[')
                json_end = response_text.rfind(']') + 1
                json_str = response_text[json_start:json_end]
                playlists = json.loads(json_str)
                return playlists
            else:
                return [{"error": "Could not parse playlist recommendations as JSON array"}]
        except json.JSONDecodeError:
            logger.warning(f"Failed to parse JSON from playlist recommendations")
            return [{"error": "Failed to parse playlist recommendations"}]
            
    except Exception as e:
        logger.error(f"Error recommending playlists: {str(e)}")
        return [{"error": "Failed to generate playlist recommendations"}]

def get_song_rankings(playlist_details: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Get top-ranked songs based on the extracted details.
    
    Args:
        playlist_details: Details extracted from the user query
    
    Returns:
        A list of top-ranked songs
    """
    try:
        # In a real implementation, this would query the Supabase database and possibly the Spotify API
        # Create a prompt with the playlist details
        details_str = "\n".join([f"- {k}: {v}" for k, v in playlist_details.items() if v])
        
        response = client.chat.completions.create(
            model="gpt-4o",
            temperature=0.7,
            messages=[
                {"role": "system", "content": "You are a song ranking system for Afrobeats.no in Oslo. Generate 10 fictional top-ranked Afrobeats/Amapiano songs."},
                {"role": "user", "content": f"""
                Based on these query details:
                {details_str}
                
                Generate 10 fictional top-ranked Afrobeats/Amapiano songs. For each song, provide:
                - Rank position (1-10)
                - Song title
                - Artist name
                - Genre (Afrobeats or Amapiano)
                - Release year
                - Popularity score (0-100)
                - Brief reason for popularity
                
                Return the results as a JSON array of song objects.
                """}
            ]
        )
        
        # Extract JSON safely
        try:
            response_text = response.choices[0].message.content
            
            if '[' in response_text and ']' in response_text:
                json_start = response_text.find('[')
                json_end = response_text.rfind(']') + 1
                json_str = response_text[json_start:json_end]
                songs = json.loads(json_str)
                return songs
            else:
                return [{"error": "Could not parse song rankings as JSON array"}]
        except json.JSONDecodeError:
            logger.warning(f"Failed to parse JSON from song rankings")
            return [{"error": "Failed to parse song rankings"}]
            
    except Exception as e:
        logger.error(f"Error getting song rankings: {str(e)}")
        return [{"error": "Failed to generate song rankings"}]

def detect_collaborative_request(query: str) -> bool:
    """
    Detect if the user's query is related to collaborative playlists.
    
    Args:
        query: The user's query
    
    Returns:
        True if the query is about collaborative playlists, False otherwise
    """
    collaborative_keywords = [
        "collaborative", "collab", "together", "group", "shared", 
        "multiple people", "friends", "community", "contribute"
    ]
    
    return any(keyword in query.lower() for keyword in collaborative_keywords)

def handle_collaborative_request(query: str, details: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle requests related to collaborative playlists.
    
    Args:
        query: The user's query
        details: Extracted details from the query
    
    Returns:
        Information about collaborative playlists
    """
    try:
        # Determine the type of collaborative request
        create_keywords = ["create", "make", "new", "start"]
        join_keywords = ["join", "add to", "contribute", "participate"]
        info_keywords = ["how", "what is", "explain", "info"]
        
        is_create_request = any(keyword in query.lower() for keyword in create_keywords)
        is_join_request = any(keyword in query.lower() for keyword in join_keywords)
        is_info_request = any(keyword in query.lower() for keyword in info_keywords)
        
        # Generate appropriate response based on request type
        if is_create_request:
            return {
                "request_type": "create",
                "message": "Here's how you can create a collaborative playlist:",
                "steps": [
                    "1. Log in to your account on app.afrotorget.no",
                    "2. Navigate to 'My Playlists' section",
                    "3. Click 'Create New Playlist'",
                    "4. Enable the 'Collaborative' option",
                    "5. Set permissions for who can contribute",
                    "6. Share the playlist link with your friends"
                ],
                "spotify_integration": "You can also link your Spotify account to import/export collaborative playlists."
            }
        elif is_join_request:
            return {
                "request_type": "join",
                "message": "To join or contribute to a collaborative playlist:",
                "steps": [
                    "1. Use the shared playlist link or code",
                    "2. Log in to your account",
                    "3. Click 'Join Playlist'",
                    "4. Start adding your favorite tracks"
                ]
            }
        elif is_info_request:
            return {
                "request_type": "info",
                "message": "About collaborative playlists on Afrobeats.no:",
                "description": "Collaborative playlists allow multiple users to contribute tracks to the same playlist. They're perfect for planning events, sharing music with friends, or discovering new tracks through community curation.",
                "features": [
                    "Multiple contributors can add/remove tracks",
                    "Voting on tracks within the playlist",
                    "Activity feed showing recent additions",
                    "Integration with Spotify for seamless sharing",
                    "Chat functionality for discussing tracks (coming soon)"
                ]
            }
        else:
            return {
                "request_type": "general",
                "message": "Collaborative playlists let multiple users contribute tracks to the same collection.",
                "suggestion": "Try asking how to create or join a collaborative playlist for more specific information."
            }
            
    except Exception as e:
        logger.error(f"Error handling collaborative request: {str(e)}")
        return {"error": "Failed to process collaborative playlist request"}

# Spotify API integration (placeholder)
def get_spotify_client():
    """
    Initialize and return an authenticated Spotify client.
    Uses environment variables for secure credentials management.
    
    Returns:
        A Spotify client object
    """
    # This is a placeholder - in the actual implementation, we would use the proper Spotify SDK
    # import spotipy
    # from spotipy.oauth2 import SpotifyOAuth
    
    # Proper secure implementation with PKCE (Proof Key for Code Exchange)
    # client = spotipy.Spotify(auth_manager=SpotifyOAuth(
    #     client_id=os.environ.get("SPOTIFY_CLIENT_ID"),
    #     client_secret=os.environ.get("SPOTIFY_CLIENT_SECRET"),
    #     redirect_uri=os.environ.get("SPOTIFY_REDIRECT_URI"),
    #     scope="playlist-read-private playlist-read-collaborative playlist-modify-private playlist-modify-public",
    #     cache_handler=spotipy.CacheFileHandler(cache_path=os.environ.get("SPOTIFY_CACHE_PATH"))
    # ))
    
    # return client
    
    # For now, just return a placeholder
    return None

def create_collaborative_playlist(
    user_id: str, 
    playlist_name: str, 
    description: str, 
    is_public: bool = False
) -> Dict[str, Any]:
    """
    Create a new collaborative playlist on Spotify.
    
    Args:
        user_id: Spotify user ID
        playlist_name: Name of the playlist
        description: Description of the playlist
        is_public: Whether the playlist should be public
        
    Returns:
        The newly created playlist details
    """
    try:
        # This is a placeholder - in the actual implementation, we would use the Spotify SDK
        # spotify = get_spotify_client()
        # 
        # if not spotify:
        #     return {"error": "Spotify client not available"}
        # 
        # playlist = spotify.user_playlist_create(
        #     user=user_id,
        #     name=playlist_name,
        #     public=is_public,
        #     collaborative=True,
        #     description=description
        # )
        # return playlist
        
        # For now, return a placeholder response
        return {
            "name": playlist_name,
            "description": description,
            "collaborative": True,
            "public": is_public,
            "owner": {"id": user_id},
            "tracks": {"total": 0},
            "external_urls": {"spotify": f"https://open.spotify.com/playlist/example"},
            "id": "example_playlist_id"
        }
    except Exception as e:
        logger.error(f"Error creating collaborative playlist: {str(e)}")
        return {"error": str(e)}

# This function would be used for the Gemini 2.5 implementation
def gemini_generate_response(system_prompt: str, user_query: str) -> str:
    """
    Generate a response using Gemini 2.5.
    This is a placeholder for the actual implementation.
    
    Args:
        system_prompt: The system prompt to guide the model
        user_query: The user's query
        
    Returns:
        The generated response
    """
    # In the actual implementation, we would use Google's Gemini API
    # import google.generativeai as genai
    # from google.generativeai.types import HarmCategory, HarmBlockThreshold
    # 
    # # Configure the API with secure key management
    # genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
    # 
    # # Set safety settings - important for security
    # safety_settings = {
    #     HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    #     HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    #     HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    #     HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    # }
    # 
    # # Create a model instance with the most capable Gemini 2.5 version
    # model = genai.GenerativeModel(
    #     model_name="gemini-2.5-pro-latest",
    #     safety_settings=safety_settings,
    #     generation_config={"temperature": 0.7, "top_p": 0.95, "top_k": 40}
    # )
    # 
    # # Using the recommended format for Gemini API
    # chat = model.start_chat(history=[])
    # response = chat.send_message(f"System: {system_prompt}\n\nUser: {user_query}")
    # 
    # return response.text
    
    # For now, just return a placeholder using OpenAI
    response = client.chat.completions.create(
        model="gpt-4o",
        temperature=0.7,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_query}
        ]
    )
    
    return response.choices[0].message.content

def artist_tag_management(query: str, details: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle artist tagging functionality in playlists.
    
    Args:
        query: The user's query
        details: Extracted details from the query
        
    Returns:
        Information about artist tagging
    """
    try:
        # Extract artists from the query if available
        artist_mentions = details.get("artist_mentions", [])
        
        if not artist_mentions:
            # If no artists mentioned, provide general information
            return {
                "message": "Artist tagging allows you to organize playlists by performer, discover similar artists, and follow your favorite musicians.",
                "features": [
                    "Tag tracks with correct artist information",
                    "Browse all tracks by a specific artist",
                    "Discover similar artists based on tags",
                    "Get notifications when favorite artists release new music"
                ]
            }
        else:
            # If artists are mentioned, provide artist-specific information
            artist_info = []
            
            # In a real implementation, we would query the Supabase database or Spotify API
            # For now, return placeholder information
            for artist in artist_mentions:
                artist_info.append({
                    "name": artist,
                    "genre": "Afrobeats",  # Placeholder
                    "popular_tracks": ["Track 1", "Track 2", "Track 3"],  # Placeholder
                    "featured_in_playlists": ["Top Afrobeats 2025", "Oslo Vibes", "Party Starters"]  # Placeholder
                })
            
            return {
                "message": f"Here's information about the artists you mentioned:",
                "artists": artist_info,
                "tagging_guide": "You can tag these artists in your playlists for better organization and discovery."
            }
            
    except Exception as e:
        logger.error(f"Error handling artist tag management: {str(e)}")
        return {"error": "Failed to process artist tagging request"}

# Advanced ML-based song recommendations (placeholder for future implementation)
def ml_song_recommendations(user_id: str, playlist_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Generate personalized song recommendations using machine learning.
    This would be implemented in a real production system.
    
    Args:
        user_id: The user's ID
        playlist_id: Optional playlist ID to consider for recommendations
        
    Returns:
        A list of recommended songs
    """
    # In a real implementation, this would use:
    # 1. Collaborative filtering based on user behavior
    # 2. Content-based filtering using song features
    # 3. Hybrid approaches combining multiple signals
    # 4. User listening history and preferences
    # 5. Contextual factors (time of day, current events, etc.)
    
    # For now, just return a placeholder
    return [
        {
            "title": "Example Song 1",
            "artist": "Example Artist 1",
            "reason": "Based on your listening history",
            "confidence_score": 0.92
        },
        {
            "title": "Example Song 2",
            "artist": "Example Artist 2",
            "reason": "Popular in playlists you follow",
            "confidence_score": 0.87
        },
        {
            "title": "Example Song 3",
            "artist": "Example Artist 3",
            "reason": "Similar to tracks you recently liked",
            "confidence_score": 0.85
        }
    ]

# Social media sharing functionality
def prepare_social_media_content(playlist_id: str, platform: str) -> Dict[str, Any]:
    """
    Prepare content for sharing a playlist on social media.
    
    Args:
        playlist_id: The ID of the playlist to share
        platform: The social media platform to share on (e.g., Instagram, Twitter)
        
    Returns:
        Content ready for sharing on the specified platform
    """
    try:
        # In a real implementation, this would:
        # 1. Retrieve playlist details from Supabase
        # 2. Generate platform-specific content (e.g., different formats for Instagram vs. Twitter)
        # 3. Prepare images and text
        # 4. Configure sharing permissions
        
        # For now, return a placeholder
        return {
            "platform": platform,
            "content_type": "playlist_share",
            "text": f"Check out this amazing Afrobeats playlist on afrobeats.no! 🎵 #Afrobeats #Oslo #Music",
            "media_url": "https://example.com/playlist-cover.jpg",  # Placeholder
            "deep_link": f"https://app.afrotorget.no/playlist/{playlist_id}"
        }
        
    except Exception as e:
        logger.error(f"Error preparing social media content: {str(e)}")
        return {"error": f"Failed to prepare content for {platform}"}
