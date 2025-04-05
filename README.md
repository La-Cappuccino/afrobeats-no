# Afrobeats.no Agentic Platform

## Project Overview
A multi-agent AI system focused on DJ booking, event marketing, playlist curation, and DJ ratings in Oslo, Norway. The platform provides comprehensive information about the Afrobeats and Amapiano music scene in Oslo.

## Key Features
- **DJ Booking System**: Book Afrobeats/Amapiano DJs for events in Oslo with pricing and availability details
- **Event Discovery**: Find upcoming Afrobeats/Amapiano events in Oslo with details on venues, times, and ticket information
- **Playlist Curation**: Get personalized Afrobeats/Amapiano playlist recommendations based on preferences
- **DJ Rating System**: View ratings and reviews for DJs in the Oslo scene
- **Content Hub**: Access articles, interviews, and news about the Oslo Afrobeats/Amapiano scene
- **Social Media Integration**: Get updates from key social media accounts in the Oslo scene

## Architecture

### System Architecture
This platform uses a multi-agent architecture with LangGraph for orchestration, enabling parallel processing and specialized handling of different query types.

```
┌───────────────────┐     ┌──────────────────┐
│                   │     │                   │
│   Client (Web/    │────▶│   API Gateway    │
│   Streamlit)      │     │   (FastAPI)      │
│                   │     │                   │
└───────────────────┘     └────────┬─────────┘
                                   │
                           ┌───────▼─────────┐
                           │                 │
                           │  Coordinator    │
                           │     Agent       │
                           │                 │
                           └─┬─────┬─────┬───┘
                             │     │     │
              ┌──────────────┘     │     └──────────────┐
              │                    │                    │
    ┌─────────▼────────┐  ┌────────▼─────────┐  ┌───────▼───────────┐
    │                  │  │                  │  │                   │
    │   DJ Booking     │  │  Event Discovery │  │  Playlist Curator │
    │     Agent        │  │      Agent       │  │       Agent       │
    │                  │  │                  │  │                   │
    └──────────────────┘  └──────────────────┘  └───────────────────┘
              │                    │                    │
              └──────────────┐     │     ┌──────────────┘
                             │     │     │
                           ┌─┴─────┴─────┴───┐
                           │                 │
                           │   Synthesizer   │
                           │     Agent       │
                           │                 │
                           └─────────────────┘
```

### Technical Stack

#### Backend
- **LangGraph**: Orchestrates the multi-agent system with a directed graph architecture
- **Pydantic**: Provides robust data validation for queries and responses
- **FastAPI**: Serves the API endpoints with automatic documentation
- **LLM Integration**: Gemini 2.5 Pro (primary), OpenAI fallback capability
- **Uvicorn**: ASGI server for high-performance API serving

#### Frontend
- **Next.js**: React framework for the web interface
- **Tailwind CSS**: Utility-first CSS framework
- **Framer Motion**: Animation library for smooth UI transitions
- **React Icons**: Icon library for UI elements
- **TypeScript**: Type-safe JavaScript for reliable code

### Agent System Architecture

The system utilizes a coordinator-based multi-agent architecture with the following components:

1. **Coordinator Agent**: Analyzes user queries and determines which specialized agents to invoke
2. **Specialized Agents**:
   - **DJ Booking Agent**: Handles queries about booking DJs
   - **Event Discovery Agent**: Provides information about upcoming events
   - **Playlist Curator Agent**: Creates and recommends personalized playlists
   - **DJ Rating Agent**: Provides information on DJ ratings and reviews
   - **Content Agent**: Delivers articles and industry information
   - **Social Media Agent**: Provides updates from relevant social media accounts
   - **Analytics Agent**: Tracks and analyzes user interactions (internal use)
3. **Response Synthesizer**: Combines outputs from multiple agents into coherent responses

### Data Flow
1. User submits a query via the web interface or Streamlit UI
2. FastAPI forwards the query to the agent system
3. Coordinator Agent analyzes the query and routes to appropriate specialized agents
4. Specialized agents process the query in parallel
5. Response Synthesizer combines the outputs
6. Final response is returned to the user

## Project Structure
```
afrobeats-agents/
├── agents/                 # Specialized agent implementations
│   ├── analytics_agent.py  # Tracks user interactions
│   ├── artist_agent.py     # Artist information
│   ├── content_agent.py    # Content and articles
│   ├── coordinator_agent.py # Query routing logic
│   ├── dj_booking_agent.py # DJ booking functionality
│   ├── dj_rating_agent.py  # DJ ratings and reviews
│   ├── event_discovery_agent.py # Event information
│   ├── playlist_agent.py   # Playlist recommendations
│   └── social_media_agent.py # Social media updates
├── cache/                  # Response cache storage
├── web/                    # Next.js frontend
│   ├── app/                # Next.js application routes
│   ├── components/         # Reusable UI components
│   ├── lib/                # Shared utilities
│   ├── public/             # Static assets
│   └── styles/             # CSS and styling
├── agent_graph.py          # Agent orchestration graph
├── api.py                  # FastAPI server implementation
├── run.py                  # CLI for interactive queries
├── run_app.sh              # Setup and run script
├── run_streamlit.sh        # Streamlit UI launcher
├── streamlit_ui.py         # Streamlit interface
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variables template
├── README.md               # Project documentation
├── SECURITY.md             # Security guidelines
└── SETUP.md                # Detailed setup instructions
```

## Setup Instructions
See [SETUP.md](SETUP.md) for detailed installation and configuration instructions.

## API Documentation

### Main Endpoint
```
POST /query
```

**Request Body:**
```json
{
  "query": "string",
  "api_preference": "string",  // Optional: "google" or "openai"
  "use_cache": "boolean"       // Optional: defaults to true
}
```

**Response:**
```json
{
  "response": "string",
  "timestamp": "string",
  "agent_used": "string"
}
```

## Security
The system implements security best practices as detailed in [SECURITY.md](SECURITY.md), including:
- API key management via environment variables
- Input validation and sanitization
- Error handling without exposing sensitive information
- Rate limiting and fallback mechanisms
- CORS configuration for web security

## Extensibility

### Adding New Agents
The system is designed for extensibility. To add a new specialized agent:

1. Create a new agent file in the `agents/` directory
2. Define the agent's prompt template and processing logic
3. Register the agent in `agent_graph.py`
4. Update the coordinator's routing logic to recognize relevant queries

### LLM Provider Integration
The system supports multiple LLM providers:
- Google Gemini 2.5 Pro (primary)
- OpenAI (fallback)

To integrate additional providers:
1. Add API key configuration in `.env`
2. Implement provider-specific client logic in `api.py`
3. Update the fallback logic to include the new provider

## Performance Optimization
- Response caching for frequently asked queries
- Provider fallback for reliability
- Parallel agent execution for faster responses

## Logging and Monitoring
- System logs stored in `api.log` and `server.log`
- Query tracking for analytics
- Error monitoring and reporting

## Development Workflow
1. Set up the development environment as described in SETUP.md
2. Run the application locally with `run_app.sh`
3. Test new features with the interactive console using `run.py`
4. Use the Streamlit UI for visual testing with `run_streamlit.sh`

## License
This project is proprietary and confidential. All rights reserved.

## Contact
For inquiries about this platform, contact info@afrobeats.no.
