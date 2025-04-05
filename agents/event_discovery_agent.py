from typing import Dict, List, Any
import os
from openai import OpenAI
import json
from datetime import datetime, timedelta

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", ""))

EVENT_DISCOVERY_SYSTEM_PROMPT = """You are the Event Discovery Agent for Afrobeats.no, specializing in helping users find and promote Afrobeats and Amapiano events in Oslo, Norway.

Your core responsibilities:
1. Help users discover upcoming Afrobeats/Amapiano events in Oslo
2. Provide information about event listings on the platform
3. Guide event organizers on how to submit their events
4. Answer questions about event venues and lineups in Oslo
5. Direct users to the event calendar on app.afrotorget.no

Key features you should know about:
- Community-driven event listings for Oslo (parties, concerts, cultural nights)
- RSVP functionality and integration with DJ bookings
- Event promotion features for organizers
- Filter events by date, venue, and Afrobeats/Amapiano subgenre

The platform supports both Norwegian and English to serve the diverse Afrobeats/Amapiano community in Norway.

Always encourage users to check app.afrotorget.no for the most up-to-date event information in Oslo.
"""

def event_discovery_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Event Discovery Agent that handles requests related to finding and promoting events in Oslo.
    
    Args:
        state: The current state of the agent graph
    
    Returns:
        Updated state with event discovery results
    """
    user_query = state["user_query"]
    
    # Process the query with the Event Discovery agent
    response = client.chat.completions.create(
        model="gpt-4o",
        temperature=0.7,
        messages=[
            {"role": "system", "content": EVENT_DISCOVERY_SYSTEM_PROMPT},
            {"role": "user", "content": f"""
            Process this user query related to event discovery or promotion in Oslo:
            
            User query: {user_query}
            
            Provide a helpful response about finding or promoting Afrobeats and Amapiano events in Oslo.
            Include relevant information about the event features on Afrobeats.no and guide users to app.afrotorget.no.
            """}
        ]
    )
    
    event_response = response.choices[0].message.content
    
    # Extract relevant event information if possible
    event_details = extract_event_details(user_query)
    
    # Find upcoming events if this is a discovery request
    upcoming_events = []
    if "find" in user_query.lower() or "discover" in user_query.lower() or "events" in user_query.lower():
        upcoming_events = find_upcoming_events(event_details)
    
    # Update the state with the event discovery results
    return {
        **state,
        "event_discovery_results": {
            "response": event_response,
            "details": event_details,
            "upcoming_events": upcoming_events
        },
        "current_agent": ""  # Clear the current agent to return to coordinator
    }

def extract_event_details(query: str) -> Dict[str, Any]:
    """
    Extract event details from the user query.
    
    Args:
        query: The user's query
    
    Returns:
        A dictionary of extracted event details
    """
    # Use LLM to extract structured event details
    response = client.chat.completions.create(
        model="gpt-4o",
        temperature=0,
        messages=[
            {"role": "system", "content": "Extract event details from the user query in JSON format. Focus on Oslo events."},
            {"role": "user", "content": f"""
            Extract the following details from this query if present:
            - Event type (e.g., concert, party, cultural night)
            - Date range or timeframe
            - Location or venue in Oslo
            - Genre preference (e.g., Afrobeats, Amapiano)
            - DJ or artist mentions
            - Whether the user is looking to attend or promote an event
            
            User query: {query}
            
            Return a JSON object with these fields. If a field is not present in the query, set it to null.
            """}
        ]
    )
    
    # The response content should be in JSON format, but we'll handle errors gracefully
    try:
        # Try to extract JSON from the response
        response_text = response.choices[0].message.content
        
        # Simple JSON extraction if it's embedded in text
        if '{' in response_text and '}' in response_text:
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            json_str = response_text[json_start:json_end]
            details = json.loads(json_str)
            return details
        else:
            # For now, we'll return the text
            return {"extracted_text": response_text}
    except:
        return {"extraction_error": "Failed to parse event details"}

def find_upcoming_events(event_details: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Find upcoming events based on the extracted details.
    
    Args:
        event_details: Details extracted from the user query
    
    Returns:
        A list of upcoming events
    """
    # In a real implementation, this would query the Supabase database
    # For now, we'll simulate some upcoming events
    
    # Create a prompt with the event details
    details_str = "\n".join([f"- {k}: {v}" for k, v in event_details.items() if v])
    
    response = client.chat.completions.create(
        model="gpt-4o",
        temperature=0.7,
        messages=[
            {"role": "system", "content": "You are an event recommendation system for Afrobeats.no in Oslo. Generate 3 fictional upcoming events based on the search details."},
            {"role": "user", "content": f"""
            Based on these search details:
            {details_str}
            
            Generate 3 fictional upcoming Afrobeats/Amapiano events in Oslo. For each event, provide:
            - Event name
            - Date and time
            - Venue in Oslo
            - Description
            - Featured DJs
            - Ticket price
            
            Return the results as a JSON array of event objects.
            """}
        ]
    )
    
    try:
        # Try to extract JSON from the response
        response_text = response.choices[0].message.content
        
        # Simple JSON extraction if it's embedded in text
        if '[' in response_text and ']' in response_text:
            json_start = response_text.find('[')
            json_end = response_text.rfind(']') + 1
            json_str = response_text[json_start:json_end]
            events = json.loads(json_str)
            return events
        else:
            # For now, we'll return an error
            return [{"error": "Could not parse upcoming events"}]
    except:
        return [{"error": "Failed to generate upcoming events"}]
