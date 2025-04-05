from typing import Dict, List, Any
import os
from openai import OpenAI
import json

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", ""))

DJ_RATING_SYSTEM_PROMPT = """You are the DJ Rating Agent for Afrobeats.no, specializing in helping users rate and review Afrobeats and Amapiano DJs in Oslo, Norway.

Your core responsibilities:
1. Process DJ rating and review submissions
2. Answer questions about the DJ rating system
3. Provide information about top-rated DJs
4. Guide users on how to leave helpful reviews
5. Explain how ratings affect DJ recommendations

Key features you should know about:
- Star rating system (1-5 stars)
- Written review component
- Verified booking badge for reviews from actual customers
- Rating categories (music selection, mixing skills, crowd interaction, professionalism)
- DJ response system to reviews

The platform supports both Norwegian and English to serve the diverse Afrobeats/Amapiano community in Norway.

Always guide users to app.afrotorget.no for submitting ratings and reviews.
"""

def dj_rating_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    DJ Rating Agent that handles requests related to rating and reviewing DJs.
    
    Args:
        state: The current state of the agent graph
    
    Returns:
        Updated state with DJ rating results
    """
    user_query = state["user_query"]
    
    # Process the query with the DJ Rating agent
    response = client.chat.completions.create(
        model="gpt-4o",
        temperature=0.7,
        messages=[
            {"role": "system", "content": DJ_RATING_SYSTEM_PROMPT},
            {"role": "user", "content": f"""
            Process this user query related to DJ ratings and reviews:
            
            User query: {user_query}
            
            Provide a helpful response about the DJ rating system, submitting reviews, or finding top-rated DJs.
            Include information about how ratings work on Afrobeats.no and guide users to app.afrotorget.no for submitting ratings.
            """}
        ]
    )
    
    rating_response = response.choices[0].message.content
    
    # Extract relevant rating information if possible
    rating_details = extract_rating_details(user_query)
    
    # Get top rated DJs if the user is asking about them
    top_rated_djs = []
    if "top" in user_query.lower() or "best" in user_query.lower() or "highest rated" in user_query.lower():
        top_rated_djs = get_top_rated_djs(rating_details)
    
    # Update the state with the DJ rating results
    return {
        **state,
        "dj_rating_results": {
            "response": rating_response,
            "details": rating_details,
            "top_rated_djs": top_rated_djs
        },
        "current_agent": ""  # Clear the current agent to return to coordinator
    }

def extract_rating_details(query: str) -> Dict[str, Any]:
    """
    Extract rating details from the user query.
    
    Args:
        query: The user's query
    
    Returns:
        A dictionary of extracted rating details
    """
    # Use LLM to extract structured rating details
    response = client.chat.completions.create(
        model="gpt-4o",
        temperature=0,
        messages=[
            {"role": "system", "content": "Extract DJ rating details from the user query in JSON format."},
            {"role": "user", "content": f"""
            Extract the following details from this query if present:
            - DJ name or mention
            - Rating value (1-5 stars) if giving a rating
            - Rating categories mentioned (music selection, mixing, crowd interaction, professionalism)
            - Review text if providing a review
            - User intent (submit rating, find top DJs, ask about system)
            
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
        return {"extraction_error": "Failed to parse rating details"}

def get_top_rated_djs(rating_details: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Get top rated DJs based on the extracted details.
    
    Args:
        rating_details: Details extracted from the user query
    
    Returns:
        A list of top rated DJs
    """
    # In a real implementation, this would query the Supabase database
    # For now, we'll simulate some top rated DJs
    
    # Create a prompt with the rating details
    details_str = "\n".join([f"- {k}: {v}" for k, v in rating_details.items() if v])
    
    response = client.chat.completions.create(
        model="gpt-4o",
        temperature=0.7,
        messages=[
            {"role": "system", "content": "You are a DJ rating system for Afrobeats.no in Oslo. Generate 3 fictional top-rated DJs based on the user query."},
            {"role": "user", "content": f"""
            Based on these query details:
            {details_str}
            
            Generate 3 fictional top-rated Afrobeats/Amapiano DJs in Oslo. For each DJ, provide:
            - DJ name
            - Overall rating (4.0-5.0 stars)
            - Primary genre
            - Number of reviews
            - Specialty/strengths
            - Brief review quote from a customer
            
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
            djs = json.loads(json_str)
            return djs
        else:
            # For now, we'll return an error
            return [{"error": "Could not parse top rated DJs"}]
    except:
        return [{"error": "Failed to generate top rated DJs"}]
