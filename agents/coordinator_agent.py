from typing import Dict, List, Any
from typing_extensions import TypedDict
import os
import json
import google.generativeai as genai
import openai

# Configure the Gemini API
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY", ""))

# Configure OpenAI as fallback - use None for missing API key instead of demo key
openai_api_key = os.environ.get("OPENAI_API_KEY")
openai_client = openai.OpenAI(api_key=openai_api_key) if openai_api_key else None

# Define available models - using actual Gemini 2.5 models
MODELS = {
    "Gemini 2.5 Pro": "models/gemini-2.5-pro-preview-03-25",
    "Gemini 2.5 Flash": "models/gemini-2.0-flash"  # Using 2.0 Flash as fallback
}

def get_model_name():
    """Get the model name based on environment variable or default to Gemini 2.5 Pro."""
    model_env = os.environ.get("GEMINI_MODEL", "Gemini 2.5 Pro")
    return MODELS.get(model_env, "models/gemini-2.5-pro-preview-03-25")

def get_temperature():
    """Get the temperature based on environment variable or default to 0.7."""
    try:
        return float(os.environ.get("GEMINI_TEMPERATURE", "0.7"))
    except ValueError:
        return 0.7

COORDINATOR_SYSTEM_PROMPT = """You are the coordinator agent for the Afrobeats.no platform, specializing in Afrobeats and Amapiano DJ bookings and events in Oslo, Norway.

Your responsibilities:
1. Analyze user queries to determine which specialized agent(s) should handle them
2. Identify requirements for multiple specialized agents that can run in parallel:
   - DJ Booking Agent: For queries about booking DJs, availability, pricing
   - Event Discovery Agent: For queries about finding or promoting events in Oslo
   - Playlist Agent: For playlist curation, voting, sharing, and music recommendations
   - DJ Rating Agent: For reviews, ratings, and feedback on DJs
   - Content Agent: For news and updates about Afrobeats/Amapiano scene in Oslo
   - Social Media Agent: For creating and sharing content on social platforms
   - Analytics Agent: For ML-driven insights, trends, and recommendations
   - Artist Agent: For artist discovery, profiles, and music submissions

3. Extract structured information from the user query
4. Enable parallel processing by multiple agents
5. Coordinate the final response generation

The platform consists of:
- Main site (afrobeats.no): WordPress-based content hub
- App subdomain (app.afrotorget.no): User portal with DJ bookings
- Amapiano subdomain (amapiano.afrotorget.no): Genre-specific space

Remember that our primary focus is on DJ booking and events in Oslo, with secondary focus on playlists, song rankings, and ratings. The platform supports both Norwegian and English to serve the diverse Afrobeats/Amapiano community in Norway.
"""

def coordinator_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Coordinator agent that analyzes user queries and determines which specialized agents
    should process the query in parallel.
    
    Args:
        state: The current state of the agent graph
    
    Returns:
        Updated state with query analysis and agent requirements
    """
    user_query = state["user_query"]
    messages = state.get("messages", [])
    
    # Add the user's query to messages
    messages.append({"role": "user", "content": user_query})
    
    # Get model and temperature from environment variables or session state
    model = get_model_name()
    temperature = get_temperature()
    
    # Analyze the query to determine required agents
    generation_config = {
        "temperature": temperature,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 4096,
    }
    
    prompt = f"""
    {COORDINATOR_SYSTEM_PROMPT}
    
    Analyze this user query in detail:
    
    User query: {user_query}
    
    For this query, determine:
    1. The primary intent of the query
    2. Which specialized agents should process this query (multiple agents can run in parallel)
    3. Any specific information that would help those agents respond effectively
    
    Return your analysis as a JSON object with the following structure:
    {{
        "query_intent": "Brief description of the user's intent",
        "needs_dj_booking": true/false,
        "needs_event_discovery": true/false,
        "needs_playlist": true/false,
        "needs_dj_rating": true/false,
        "needs_content": true/false,
        "needs_social_media": true/false,
        "needs_analytics": true/false,
        "needs_artist": true/false,
        "extracted_information": {{
            // Any relevant details extracted from the query
            // For example: date, location, genre preferences, etc.
        }}
    }}
    
    Be precise in your analysis. Only mark an agent as needed if it's directly relevant to the query.
    """
    
    try:
        response_text = ""
        try:
            # First try with Gemini
            # Initialize Gemini model
            gemini_model = genai.GenerativeModel(
                model_name=model,
                generation_config=generation_config
            )
            
            # Generate response
            response = gemini_model.generate_content(prompt)
            response_text = response.text
            print("Successfully used Gemini API")
        except Exception as gemini_error:
            # If Gemini fails, try OpenAI as fallback
            print(f"Error with Gemini API: {str(gemini_error)}. Using OpenAI fallback.")
            
            try:
                # Try with OpenAI
                openai_response = openai_client.chat.completions.create(
                    model="gpt-4o",
                    temperature=temperature,
                    messages=[
                        {"role": "system", "content": COORDINATOR_SYSTEM_PROMPT},
                        {"role": "user", "content": prompt}
                    ]
                )
                response_text = openai_response.choices[0].message.content
                print("Successfully used OpenAI fallback")
            except Exception as openai_error:
                print(f"Error with OpenAI fallback: {str(openai_error)}")
                # Let it fall through to the basic fallback below
                raise
        
        # Extract the query information from the response
        query_info = {}
        try:
            # Simple JSON extraction if it's embedded in text
            if '{' in response_text and '}' in response_text:
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                json_str = response_text[json_start:json_end]
                query_info = json.loads(json_str)
            else:
                # Fallback if proper JSON isn't returned
                query_info = {
                    "query_intent": "Unknown intent",
                    "needs_dj_booking": "dj" in user_query.lower() and "book" in user_query.lower(),
                    "needs_event_discovery": "event" in user_query.lower() or "happening" in user_query.lower(),
                    "needs_playlist": "playlist" in user_query.lower() or "music" in user_query.lower(),
                    "needs_dj_rating": "rating" in user_query.lower() or "review" in user_query.lower(),
                    "needs_content": "news" in user_query.lower() or "article" in user_query.lower(),
                    "needs_social_media": "social" in user_query.lower() or "instagram" in user_query.lower(),
                    "needs_analytics": "trend" in user_query.lower() or "popular" in user_query.lower(),
                    "needs_artist": "artist" in user_query.lower() or "musician" in user_query.lower()
                }
        except:
            # If parsing fails, use a basic fallback
            query_info = {
                "query_intent": "Unknown intent",
                "needs_dj_booking": "dj" in user_query.lower() and "book" in user_query.lower(),
                "needs_event_discovery": "event" in user_query.lower() or "happening" in user_query.lower(),
                "needs_playlist": "playlist" in user_query.lower() or "music" in user_query.lower(),
                "needs_dj_rating": "rating" in user_query.lower() or "review" in user_query.lower(),
                "needs_content": "news" in user_query.lower() or "article" in user_query.lower(),
                "needs_social_media": "social" in user_query.lower() or "instagram" in user_query.lower(),
                "needs_analytics": "trend" in user_query.lower() or "popular" in user_query.lower(),
                "needs_artist": "artist" in user_query.lower() or "musician" in user_query.lower()
            }
        
    except Exception as e:
        # If all API calls fail, use a basic fallback
        print(f"Error calling all APIs: {str(e)}")
        query_info = {
            "query_intent": "Unknown intent",
            "needs_dj_booking": "dj" in user_query.lower() and "book" in user_query.lower(),
            "needs_event_discovery": "event" in user_query.lower() or "happening" in user_query.lower(),
            "needs_playlist": "playlist" in user_query.lower() or "music" in user_query.lower(),
            "needs_dj_rating": "rating" in user_query.lower() or "review" in user_query.lower(),
            "needs_content": "news" in user_query.lower() or "article" in user_query.lower(),
            "needs_social_media": "social" in user_query.lower() or "instagram" in user_query.lower(),
            "needs_analytics": "trend" in user_query.lower() or "popular" in user_query.lower(),
            "needs_artist": "artist" in user_query.lower() or "musician" in user_query.lower()
        }
    
    # If no agents are needed, set at least one to True to avoid empty processing
    any_agent_needed = any([
        query_info.get("needs_dj_booking", False),
        query_info.get("needs_event_discovery", False),
        query_info.get("needs_playlist", False),
        query_info.get("needs_dj_rating", False),
        query_info.get("needs_content", False),
        query_info.get("needs_social_media", False),
        query_info.get("needs_analytics", False),
        query_info.get("needs_artist", False)
    ])
    
    if not any_agent_needed:
        # If no specific agent is needed, use content agent as default
        query_info["needs_content"] = True
    
    # Update the state with the query info
    return {
        **state,
        "messages": messages,
        "query_info": query_info,
        "current_agent": ""  # Reset current agent to allow branching logic to work
    }

def generate_final_response(query: str, results: Dict[str, Any]) -> str:
    """
    Generate a final response based on the results from specialized agents.
    
    Args:
        query: The original user query
        results: Results from various specialized agents
    
    Returns:
        A final response to the user
    """
    # Collect all non-empty results
    relevant_results = {}
    for key, value in results.items():
        if value:
            relevant_results[key] = value
    
    # Get model and temperature from environment variables
    model_name = get_model_name()
    temperature = get_temperature()
    
    # Configure Gemini generation parameters
    generation_config = {
        "temperature": temperature,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 4096,
    }
    
    # If we have specialized agent results, use them to form a response
    if relevant_results:
        # Create a prompt with all the results
        results_prompt = ""
        for key, value in relevant_results.items():
            results_prompt += f"\n{key}:\n{value}\n"
        
        prompt = f"""
        {COORDINATOR_SYSTEM_PROMPT}
        
        Create a cohesive, detailed response to the user's query: "{query}"
        
        Here are the results from specialized agents:
        {results_prompt}
        
        Integrate these results into a helpful, comprehensive response. Remember that we focus on Oslo's Afrobeats/Amapiano DJ scene.
        Include relevant URLs or next steps if appropriate.
        
        Format the response attractively with clear sections, lists, and other formatting as needed.
        Make it feel like a single, unified response rather than disjointed information from different sources.
        """
        
        try:
            try:
                # First try with Gemini
                gemini_model = genai.GenerativeModel(
                    model_name=model_name,
                    generation_config=generation_config
                )
                response = gemini_model.generate_content(prompt)
                print("Successfully used Gemini API for final response")
                return response.text
            except Exception as gemini_error:
                # If Gemini fails, try OpenAI as fallback
                print(f"Error with Gemini API for final response: {str(gemini_error)}. Using OpenAI fallback.")
                
                try:
                    # Try with OpenAI
                    openai_response = openai_client.chat.completions.create(
                        model="gpt-4o",
                        temperature=temperature,
                        messages=[
                            {"role": "system", "content": COORDINATOR_SYSTEM_PROMPT},
                            {"role": "user", "content": prompt}
                        ]
                    )
                    print("Successfully used OpenAI fallback for final response")
                    return openai_response.choices[0].message.content
                except Exception as openai_error:
                    print(f"Error with OpenAI fallback for final response: {str(openai_error)}")
                    # Let it fall through to the basic fallback below
                    raise
        except Exception as e:
            print(f"Error generating final response: {str(e)}")
            # Fallback to a simple response if all API calls fail
            return f"I found some information about your query regarding {query}, but I'm having trouble formatting the response. Please try again later."
    
    # If no specialized agent results, generate a direct response
    prompt = f"""
    {COORDINATOR_SYSTEM_PROMPT}
    
    The user asked: "{query}"
    
    Please provide a helpful response about the Afrobeats.no platform in Oslo. Focus on DJ booking, events, 
    playlists, and DJ ratings. Direct them to app.afrotorget.no for booking features if relevant.
    """
    
    try:
        try:
            # First try with Gemini
            gemini_model = genai.GenerativeModel(
                model_name=model_name,
                generation_config=generation_config
            )
            response = gemini_model.generate_content(prompt)
            print("Successfully used Gemini API for direct response")
            return response.text
        except Exception as gemini_error:
            # If Gemini fails, try OpenAI as fallback
            print(f"Error with Gemini API for direct response: {str(gemini_error)}. Using OpenAI fallback.")
            
            try:
                # Try with OpenAI
                openai_response = openai_client.chat.completions.create(
                    model="gpt-4o",
                    temperature=temperature,
                    messages=[
                        {"role": "system", "content": COORDINATOR_SYSTEM_PROMPT},
                        {"role": "user", "content": prompt}
                    ]
                )
                print("Successfully used OpenAI fallback for direct response")
                return openai_response.choices[0].message.content
            except Exception as openai_error:
                print(f"Error with OpenAI fallback for direct response: {str(openai_error)}")
                # Let it fall through to the basic fallback below
                raise
    except Exception as e:
        print(f"Error generating direct response: {str(e)}")
        # Fallback to a simple response if all API calls fail
        return f"I'd be happy to help with your query about {query}, but I'm having trouble connecting to my knowledge base. Please try again later."