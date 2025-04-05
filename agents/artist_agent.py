from typing import Dict, List, Any
import os
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", ""))

ARTIST_SYSTEM_PROMPT = """You are the Artist Agent for Afrobeats.no, specializing in helping users discover artists and handling artist-related inquiries.

Your core responsibilities:
1. Answer questions about Afrobeats and Amapiano artists
2. Provide information about artist features on the platform
3. Guide artists on how to submit their music and profiles
4. Handle inquiries about artist promotion and exposure
5. Direct users to artist features on all subdomains

Key features you should know about:
- Artist spotlight pages on afrobeats.no with SEO optimization
- Artist submission process for new music, bios, and media
- Integration with the DJ booking system on app.afrotorget.no
- Genre-specific artist promotion on amapiano.afrotorget.no

Always encourage artists to submit their content through app.afrotorget.no for the best visibility.
"""

def artist_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Artist Agent that handles requests related to artists and music submissions.
    
    Args:
        state: The current state of the agent graph
    
    Returns:
        Updated state with artist results
    """
    user_query = state["user_query"]
    
    # Process the query with the Artist agent
    response = client.chat.completions.create(
        model="gpt-4o",
        temperature=0.7,
        messages=[
            {"role": "system", "content": ARTIST_SYSTEM_PROMPT},
            {"role": "user", "content": f"""
            Process this user query related to artists or music submissions:
            
            User query: {user_query}
            
            Provide a helpful response about Afrobeats and Amapiano artists or the process for artists to submit their content.
            Include information about the artist features on Afrobeats.no and guide users to app.afrotorget.no for submissions.
            """}
        ]
    )
    
    artist_response = response.choices[0].message.content
    
    # Extract relevant artist information if possible
    artist_details = extract_artist_details(user_query)
    
    # Update the state with the artist results
    return {
        **state,
        "artist_results": {
            "response": artist_response,
            "details": artist_details
        },
        "current_agent": ""  # Clear the current agent to return to coordinator
    }

def extract_artist_details(query: str) -> Dict[str, Any]:
    """
    Extract artist details from the user query.
    
    Args:
        query: The user's query
    
    Returns:
        A dictionary of extracted artist details
    """
    # Use LLM to extract structured artist details
    response = client.chat.completions.create(
        model="gpt-4o",
        temperature=0,
        messages=[
            {"role": "system", "content": "Extract artist details from the user query in JSON format."},
            {"role": "user", "content": f"""
            Extract the following details from this query if present:
            - Artist name
            - Genre (e.g., Afrobeats, Amapiano)
            - Whether the user is an artist or a fan
            - Specific artist services mentioned (e.g., profile creation, music submission)
            - Type of information requested
            
            User query: {query}
            
            Return a JSON object with these fields. If a field is not present in the query, set it to null.
            """}
        ]
    )
    
    # The response content should be in JSON format, but we'll handle errors gracefully
    try:
        # Note: In a real implementation, you would parse this properly
        # This is a simplified approximation
        details_text = response.choices[0].message.content
        
        # For now, we'll return the text
        return {"extracted_text": details_text}
    except:
        return {"extraction_error": "Failed to parse artist details"}
