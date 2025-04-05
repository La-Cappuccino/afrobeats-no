from typing import Dict, List, Any
import os
from openai import OpenAI
import json

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", ""))

DJ_BOOKING_SYSTEM_PROMPT = """You are the DJ Booking Agent for Afrobeats.no, specializing in helping users book Afrobeats and Amapiano DJs in Oslo, Norway.

Your core responsibilities:
1. Process DJ booking requests for events in Oslo
2. Answer questions about the booking process
3. Provide information about available DJs and their ratings
4. Guide users through the booking steps
5. Handle availability checks and pricing inquiries
6. Direct users to the booking form on app.afrotorget.no

Key features you should know about:
- Searchable profiles of verified Afrobeats & Amapiano DJs in Oslo
- Direct booking system with availability calendars and pricing
- Support for various event types: private parties, clubs, weddings, cultural festivals
- DJ rating system to help users choose the best DJ for their event

The booking process involves:
1. Users specify event details (date, location in Oslo, event type, budget)
2. System checks available DJs matching requirements
3. User selects a DJ and submits booking request
4. DJ confirms availability and accepts booking
5. Booking is confirmed and details are shared

Always guide users to complete their bookings through app.afrotorget.no for the full experience.
"""

def dj_booking_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    DJ Booking Agent that handles requests related to booking DJs in Oslo.
    
    Args:
        state: The current state of the agent graph
    
    Returns:
        Updated state with DJ booking results
    """
    user_query = state["user_query"]
    
    # Process the query with the DJ booking agent
    response = client.chat.completions.create(
        model="gpt-4o",
        temperature=0.7,
        messages=[
            {"role": "system", "content": DJ_BOOKING_SYSTEM_PROMPT},
            {"role": "user", "content": f"""
            Process this user query related to DJ booking in Oslo:
            
            User query: {user_query}
            
            Provide a helpful response with information about booking Afrobeats/Amapiano DJs in Oslo.
            Include details about the booking process, and guide the user to app.afrotorget.no for completing bookings.
            """}
        ]
    )
    
    booking_response = response.choices[0].message.content
    
    # Extract relevant booking information if possible
    booking_details = extract_booking_details(user_query)
    
    # Recommend available DJs if this is a booking request
    dj_recommendations = []
    if booking_details.get("event_type") or booking_details.get("date"):
        dj_recommendations = recommend_djs(booking_details)
    
    # Update the state with the DJ booking results
    return {
        **state,
        "dj_booking_results": {
            "response": booking_response,
            "details": booking_details,
            "recommendations": dj_recommendations
        },
        "current_agent": ""  # Clear the current agent to return to coordinator
    }

def extract_booking_details(query: str) -> Dict[str, Any]:
    """
    Extract booking details from the user query.
    
    Args:
        query: The user's query
    
    Returns:
        A dictionary of extracted booking details
    """
    # Use LLM to extract structured booking details
    response = client.chat.completions.create(
        model="gpt-4o",
        temperature=0,
        messages=[
            {"role": "system", "content": "Extract booking details from the user query in JSON format. Focus on Oslo events."},
            {"role": "user", "content": f"""
            Extract the following details from this query if present:
            - Event type (e.g., wedding, club, private party)
            - Date or timeframe
            - Location in Oslo (neighborhood if specified)
            - Genre preference (e.g., Afrobeats, Amapiano)
            - Budget indication (if any)
            - Number of guests/size of event
            
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
        return {"extraction_error": "Failed to parse booking details"}

def recommend_djs(booking_details: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Recommend DJs based on booking details.
    
    Args:
        booking_details: Details of the booking request
    
    Returns:
        A list of recommended DJs
    """
    # In a real implementation, this would query the Supabase database
    # For now, we'll simulate some recommendations
    
    # Prepare a prompt with the booking details
    details_str = "\n".join([f"- {k}: {v}" for k, v in booking_details.items() if v])
    
    response = client.chat.completions.create(
        model="gpt-4o",
        temperature=0.7,
        messages=[
            {"role": "system", "content": "You are a DJ recommendation system for Afrobeats.no in Oslo. Recommend 3 fictional DJs based on the booking details."},
            {"role": "user", "content": f"""
            Based on these booking details:
            {details_str}
            
            Recommend 3 fictional Afrobeats/Amapiano DJs in Oslo. For each DJ, provide:
            - Name
            - Main genre
            - Hourly rate range
            - Rating (1-5 stars)
            - Brief description
            
            Return the results as a JSON array of DJ objects.
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
            recommendations = json.loads(json_str)
            return recommendations
        else:
            # For now, we'll return an error
            return [{"error": "Could not parse DJ recommendations"}]
    except:
        return [{"error": "Failed to generate DJ recommendations"}]
