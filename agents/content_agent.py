from typing import Dict, List, Any
import os
from openai import OpenAI
import json

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", ""))

CONTENT_SYSTEM_PROMPT = """You are the Content Agent for Afrobeats.no, specializing in providing news, updates, and educational content about Afrobeats and Amapiano music culture in Oslo, Norway.

Your core responsibilities:
1. Answer questions about Afrobeats and Amapiano music, history, and culture
2. Provide updates on the latest news and trends in these genres
3. Guide users to educational content on the platform
4. Share information about the Norwegian Afrobeats/Amapiano scene
5. Direct users to relevant blog posts and articles

Key features you should know about:
- Blog/news platform on afrobeats.no highlighting music trends and cultural news
- Educational content about African music genres and history
- Content available in both English and Norwegian
- Latest updates on the Oslo Afrobeats/Amapiano scene

Always direct users to afrobeats.no for the main content hub experience.
"""

def content_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Content Agent that handles requests related to news, updates, and educational content.
    
    Args:
        state: The current state of the agent graph
    
    Returns:
        Updated state with content results
    """
    user_query = state["user_query"]
    
    # Process the query with the Content agent
    response = client.chat.completions.create(
        model="gpt-4o",
        temperature=0.7,
        messages=[
            {"role": "system", "content": CONTENT_SYSTEM_PROMPT},
            {"role": "user", "content": f"""
            Process this user query related to Afrobeats/Amapiano news, updates, or educational content:
            
            User query: {user_query}
            
            Provide a helpful response about Afrobeats and Amapiano culture, news, or educational content.
            Include information about content features on Afrobeats.no and guide users to relevant sections.
            Focus on the Oslo and Norwegian scene when relevant.
            """}
        ]
    )
    
    content_response = response.choices[0].message.content
    
    # Extract relevant content information if possible
    content_details = extract_content_details(user_query)
    
    # Get news/article recommendations if appropriate
    news_articles = []
    if "news" in user_query.lower() or "article" in user_query.lower() or "learn" in user_query.lower():
        news_articles = get_news_articles(content_details)
    
    # Update the state with the content results
    return {
        **state,
        "content_results": {
            "response": content_response,
            "details": content_details,
            "news_articles": news_articles
        },
        "current_agent": ""  # Clear the current agent to return to coordinator
    }

def extract_content_details(query: str) -> Dict[str, Any]:
    """
    Extract content details from the user query.
    
    Args:
        query: The user's query
    
    Returns:
        A dictionary of extracted content details
    """
    # Use LLM to extract structured content details
    response = client.chat.completions.create(
        model="gpt-4o",
        temperature=0,
        messages=[
            {"role": "system", "content": "Extract content details from the user query in JSON format."},
            {"role": "user", "content": f"""
            Extract the following details from this query if present:
            - Content type (news, educational, history, culture)
            - Genre focus (Afrobeats, Amapiano, both)
            - Specific topics mentioned
            - Time period (recent news, historical information)
            - Norwegian relevance (Oslo scene, Norwegian events)
            
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
        return {"extraction_error": "Failed to parse content details"}

def get_news_articles(content_details: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Get news articles based on the extracted details.
    
    Args:
        content_details: Details extracted from the user query
    
    Returns:
        A list of news articles
    """
    # In a real implementation, this would query the Supabase database or WordPress API
    # For now, we'll simulate some news articles
    
    # Create a prompt with the content details
    details_str = "\n".join([f"- {k}: {v}" for k, v in content_details.items() if v])
    
    response = client.chat.completions.create(
        model="gpt-4o",
        temperature=0.7,
        messages=[
            {"role": "system", "content": "You are a content recommendation system for Afrobeats.no. Generate 3 fictional news articles based on the query details."},
            {"role": "user", "content": f"""
            Based on these query details:
            {details_str}
            
            Generate 3 fictional Afrobeats/Amapiano news articles with an Oslo/Norway focus. For each article, provide:
            - Article title
            - Publication date (recent)
            - Brief summary
            - Main genre focus
            - Relevance to Oslo/Norway
            
            Return the results as a JSON array of article objects.
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
            articles = json.loads(json_str)
            return articles
        else:
            # For now, we'll return an error
            return [{"error": "Could not parse news articles"}]
    except:
        return [{"error": "Failed to generate news articles"}]
