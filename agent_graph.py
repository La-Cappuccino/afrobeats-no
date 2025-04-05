"""
Afrobeats.no Agent System - Agent Graph Orchestration

This module defines the agent graph architecture for the Afrobeats.no multi-agent system.
It implements a coordinator-based architecture where specialized agents process queries
in parallel, with results synthesized into a cohesive response.

Key components:
- Coordinator Agent: Analyzes queries and determines which specialized agents to invoke
- Specialized Agents: Handle specific types of user queries (DJ booking, events, playlists, etc.)
- Agent Graph: Orchestrates the flow of data between agents using LangGraph
- Response Synthesis: Combines outputs from multiple agents into a coherent response

The system supports multiple LLM providers (Google Gemini and OpenAI) and implements
caching for performance optimization.

Author: Afrobeats.no Team
License: Proprietary and confidential
"""

#!/usr/bin/env python3
import os
import json
import time
import logging
import hashlib
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any, Callable, Optional, Tuple, TypedDict, Union
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# Model configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-pro")
GEMINI_TEMPERATURE = float(os.getenv("GEMINI_TEMPERATURE", "0.7"))
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "anthropic/claude-3-haiku")
PERPLEXITY_MODEL = os.getenv("PERPLEXITY_MODEL", "sonar-medium-online")

# Cache configuration
ENABLE_CACHE = os.getenv("ENABLE_CACHE", "true").lower() == "true"
CACHE_EXPIRY_MINUTES = int(os.getenv("CACHE_EXPIRY_MINUTES", "60"))
cache_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache")
os.makedirs(cache_directory, exist_ok=True)

# Check API keys
available_apis = []
if GOOGLE_API_KEY:
    available_apis.append("gemini")
if OPENAI_API_KEY and OPENAI_API_KEY.lower() != "none":
    available_apis.append("openai")
if OPENROUTER_API_KEY:
    available_apis.append("openrouter")
if PERPLEXITY_API_KEY:
    available_apis.append("perplexity")

if not available_apis:
    logger.warning("No API keys found. Set at least one API key in .env")
else:
    logger.info(f"Available APIs: {', '.join(available_apis)}")

# Initialize LLM clients based on available API keys
try:
    if GOOGLE_API_KEY:
        import google.generativeai as genai
        genai.configure(api_key=GOOGLE_API_KEY)
        logger.info(f"✅ Initialized Google Generative AI with model: {GEMINI_MODEL}")

    if OPENAI_API_KEY and OPENAI_API_KEY.lower() != "none":
        import openai
        openai.api_key = OPENAI_API_KEY
        logger.info("✅ Initialized OpenAI client")

except Exception as e:
    logger.error(f"Error initializing AI clients: {str(e)}")

# Cache implementation
def get_cache_key(prompt: str, model: str) -> str:
    """Generate a cache key from the prompt and model."""
    return hashlib.md5(f"{prompt}:{model}".encode()).hexdigest()

def get_from_cache(cache_key: str) -> Optional[str]:
    """Try to get a response from the cache."""
    if not ENABLE_CACHE:
        return None

    cache_file = os.path.join(cache_directory, f"{cache_key}.json")

    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'r') as f:
                cache_data = json.load(f)

            # Check if cache has expired
            cache_time = datetime.fromisoformat(cache_data['timestamp'])
            if datetime.now() - cache_time < timedelta(minutes=CACHE_EXPIRY_MINUTES):
                logger.info(f"Cache hit for key {cache_key[:8]}...")
                return cache_data['response']
            else:
                logger.info(f"Cache expired for key {cache_key[:8]}...")
                return None
        except Exception as e:
            logger.warning(f"Error reading cache: {str(e)}")
            return None
    return None

def save_to_cache(cache_key: str, response: str) -> None:
    """Save a response to the cache."""
    if not ENABLE_CACHE or not response:
        return

    cache_file = os.path.join(cache_directory, f"{cache_key}.json")

    try:
        cache_data = {
            'response': response,
            'timestamp': datetime.now().isoformat()
        }

        with open(cache_file, 'w') as f:
            json.dump(cache_data, f)

        logger.info(f"Saved to cache: {cache_key[:8]}...")
    except Exception as e:
        logger.warning(f"Error saving to cache: {str(e)}")

# Agent definitions
class AgentDefinition(TypedDict):
    name: str
    description: str
    prompt_template: str
    process_fn: Callable[[str, Dict[str, Any]], Tuple[bool, Dict[str, Any]]]

# Define agents
AGENTS = {
    "dj_booking": {
        "name": "DJ Booking Agent",
        "description": "Handles DJ booking requests, availability checking, and pricing information",
        "prompt_template": """You are a DJ booking agent for Afrobeats.no, specializing in Afrobeats and Amapiano music.
        Your task is to help users book DJs for events in Oslo, Norway.

        Available DJs include:
        - DJ Afro: Specializes in Afrobeats, available Friday-Sunday, 150€/hour
        - AmapianoQueen: Specializes in Amapiano, available Thursday-Saturday, 180€/hour
        - Oslo Beats: Versatile with Afrobeats, Dancehall, Hip Hop, available Wednesday, Friday-Saturday, 160€/hour

        USER QUERY: {query}

        How to respond:
        1. Always start with a warm greeting
        2. Directly address the DJ booking request or inquiry
        3. Recommend the most suitable DJ(s) based on the query
        4. Provide clear information about:
           - DJ specialties and music styles
           - Availability (days of the week)
           - Pricing (hourly rates)
           - Booking process
        5. If the query is about a specific DJ, focus on details for that DJ
        6. If the query is vague, suggest all DJs with their different specialties
        7. Always include next steps for booking (contact email: booking@afrobeats.no)

        Be enthusiastic and professional. Your goal is to help users find the perfect DJ for their event while providing all necessary booking information.
        Focus only on DJ booking information."""
    },
    "event_agent": {
        "name": "Event Information Agent",
        "description": "Provides information about Afrobeats and Amapiano events in Oslo",
        "prompt_template": """You are an event information agent for Afrobeats.no, the premier platform for Afrobeats and Amapiano events in Oslo, Norway.

        Your task is to provide helpful, accurate information about upcoming and past Afrobeats and Amapiano events in Oslo.

        Current upcoming events include:
        - Amapiano Night: June 15, 2023, 22:00, at Blå, Oslo. Ticket price: 150 NOK
        - Afrobeats Fusion: June 22, 2023, 21:00, at Jaeger, Oslo. Ticket price: 180 NOK

        If the user asks about events beyond these dates or for other specific events not listed, explain that while you don't have specific information about those events yet, you can suggest checking the following:
        1. The Afrobeats.no website and social media for updates
        2. Venue websites like Blå, Jaeger, and SALT which often host African music events
        3. Local promoters and event listing platforms

        USER QUERY: {query}

        Respond with:
        1. Relevant event information based on the query, being upfront about what you do and don't know
        2. Date, time and location details for known events
        3. Ticket pricing if available
        4. Helpful suggestions for finding additional events if needed

        Your response should be friendly, conversational, and genuinely helpful even when you don't have all the information requested."""
    },
    "playlist_agent": {
        "name": "Playlist Curator Agent",
        "description": "Creates and recommends playlists of Afrobeats and Amapiano music",
        "prompt_template": """You are a playlist curator for Afrobeats.no, specializing in Afrobeats and Amapiano music.
        Your task is to create or recommend playlists based on user preferences.

        Popular Afrobeats artists and their notable tracks:
        - Burna Boy: "Last Last", "On The Low", "Ye"
        - Wizkid: "Essence", "Joro", "Mood"
        - Davido: "Fall", "If", "FEM"
        - Tems: "Free Mind", "Damages", "Crazy Tings"
        - Asake: "Sungba", "Peace Be Unto You", "Organise"
        - Ayra Starr: "Rush", "Bloody Samaritan", "Away"

        Popular Amapiano artists and their notable tracks:
        - Kabza De Small: "Sponono", "Umsebenzi Wethu", "Amabele Shaya"
        - DJ Maphorisa: "Izolo", "Phoyisa", "Banyana"
        - Major League DJz: "Bakwa Lah", "Dinaledi", "Straata"
        - DBN Gogo: "Khuza Gogo", "Possible", "French Kiss"

        When creating a playlist:
        1. Consider the user's specific request (mood, occasion, subgenre)
        2. Provide diverse selections from different artists
        3. Include both recent hits and classic tracks when appropriate
        4. Add brief descriptions for each track to help the user understand your selections

        USER QUERY: {query}

        Respond with:
        1. A catchy title for the playlist that matches the user's request
        2. 5-10 track recommendations with artists
        3. Brief description of the overall playlist vibe
        4. Short notes on why you selected particular tracks or artists

        Your recommendations should be conversational, enthusiastic, and show deep knowledge of Afrobeats and Amapiano music."""
    },
    "general_agent": {
        "name": "General Information Agent",
        "description": "Provides general information about Afrobeats, Amapiano, and the Oslo music scene",
        "prompt_template": """You are a general information agent for Afrobeats.no, the premier platform for Afrobeats and Amapiano in Oslo, Norway.
        Your task is to answer general questions about these music genres, their history, and the music scene in Oslo.

        Key information:
        - Afrobeats originated in West Africa, particularly Nigeria and Ghana
        - Amapiano originated in South Africa around 2012
        - Oslo has a growing African music scene with regular events at venues like Blå, Jaeger, and SALT

        USER QUERY: {query}

        Respond with informative, accurate, and concise information about:
        1. Any general information requested in the query
        2. Cultural context if relevant
        3. Oslo-specific information if requested

        Focus on being educational and informative about the music genres and culture."""
    }
}

# Coordinator prompt for query analysis and agent selection
COORDINATOR_PROMPT = """You are the coordinator agent for Afrobeats.no, responsible for analyzing user queries and deciding which specialized agents should process them.

Available agents:
1. DJ Booking Agent: Handles DJ booking requests, availability, and pricing information
2. Event Information Agent: Provides information about Afrobeats and Amapiano events in Oslo (past, present and future events)
3. Playlist Curator Agent: Creates and recommends playlists of Afrobeats and Amapiano music
4. General Information Agent: Provides general information about the genres and Oslo music scene

USER QUERY: {query}

Important guidance for agent selection:
- The DJ Booking Agent should handle ANY query about DJs, including:
  * Questions about hiring or booking a DJ
  * Inquiries about DJ costs, prices, or fees
  * Questions about DJ availability
  * Specific mentions of DJ Afro, AmapianoQueen, or Oslo Beats
  * Any query containing "book a DJ", "hire a DJ", "DJ for my event", "DJ for wedding", etc.
  * ANY query that mentions both "DJ" and pricing/cost/availability or event types
- Be generous when assigning relevance to the Event Information Agent for any query that mentions events, concerts, shows, performances, festival, happening, schedule, calendar, or asks about things happening at a particular time or place in Oslo.
- The Playlist Curator Agent should handle ANY query related to songs, music recommendations, playlists, tracks, artists, or music suggestions - if the user is asking about specific Afrobeats/Amapiano songs or wants music recommendations, assign high relevance to the Playlist Agent.
- The General Information Agent should handle queries about the history, background, or general information about Afrobeats, Amapiano, or the Oslo music scene.

Your task is to:
1. Analyze the query to understand the user's intent
2. Determine which agent(s) are most suitable to handle this query
3. For each relevant agent, assign a relevance score from 0 to 10, where 10 is extremely relevant
4. Briefly explain why each agent is or isn't relevant

Return your analysis in the following JSON format:
{{
    "analysis": "Brief analysis of the query",
    "selected_agents": {{
        "dj_booking": {{
            "relevance": 0-10,
            "reason": "Why this agent is or isn't relevant"
        }},
        "event_agent": {{
            "relevance": 0-10,
            "reason": "Why this agent is or isn't relevant"
        }},
        "playlist_agent": {{
            "relevance": 0-10,
            "reason": "Why this agent is or isn't relevant"
        }},
        "general_agent": {{
            "relevance": 0-10,
            "reason": "Why this agent is or isn't relevant"
        }}
    }}
}}

Only return valid JSON without additional commentary."""

# Response consolidation prompt for generating final response
RESPONSE_CONSOLIDATION_PROMPT = """You are the response consolidator for Afrobeats.no, responsible for creating a coherent, helpful response based on input from specialized agents.

USER QUERY: {query}

Agent Responses:
{agent_responses}

Your task is to:
1. Create a unified response that coherently incorporates the relevant information from each agent
2. Ensure the response is helpful, accurate, and directly addresses the user's query
3. Remove any redundancies or contradictions between agent responses
4. Prioritize information that is most relevant to the user's query
5. Format the response in a user-friendly way with appropriate paragraphs, lists, or sections

Respond in a conversational, helpful tone as if you are directly addressing the user. Don't mention the different agents or the internal system in your response; simply provide a seamless answer."""

# Function to call Google's Gemini API
def call_gemini(prompt: str) -> str:
    if not GOOGLE_API_KEY:
        logger.warning("No Google API key found, skipping Gemini API call")
        return None

    cache_key = get_cache_key(prompt, f"gemini-{GEMINI_MODEL}")
    cached_response = get_from_cache(cache_key)
    if cached_response:
        return cached_response

    try:
        import google.generativeai as genai

        logger.info(f"Using Gemini model: {GEMINI_MODEL}")

        # Configure the model with proper parameters
        model = genai.GenerativeModel(
            model_name=GEMINI_MODEL,
            generation_config={"temperature": GEMINI_TEMPERATURE}
        )

        # Log that we're sending the request to the API
        logger.info(f"Sending request to Gemini API. Prompt length: {len(prompt)} characters")

        # Generate the response
        try:
            response = model.generate_content(prompt)

            if hasattr(response, 'text') and response.text:
                logger.info("Successfully received response from Gemini API")
                result = response.text
                save_to_cache(cache_key, result)
                return result
            else:
                # Check different response attributes in case the API changes
                if hasattr(response, 'parts') and response.parts:
                    result = response.parts[0].text
                    save_to_cache(cache_key, result)
                    return result
                elif hasattr(response, 'content') and response.content:
                    result = response.content
                    save_to_cache(cache_key, result)
                    return result
                elif hasattr(response, 'choices') and response.choices:
                    result = response.choices[0].text
                    save_to_cache(cache_key, result)
                    return result
                else:
                    logger.error(f"Empty response from Gemini API. Response structure: {dir(response)}")
                    return None
        except Exception as api_error:
            # Check specifically for rate limit errors
            if "429" in str(api_error) and "quota" in str(api_error):
                logger.warning(f"Gemini API rate limit exceeded: {str(api_error)}")
                # Extract wait time if available in the error message
                import re
                wait_match = re.search(r'retry_delay\s*{\s*seconds:\s*(\d+)', str(api_error))
                wait_time = int(wait_match.group(1)) if wait_match else 60
                logger.info(f"Rate limit hit, need to wait {wait_time} seconds")

                # Return a specific message for rate limiting
                return "I'm sorry, but we've hit our API rate limits. Please try again in a minute."
            else:
                # Re-raise other errors
                raise
    except Exception as e:
        logger.error(f"Error calling Gemini API: {str(e)}")
        # Print traceback for detailed debugging
        import traceback
        logger.error(traceback.format_exc())
        return None

# Function to call OpenAI API
def call_openai(prompt: str) -> str:
    if not OPENAI_API_KEY or OPENAI_API_KEY.lower() == 'none':
        logger.warning("No OpenAI API key found or set to 'none', skipping OpenAI API call")
        return None

    cache_key = get_cache_key(prompt, "openai-gpt4o")
    cached_response = get_from_cache(cache_key)
    if cached_response:
        return cached_response

    try:
        import openai

        logger.info("Sending request to OpenAI API (gpt-4o model)")

        # Create the completion request
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant for Afrobeats.no."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000,
        )

        if response and hasattr(response, 'choices') and response.choices:
            logger.info("Successfully received response from OpenAI API")
            result = response.choices[0].message.content
            save_to_cache(cache_key, result)
            return result
        else:
            logger.error(f"Empty response from OpenAI API. Response structure: {dir(response) if response else 'None'}")
            return None
    except Exception as e:
        logger.error(f"Error calling OpenAI API: {str(e)}")
        # Print traceback for detailed debugging
        import traceback
        logger.error(traceback.format_exc())
        return None

# Function to call OpenRouter API
def call_openrouter(prompt: str) -> str:
    if not OPENROUTER_API_KEY:
        logger.warning("No OpenRouter API key found, skipping OpenRouter API call")
        return None

    cache_key = get_cache_key(prompt, f"openrouter-{OPENROUTER_MODEL}")
    cached_response = get_from_cache(cache_key)
    if cached_response:
        return cached_response

    try:
        logger.info(f"Sending request to OpenRouter API (model: {OPENROUTER_MODEL})")

        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://afrobeats.no",  # Optional but recommended
            "X-Title": "Afrobeats.no Agent",  # Optional but recommended
        }

        data = {
            "model": OPENROUTER_MODEL,
            "messages": [
                {"role": "system", "content": "You are a helpful assistant for Afrobeats.no."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 1000
        }

        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data
        )

        if response.status_code == 200:
            result = response.json()
            logger.info("Successfully received response from OpenRouter API")
            content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
            if content:
                save_to_cache(cache_key, content)
                return content
            else:
                logger.error(f"Empty content in OpenRouter response: {result}")
                return None
        elif response.status_code == 429:
            logger.warning("OpenRouter API rate limit exceeded")
            return "I'm sorry, but we've hit our API rate limits. Please try again in a minute."
        else:
            logger.error(f"Error from OpenRouter API: {response.status_code} - {response.text}")
            return None

    except Exception as e:
        logger.error(f"Error calling OpenRouter API: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return None

# Function to call Perplexity API (for up-to-date information)
def call_perplexity(prompt: str, search: bool = True) -> str:
    if not PERPLEXITY_API_KEY:
        logger.warning("No Perplexity API key found, skipping Perplexity API call")
        return None

    cache_key = get_cache_key(prompt, f"perplexity-{PERPLEXITY_MODEL}-search-{search}")
    cached_response = get_from_cache(cache_key)
    if cached_response:
        return cached_response

    try:
        logger.info(f"Sending request to Perplexity API (model: {PERPLEXITY_MODEL}, search: {search})")

        headers = {
            "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
            "Content-Type": "application/json"
        }

        data = {
            "model": PERPLEXITY_MODEL,
            "messages": [
                {"role": "system", "content": "You are a helpful assistant for Afrobeats.no providing up-to-date information about events, music, and DJs."},
                {"role": "user", "content": prompt}
            ],
            "options": {
                "search": search  # Enable search for up-to-date information
            }
        }

        response = requests.post(
            "https://api.perplexity.ai/chat/completions",
            headers=headers,
            json=data
        )

        if response.status_code == 200:
            result = response.json()
            logger.info("Successfully received response from Perplexity API")
            content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
            if content:
                save_to_cache(cache_key, content)
                return content
            else:
                logger.error(f"Empty content in Perplexity response: {result}")
                return None
        elif response.status_code == 429:
            logger.warning("Perplexity API rate limit exceeded")
            return "I'm sorry, but we've hit our API rate limits. Please try again in a minute."
        else:
            logger.error(f"Error from Perplexity API: {response.status_code} - {response.text}")
            return None

    except Exception as e:
        logger.error(f"Error calling Perplexity API: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return None

# Function to enhance responses with up-to-date information when needed
def enhance_with_realtime_data(agent_id: str, query: str, base_response: str) -> str:
    """
    Enhance base response with real-time information for event and general queries
    """
    # Only use Perplexity for event and general information queries
    if agent_id not in ["event_agent", "general_agent"]:
        return base_response

    if not PERPLEXITY_API_KEY:
        return base_response

    try:
        # Skip enhancement if response already seems good
        if len(base_response) > 300 and "I don't have specific information" not in base_response:
            return base_response

        # Prepare prompt for Perplexity
        if agent_id == "event_agent":
            enhancement_prompt = f"""
            The user asked: "{query}"

            I have this initial information about Afrobeats and Amapiano events in Oslo:
            "{base_response}"

            Please enhance this with up-to-date information about current and upcoming Afrobeats and Amapiano events in Oslo.
            Search for the latest events on social media, venue websites, and event listing platforms.
            Focus on current events, locations, dates, ticket prices, and artists.
            Be specific and provide detailed, actionable information.
            """
        else:  # general_agent
            enhancement_prompt = f"""
            The user asked: "{query}"

            I have this initial information:
            "{base_response}"

            Please enhance this with up-to-date information about Afrobeats and Amapiano music scene in Oslo.
            Include recent news, trends, and context that would be helpful.
            """

        # Call Perplexity with search enabled
        logger.info(f"Enhancing {agent_id} response with real-time data")
        enhanced_response = call_perplexity(enhancement_prompt, search=True)

        if not enhanced_response or "API rate limits" in enhanced_response:
            logger.warning("Couldn't enhance with real-time data due to API limits or error")
            return base_response

        logger.info("Successfully enhanced response with real-time data")
        return enhanced_response

    except Exception as e:
        logger.error(f"Error enhancing response with real-time data: {str(e)}")
        return base_response

# Function to call LLM with fallback
def call_llm(prompt: str, prefer_api: Optional[str] = None) -> Union[str, Tuple[str, str]]:
    """
    Call an LLM with the given prompt, with intelligent fallback between available APIs.

    Args:
        prompt: The prompt to send to the LLM
        prefer_api: Optional preference for which API to try first

    Returns:
        Either the response text, or a tuple of (response_text, api_used)
    """
    # Try APIs in order of preference until one succeeds
    attempt = 1
    max_attempts = 2  # Reduced to avoid hitting rate limits too frequently

    # Determine API order based on preference and availability
    if prefer_api and prefer_api in available_apis:
        # If preferred API is available, try it first
        logger.info(f"Using preferred API: {prefer_api}")
        api_order = [prefer_api] + [api for api in available_apis if api != prefer_api]
    else:
        # Default order of APIs to try
        api_order = ["gemini", "openrouter", "perplexity", "openai"]
        # Filter to only include available APIs
        api_order = [api for api in api_order if api in available_apis]

    if not api_order:
        logger.error("No APIs available")
        return "I'm sorry, I couldn't process your request at this time. No AI services are available."

    # Log the API order
    logger.info(f"API order: {api_order}")

    while attempt <= max_attempts:
        logger.info(f"LLM call attempt {attempt}/{max_attempts}")

        for api in api_order:
            logger.info(f"Trying {api} API...")

            if api == "gemini" and "gemini" in available_apis:
                response = call_gemini(prompt)
                if response:
                    # If response is specifically about rate limits, continue to the next API
                    if "rate limits" in response:
                        logger.warning(f"{api} API rate limited, trying another API")
                        continue
                    return response, "gemini"
                logger.warning(f"{api} call failed")

            elif api == "openrouter" and "openrouter" in available_apis:
                response = call_openrouter(prompt)
                if response:
                    # If response is specifically about rate limits, continue to the next API
                    if "rate limits" in response:
                        logger.warning(f"{api} API rate limited, trying another API")
                        continue
                    return response, "openrouter"
                logger.warning(f"{api} call failed")

            elif api == "perplexity" and "perplexity" in available_apis:
                # For Perplexity, we don't use search for normal LLM responses
                response = call_perplexity(prompt, search=False)
                if response:
                    # If response is specifically about rate limits, continue to the next API
                    if "rate limits" in response:
                        logger.warning(f"{api} API rate limited, trying another API")
                        continue
                    return response, "perplexity"
                logger.warning(f"{api} call failed")

            elif api == "openai" and "openai" in available_apis:
                response = call_openai(prompt)
                if response:
                    return response, "openai"
                logger.warning(f"{api} call failed")

        # If all available APIs failed, wait briefly and retry
        if attempt < max_attempts:
            wait_time = attempt * 5  # Progressive backoff
            logger.info(f"Retrying in {wait_time} seconds...")
            time.sleep(wait_time)

        attempt += 1

    # If all attempts failed, return error message
    logger.error(f"All {max_attempts} LLM call attempts failed")
    return "I'm sorry, I couldn't process your request at this time. Please try again later.", "none"

# Function to run the agent graph
def run_agent_graph(query: str, stream: bool = False, options: Dict[str, Any] = None) -> Dict[str, Any]:
    start_time = time.time()
    logger.info(f"Processing query: '{query[:50]}{'...' if len(query) > 50 else ''}'")

    # Default options
    default_options = {
        "prefer_api": None,  # Preferred API to use
        "bypass_cache": False,  # Whether to bypass the cache
        "enable_search": True,  # Whether to use search for up-to-date info
    }

    # Merge with provided options
    if options is None:
        options = {}

    # Apply defaults for missing options
    for key, default_value in default_options.items():
        if key not in options or options[key] is None:
            options[key] = default_value

    # Log options if non-default
    if any(options[key] != default_value for key, default_value in default_options.items()):
        logger.info(f"Custom options: {options}")

    # Check cache for identical query (unless bypassing)
    if not options["bypass_cache"]:
        cache_key = get_cache_key(f"full_query_{query}", "all_agents")
        cached_result = get_from_cache(cache_key)
        if cached_result:
            try:
                result = json.loads(cached_result)
                # Add marker that this was from cache
                result["from_cache"] = True
                # Update timestamp
                result["timestamp"] = datetime.now().isoformat()
                logger.info(f"Returning cached result for query (age: {result.get('processing_time', 0):.2f}s)")
                return result
            except:
                # If there's an error parsing the cache, continue with normal processing
                logger.warning("Error parsing cached result, continuing with normal processing")
    elif options["bypass_cache"]:
        logger.info("Cache bypass requested, skipping cache check")

    # State to track the agent graph execution
    state = {
        "query": query,
        "coordinator_results": None,
        "selected_agents": [],
        "agent_responses": {},
        "final_response": None,
        "processing_time": 0,
        "from_cache": False,
        "api_used": None
    }

    try:
        # Step 1: Query analysis by coordinator
        coordinator_prompt = COORDINATOR_PROMPT.format(query=query)
        logger.info("Calling coordinator agent to analyze query")

        # Call LLM with preferred API if specified
        coordinator_response, api_used = call_llm(coordinator_prompt, prefer_api=options["prefer_api"])

        # Track which API was used
        if isinstance(coordinator_response, tuple) and len(coordinator_response) == 2:
            coordinator_response, api_used = coordinator_response
            state["api_used"] = api_used

        if not coordinator_response:
            logger.error("Coordinator agent failed to process the query")
            state["final_response"] = "I'm sorry, I couldn't process your request at this time. Please try again later."
            return state

        # Parse the JSON response from the coordinator
        try:
            # Check if we need to extract JSON from a markdown codeblock
            if "```json" in coordinator_response:
                logger.info("Coordinator response contains markdown JSON codeblock, extracting...")
                import re
                json_match = re.search(r"```json\s*([\s\S]*?)\s*```", coordinator_response)
                if json_match:
                    coordinator_response = json_match.group(1).strip()

            # Check for other possible JSON formats
            if coordinator_response.strip().startswith("```") and coordinator_response.strip().endswith("```"):
                logger.info("Coordinator response contains generic markdown codeblock, extracting...")
                coordinator_response = coordinator_response.strip().strip("`").strip()

            # Attempt to parse the JSON
            logger.info(f"Attempting to parse coordinator response as JSON: {coordinator_response[:100]}...")
            coordinator_results = json.loads(coordinator_response)
            state["coordinator_results"] = coordinator_results

            # Extract selected agents with relevance > 5
            selected_agents = []
            for agent_id, details in coordinator_results.get("selected_agents", {}).items():
                relevance = details.get("relevance", 0)
                logger.info(f"Agent {agent_id} relevance: {relevance}")
                if relevance > 5:
                    selected_agents.append(agent_id)

            state["selected_agents"] = selected_agents

            if not selected_agents:
                # If no agents are selected, use general agent as fallback
                selected_agents = ["general_agent"]
                state["selected_agents"] = selected_agents
                logger.warning("No agents selected with high relevance, using general agent as fallback")

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse coordinator response as JSON: {e}")
            logger.error(f"Raw response: {coordinator_response}")
            # Default to general agent if coordinator response parsing fails
            state["selected_agents"] = ["general_agent"]
            logger.warning("Using general agent as fallback due to JSON parsing error")

        # Step 2: Parallel processing by selected agents
        agent_responses = {}

        for agent_id in state["selected_agents"]:
            if agent_id in AGENTS:
                agent = AGENTS[agent_id]
                prompt = agent["prompt_template"].format(query=query)

                logger.info(f"Calling agent: {agent['name']}")
                response, api_used = call_llm(prompt, prefer_api=options["prefer_api"])

                # Track which API was used (if returned as tuple)
                if isinstance(response, tuple) and len(response) == 2:
                    response, api_used = response
                    if state["api_used"] is None:  # Only set if not already set
                        state["api_used"] = api_used

                if response:
                    # Enhance event and general agent responses with up-to-date information if requested
                    if agent_id in ["event_agent", "general_agent"] and options["enable_search"] and "perplexity" in available_apis:
                        response = enhance_with_realtime_data(agent_id, query, response)

                    agent_responses[agent_id] = {
                        "agent_name": agent["name"],
                        "response": response
                    }
                    logger.info(f"Received response from {agent['name']}")
                else:
                    logger.error(f"Failed to get response from {agent['name']}")

        state["agent_responses"] = agent_responses

        # Step 3: Response consolidation
        if agent_responses:
            # Format agent responses for the consolidation prompt
            agent_responses_text = ""
            for agent_id, data in agent_responses.items():
                agent_responses_text += f"From {data['agent_name']}:\n{data['response']}\n\n"

            consolidation_prompt = RESPONSE_CONSOLIDATION_PROMPT.format(
                query=query,
                agent_responses=agent_responses_text
            )

            logger.info("Calling response consolidator")
            final_response, api_used = call_llm(consolidation_prompt, prefer_api=options["prefer_api"])

            # Track which API was used (if returned as tuple)
            if isinstance(final_response, tuple) and len(final_response) == 2:
                final_response, api_used = final_response
                if state["api_used"] is None:  # Only set if not already set
                    state["api_used"] = api_used

            if final_response:
                state["final_response"] = final_response
                logger.info("Generated consolidated response")
            else:
                logger.error("Failed to generate consolidated response")
                # Use the first agent response as fallback
                first_agent_response = next(iter(agent_responses.values()), {}).get("response", "")
                state["final_response"] = first_agent_response or "I couldn't generate a proper response at this time."
        else:
            logger.error("No agent responses received")
            state["final_response"] = "I couldn't process your request at this time. Please try again later."

    except Exception as e:
        logger.error(f"Error in agent graph execution: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        state["final_response"] = "I encountered an error while processing your request. Please try again later."

    finally:
        # Calculate processing time
        state["processing_time"] = round(time.time() - start_time, 2)
        logger.info(f"Query processed in {state['processing_time']} seconds")

        # Cache the full result if not bypassing cache
        if not options["bypass_cache"] and state["final_response"] and "rate limits" not in state["final_response"]:
            try:
                cache_key = get_cache_key(f"full_query_{query}", "all_agents")
                save_to_cache(cache_key, json.dumps(state))
                logger.info("Saved result to cache")
            except Exception as e:
                # If there's an error saving to cache, log but continue
                logger.warning(f"Failed to save full result to cache: {str(e)}")

    return state

# For local testing
if __name__ == "__main__":
    test_query = "Tell me about Amapiano music and upcoming events in Oslo"
    result = run_agent_graph(test_query)

    print("\n" + "="*50)
    print(f"Query: {test_query}")
    print("="*50)
    print(f"Response:\n{result['final_response']}")
    print("="*50)
    print(f"Processing time: {result['processing_time']} seconds")
    print(f"Agents used: {', '.join(result['selected_agents'])}")
    print("="*50)