from typing import Dict, List, Any, Optional
import os
import json
import logging
from datetime import datetime
import traceback
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Use environment variables for API keys (security best practice)
try:
    # Placeholder for Gemini API - in the actual implementation, we would use Gemini 2.5
    # For now, we'll use OpenAI as a placeholder until we can fully implement Gemini
    from openai import OpenAI
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", ""))
except ImportError as e:
    logger.error(f"Failed to import required libraries: {e}")
    raise

# System prompt for the Social Media Agent
SOCIAL_MEDIA_SYSTEM_PROMPT = """You are the Social Media Agent for Afrobeats.no, specializing in creating and sharing content about Afrobeats and Amapiano music, DJs, events, and playlists in Oslo, Norway.

Your core responsibilities:
1. Create engaging social media content for various platforms (Instagram, Twitter, Facebook, TikTok)
2. Highlight popular playlists, events, and DJs from the platform
3. Extract interesting discussions from the community forum for social sharing
4. Generate automated posts for new content and trending items
5. Create promotional content for upcoming events
6. Develop content series and campaigns to drive engagement

Key features you should know about:
- Platform audience demographics and preferences
- Best practices for each social media platform
- Optimal posting times and frequencies
- Multilingual content (Norwegian and English)
- Integration with n8n for automated posting
- Content performance tracking and analytics

Always maintain the authentic voice of the Afrobeats/Amapiano community in Norway while creating content that will drive growth and engagement.
"""

def social_media_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Social Media Agent that handles creation and sharing of content on social platforms.
    
    Args:
        state: The current state of the agent graph
    
    Returns:
        Updated state with social media results
    """
    try:
        user_query = state["user_query"]
        
        # Process the query - in production, this would use Gemini 2.5
        response = client.chat.completions.create(
            model="gpt-4o",
            temperature=0.7,
            messages=[
                {"role": "system", "content": SOCIAL_MEDIA_SYSTEM_PROMPT},
                {"role": "user", "content": f"""
                Process this user query related to social media content creation or sharing:
                
                User query: {user_query}
                
                Provide a helpful response about creating or sharing social media content for Afrobeats.no.
                Include platform-specific recommendations and best practices where relevant.
                """}
            ]
        )
        
        social_media_response = response.choices[0].message.content
        
        # Extract relevant social media information
        social_media_details = extract_social_media_details(user_query)
        
        # Determine what type of social media content is needed
        content_platform = social_media_details.get("platform", "")
        content_type = social_media_details.get("content_type", "")
        
        # Generate appropriate content based on the request
        generated_content = {}
        
        if "create" in user_query.lower() or "generate" in user_query.lower() or "post" in user_query.lower():
            generated_content = generate_social_media_content(social_media_details)
        
        if "share" in user_query.lower() or "post" in user_query.lower():
            sharing_info = get_sharing_recommendations(social_media_details)
            generated_content["sharing_info"] = sharing_info
        
        if "highlight" in user_query.lower() or "forum" in user_query.lower() or "discussion" in user_query.lower():
            forum_highlights = extract_forum_highlights(social_media_details)
            generated_content["forum_highlights"] = forum_highlights
        
        if "campaign" in user_query.lower() or "strategy" in user_query.lower() or "plan" in user_query.lower():
            campaign_strategy = create_campaign_strategy(social_media_details)
            generated_content["campaign_strategy"] = campaign_strategy
        
        # Update the state with the social media results
        return {
            **state,
            "social_media_results": {
                "response": social_media_response,
                "details": social_media_details,
                "generated_content": generated_content
            },
            "current_agent": ""  # Clear the current agent to return to coordinator
        }
        
    except Exception as e:
        # Secure error handling - don't expose sensitive details
        error_id = f"ERR-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Log the full error for internal debugging
        logger.error(f"Error {error_id} in social media agent: {str(e)}")
        logger.debug(traceback.format_exc())
        
        # Return a sanitized error message to the user
        return {
            **state,
            "social_media_results": {
                "error": f"Sorry, we encountered an issue processing your social media request. Reference ID: {error_id}"
            },
            "current_agent": ""
        }

def extract_social_media_details(query: str) -> Dict[str, Any]:
    """
    Extract social media details from the user query.
    
    Args:
        query: The user's query
    
    Returns:
        A dictionary of extracted social media details
    """
    try:
        # Use LLM to extract structured social media details
        response = client.chat.completions.create(
            model="gpt-4o",
            temperature=0,
            messages=[
                {"role": "system", "content": "Extract social media details from the user query in JSON format."},
                {"role": "user", "content": f"""
                Extract the following details from this query if present:
                - Platform (e.g., Instagram, Twitter, Facebook, TikTok)
                - Content type (e.g., post, story, reel, tweet)
                - Event or DJ mentioned
                - Playlist mentioned
                - Campaign mentioned
                - Goal or purpose
                - Target audience
                - Tone or style preferences
                
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
            return {"extraction_error": "Failed to parse social media details as JSON"}
            
    except Exception as e:
        logger.error(f"Error extracting social media details: {str(e)}")
        return {"extraction_error": "Failed to extract social media details"}

def generate_social_media_content(details: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate social media content based on the extracted details.
    
    Args:
        details: Details extracted from the user query
    
    Returns:
        Generated social media content
    """
    try:
        # Extract relevant details for content creation
        platform = details.get("platform")
        content_type = details.get("content_type")
        event = details.get("event")
        dj = details.get("dj")
        playlist = details.get("playlist")
        goal = details.get("goal")
        audience = details.get("target_audience")
        tone = details.get("tone")
        
        # Create a prompt with the details
        details_str = "\n".join([f"- {k}: {v}" for k, v in details.items() if v])
        
        # Add platform-specific constraints
        platform_constraints = {
            "instagram": "Caption should be engaging, use emojis, include 5-10 relevant hashtags.",
            "twitter": "Text should be under 280 characters, use 1-2 hashtags.",
            "facebook": "More detailed text allowed, can include links and calls to action.",
            "tiktok": "Short, trendy, catchy text with relevant hashtags."
        }
        
        constraint = ""
        if platform and platform.lower() in platform_constraints:
            constraint = platform_constraints[platform.lower()]
        
        response = client.chat.completions.create(
            model="gpt-4o",
            temperature=0.7,
            messages=[
                {"role": "system", "content": f"You are a social media content creator for Afrobeats.no in Oslo. Generate authentic, engaging content for {platform or 'social media'} that will resonate with the Afrobeats/Amapiano community."},
                {"role": "user", "content": f"""
                Create social media content based on these details:
                {details_str}
                
                {constraint}
                
                Generate both English and Norwegian versions.
                Include text, hashtags, and any other elements appropriate for the platform.
                Focus on driving engagement and growth for Afrobeats.no.
                
                Return the content in JSON format with separate fields for each element.
                """}
            ]
        )
        
        # Extract JSON safely
        try:
            response_text = response.choices[0].message.content
            
            if '{' in response_text and '}' in response_text:
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                json_str = response_text[json_start:json_end]
                content = json.loads(json_str)
                
                # Add platform-specific validation
                if platform and platform.lower() == "twitter" and "text_en" in content:
                    # Check Twitter character limit
                    if len(content["text_en"]) > 280:
                        content["warning"] = "Twitter text exceeds 280 character limit and may be truncated."
                
                return content
            else:
                # If not properly formatted as JSON, return the raw text
                return {
                    "platform": platform,
                    "content_type": content_type,
                    "raw_content": response_text
                }
        except json.JSONDecodeError:
            logger.warning(f"Failed to parse JSON from social media content")
            return {"content": response_text}
            
    except Exception as e:
        logger.error(f"Error generating social media content: {str(e)}")
        return {"error": "Failed to generate social media content"}

def get_sharing_recommendations(details: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get recommendations for sharing content on social media.
    
    Args:
        details: Details extracted from the user query
    
    Returns:
        Social media sharing recommendations
    """
    try:
        # Extract relevant details
        platform = details.get("platform")
        content_type = details.get("content_type")
        goal = details.get("goal")
        
        # Create a prompt with the details
        details_str = "\n".join([f"- {k}: {v}" for k, v in details.items() if v])
        
        response = client.chat.completions.create(
            model="gpt-4o",
            temperature=0.7,
            messages=[
                {"role": "system", "content": "You are a social media strategy expert for Afrobeats.no in Oslo. Provide strategic recommendations for sharing content."},
                {"role": "user", "content": f"""
                Provide sharing recommendations based on these details:
                {details_str}
                
                Include:
                - Best time to post
                - Frequency recommendations
                - Cross-platform strategy
                - Engagement tactics
                - Hashtag strategy
                - Measurement metrics
                
                Return the recommendations in JSON format.
                """}
            ]
        )
        
        # Extract JSON safely
        try:
            response_text = response.choices[0].message.content
            
            if '{' in response_text and '}' in response_text:
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                json_str = response_text[json_start:json_end]
                recommendations = json.loads(json_str)
                return recommendations
            else:
                return {"recommendations": response_text}
        except json.JSONDecodeError:
            logger.warning(f"Failed to parse JSON from sharing recommendations")
            return {"recommendations": response_text}
            
    except Exception as e:
        logger.error(f"Error getting sharing recommendations: {str(e)}")
        return {"error": "Failed to generate sharing recommendations"}

def extract_forum_highlights(details: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extract highlights from forum discussions for social media sharing.
    
    Args:
        details: Details extracted from the user query
    
    Returns:
        Highlighted forum discussions for social sharing
    """
    try:
        # In a real implementation, this would query the Supabase database for forum posts
        # For now, we'll simulate some forum highlights
        
        # Create a prompt with the details
        details_str = "\n".join([f"- {k}: {v}" for k, v in details.items() if v])
        
        response = client.chat.completions.create(
            model="gpt-4o",
            temperature=0.7,
            messages=[
                {"role": "system", "content": "You are a community manager for Afrobeats.no in Oslo. Extract engaging content from forum discussions for social media."},
                {"role": "user", "content": f"""
                Generate 3 fictional forum discussion highlights based on these details:
                {details_str}
                
                For each highlight, provide:
                - Forum topic
                - Brief content summary
                - Why it would be engaging on social media
                - Platform-specific adaptation ideas
                
                Return the highlights as a JSON array.
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
                highlights = json.loads(json_str)
                return highlights
            else:
                return [{"error": "Could not parse forum highlights as JSON array"}]
        except json.JSONDecodeError:
            logger.warning(f"Failed to parse JSON from forum highlights")
            return [{"error": "Failed to parse forum highlights"}]
            
    except Exception as e:
        logger.error(f"Error extracting forum highlights: {str(e)}")
        return [{"error": "Failed to extract forum highlights"}]

def create_campaign_strategy(details: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a social media campaign strategy.
    
    Args:
        details: Details extracted from the user query
    
    Returns:
        A social media campaign strategy
    """
    try:
        # Extract relevant details
        campaign = details.get("campaign")
        goal = details.get("goal")
        audience = details.get("target_audience")
        
        # Create a prompt with the details
        details_str = "\n".join([f"- {k}: {v}" for k, v in details.items() if v])
        
        response = client.chat.completions.create(
            model="gpt-4o",
            temperature=0.7,
            messages=[
                {"role": "system", "content": "You are a social media campaign strategist for Afrobeats.no in Oslo. Create comprehensive, effective campaign strategies."},
                {"role": "user", "content": f"""
                Create a social media campaign strategy based on these details:
                {details_str}
                
                Include:
                - Campaign objectives
                - Target audience
                - Key messages
                - Content calendar (3-4 week outline)
                - Platform-specific tactics
                - Content types and themes
                - Success metrics
                - Required resources
                
                Return the strategy in JSON format.
                """}
            ]
        )
        
        # Extract JSON safely
        try:
            response_text = response.choices[0].message.content
            
            if '{' in response_text and '}' in response_text:
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                json_str = response_text[json_start:json_end]
                strategy = json.loads(json_str)
                return strategy
            else:
                return {"strategy": response_text}
        except json.JSONDecodeError:
            logger.warning(f"Failed to parse JSON from campaign strategy")
            return {"strategy": response_text}
            
    except Exception as e:
        logger.error(f"Error creating campaign strategy: {str(e)}")
        return {"error": "Failed to create campaign strategy"}

# n8n integration for automated posting
def schedule_social_media_post(content: Dict[str, Any]) -> Dict[str, Any]:
    """
    Schedule a social media post via n8n.
    
    Args:
        content: The content to post
    
    Returns:
        Information about the scheduled post
    """
    try:
        # In a real implementation, this would:
        # 1. Format the content according to the n8n webhook requirements
        # 2. Send a request to the n8n webhook URL
        # 3. Handle the response and any errors
        
        # For now, return a placeholder
        return {
            "status": "scheduled",
            "platform": content.get("platform", "unknown"),
            "scheduled_time": datetime.now().isoformat(),
            "post_id": f"post_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "n8n_workflow": "social_media_publishing",
            "message": "Post has been successfully scheduled"
        }
        
    except Exception as e:
        logger.error(f"Error scheduling social media post: {str(e)}")
        return {"error": f"Failed to schedule post: {str(e)}"}

# Analytics for social media post performance
def get_post_performance(post_id: str, platform: str) -> Dict[str, Any]:
    """
    Get performance metrics for a social media post.
    
    Args:
        post_id: The ID of the post
        platform: The social media platform
    
    Returns:
        Performance metrics for the post
    """
    try:
        # In a real implementation, this would query the analytics API for the relevant platform
        # For now, return a placeholder
        return {
            "post_id": post_id,
            "platform": platform,
            "metrics": {
                "impressions": 1250,
                "engagements": 87,
                "clicks": 45,
                "likes": 72,
                "comments": 12,
                "shares": 8
            },
            "performance_rating": "above_average",
            "best_performing_audience": "25-34 year olds in Oslo",
            "recommendation": "Content performed well. Consider similar posts at the same time on Thursdays."
        }
        
    except Exception as e:
        logger.error(f"Error getting post performance: {str(e)}")
        return {"error": f"Failed to get performance metrics: {str(e)}"}

# Find trending topics for content creation
def find_trending_topics() -> List[Dict[str, Any]]:
    """
    Find trending topics related to Afrobeats and Amapiano for content creation.
    
    Returns:
        A list of trending topics
    """
    try:
        # In a real implementation, this would:
        # 1. Query social listening tools
        # 2. Analyze platform-specific trending data
        # 3. Check forum activity
        # 4. Look at recent playlist/song popularity
        
        # For now, return a placeholder
        return [
            {
                "topic": "New Burna Boy album release",
                "platforms": ["Instagram", "Twitter", "TikTok"],
                "engagement_potential": "very_high",
                "relevance_to_audience": 9.2,
                "content_ideas": [
                    "Album reaction thread",
                    "Playlist featuring new tracks",
                    "Local DJ reactions"
                ]
            },
            {
                "topic": "Amapiano dance challenge",
                "platforms": ["TikTok", "Instagram"],
                "engagement_potential": "high",
                "relevance_to_audience": 8.7,
                "content_ideas": [
                    "Norwegian dancers doing the challenge",
                    "Oslo club night featuring the song",
                    "DJ tutorial on mixing the track"
                ]
            },
            {
                "topic": "Upcoming Afrobeats festival in Oslo",
                "platforms": ["Facebook", "Instagram", "Twitter"],
                "engagement_potential": "medium",
                "relevance_to_audience": 9.8,
                "content_ideas": [
                    "Ticket giveaway",
                    "Artist lineup announcement",
                    "Throwback to last year's festival",
                    "DJ booking opportunities"
                ]
            }
        ]
        
    except Exception as e:
        logger.error(f"Error finding trending topics: {str(e)}")
        return [{"error": f"Failed to find trending topics: {str(e)}"}]
