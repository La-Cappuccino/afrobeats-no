from typing import Dict, List, Any
import os
from openai import OpenAI
import json

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", ""))

ANALYTICS_SYSTEM_PROMPT = """You are the Analytics Agent for Afrobeats.no, specializing in data analysis, trends, and insights for the Afrobeats and Amapiano scene in Oslo, Norway.

Your core responsibilities:
1. Analyze user behavior and preferences across the platform
2. Identify trending songs, artists, and DJs in the Oslo scene
3. Generate insights about event attendance and popularity
4. Support personalized recommendations using ML techniques
5. Track playlist engagement and voting patterns
6. Monitor DJ booking trends and performance metrics
7. Provide data-driven suggestions for content, events, and artists

Key features you should know about:
- User segmentation based on music preferences and platform behavior
- Trend analysis using time-series data of song popularity
- Collaborative filtering for personalized music recommendations
- Predictive analytics for event success and attendance
- Performance metrics for DJs, playlists, and content

Ensure your insights are actionable and specific to the Oslo Afrobeats/Amapiano scene.
"""

def analytics_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analytics Agent that handles requests related to data analysis, trends, and insights.
    
    Args:
        state: The current state of the agent graph
    
    Returns:
        Updated state with analytics results
    """
    user_query = state["user_query"]
    
    # Process the query with the Analytics agent
    response = client.chat.completions.create(
        model="gpt-4o",
        temperature=0.7,
        messages=[
            {"role": "system", "content": ANALYTICS_SYSTEM_PROMPT},
            {"role": "user", "content": f"""
            Process this user query related to analytics and insights:
            
            User query: {user_query}
            
            Provide data-driven insights and analysis for the Afrobeats/Amapiano scene in Oslo.
            Include specific trends, patterns, or recommendations based on data analysis.
            Remember to focus on Oslo's specific music scene and audience.
            """}
        ]
    )
    
    analytics_response = response.choices[0].message.content
    
    # Extract analytics requirements if possible
    analytics_details = extract_analytics_requirements(user_query)
    
    # Generate mock insights based on the query
    insights = generate_insights(analytics_details)
    
    # Update the state with the analytics results
    return {
        **state,
        "analytics_results": {
            "response": analytics_response,
            "details": analytics_details,
            "insights": insights
        },
        "current_agent": ""  # Clear the current agent to return to coordinator
    }

def extract_analytics_requirements(query: str) -> Dict[str, Any]:
    """
    Extract analytics requirements from the user query.
    
    Args:
        query: The user's query
    
    Returns:
        A dictionary of extracted analytics requirements
    """
    # Use LLM to extract structured analytics requirements
    response = client.chat.completions.create(
        model="gpt-4o",
        temperature=0,
        messages=[
            {"role": "system", "content": "Extract analytics requirements from the user query in JSON format."},
            {"role": "user", "content": f"""
            Extract the following details from this query if present:
            - Analysis type (e.g., trend analysis, user segmentation, recommendations)
            - Time period of interest
            - Specific entity to analyze (e.g., DJs, songs, events, playlists)
            - Metrics of interest (e.g., popularity, engagement, bookings)
            - Format of results requested (e.g., report, visualization, recommendation)
            
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
        return {"extraction_error": "Failed to parse analytics requirements"}

def generate_insights(analytics_details: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Generate insights based on analytics requirements.
    
    Args:
        analytics_details: Details of the analytics request
    
    Returns:
        A list of generated insights
    """
    # In a real implementation, this would query a database and run ML models
    # For now, we'll simulate insights
    
    # Prepare a prompt with the analytics details
    details_str = "\n".join([f"- {k}: {v}" for k, v in analytics_details.items() if v])
    
    response = client.chat.completions.create(
        model="gpt-4o",
        temperature=0.7,
        messages=[
            {"role": "system", "content": "You are an analytics system for Afrobeats.no in Oslo. Generate 3 fictional data-driven insights."},
            {"role": "user", "content": f"""
            Based on these analytics requirements:
            {details_str}
            
            Generate 3 fictional but realistic data-driven insights for the Afrobeats/Amapiano scene in Oslo. For each insight, provide:
            - Insight title
            - Key finding
            - Supporting data points
            - Actionable recommendation
            
            Make these specific to Oslo's music scene and ensure they would be valuable for platform users or administrators.
            Return the results as a JSON array of insight objects.
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
            insights = json.loads(json_str)
            return insights
        else:
            # For now, we'll return an error
            return [{"error": "Could not parse generated insights"}]
    except:
        return [{"error": "Failed to generate analytics insights"}]