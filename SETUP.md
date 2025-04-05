# Setup Instructions for Afrobeats.no Agent System

## Prerequisites
- Python 3.8+ (3.10+ recommended)
- Node.js 16+ (18+ recommended)
- npm or yarn
- Git

## Quick Installation

For a quick installation, use the setup script:

```bash
chmod +x run_app.sh
./run_app.sh
```

This script will:
1. Install all backend dependencies
2. Set up the `.env` file (prompting for API keys)
3. Install frontend dependencies
4. Start both backend and frontend servers

## Manual Installation

### Backend Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/afrobeats-agents.git
   cd afrobeats-agents
   ```

2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the root directory:
   ```
   # Required: At least one of these API keys
   GOOGLE_API_KEY=your_gemini_api_key_here
   OPENAI_API_KEY=your_openai_api_key_here  # Optional fallback

   # LLM Configuration
   GEMINI_MODEL=gemini-1.5-pro
   GEMINI_TEMPERATURE=0.7

   # OpenAI Configuration (if using OpenAI fallback)
   OPENAI_MODEL=gpt-4-turbo
   OPENAI_TEMPERATURE=0.7

   # Server Configuration
   PORT=8000
   ENVIRONMENT=development
   ENABLE_CACHE=true
   CACHE_EXPIRY_HOURS=24

   # Security (for production)
   API_KEY=  # Generate a secure key for production
   ALLOWED_ORIGINS=http://localhost:3000  # Add production domain if needed
   ```

5. Start the backend server:
   ```bash
   python api.py
   ```
   The API server will be available at http://localhost:8000

### Frontend Setup

1. Navigate to the web directory:
   ```bash
   cd web
   ```

2. Install dependencies:
   ```bash
   npm install
   # or if using yarn
   yarn install
   ```

3. Start the development server:
   ```bash
   npm run dev
   # or if using yarn
   yarn dev
   ```
   The frontend will be available at http://localhost:3000

## System Architecture

### Agent Architecture
The system uses a coordinator-based multi-agent architecture:

1. **Coordinator Agent**:
   - Analyzes user queries to determine which specialized agents to invoke
   - Routes queries appropriately based on intent detection

2. **Specialized Agents**:
   - **DJ Booking Agent**: Handles DJ booking requests and availability queries
   - **Event Discovery Agent**: Provides information about upcoming events
   - **Playlist Curator Agent**: Creates and recommends playlists
   - **DJ Rating Agent**: Handles DJ rating information
   - **Content Agent**: Delivers articles and content about the scene
   - **Social Media Agent**: Handles social media information and content
   - **Analytics Agent**: Tracks user interactions (internal)
   - **Artist Agent**: Provides information about artists

3. **Agent Workflow**:
   - User query is analyzed by the coordinator
   - Relevant specialized agents are invoked in parallel
   - Results are synthesized into a coherent response
   - Response is returned to the user

### Component Integration
- **FastAPI Backend**: Serves API endpoints and manages agent orchestration
- **Next.js Frontend**: Provides the user interface for interacting with the system
- **LangGraph**: Manages the agent workflow and parallel execution
- **Pydantic**: Ensures type safety and validation throughout the system

## Security Best Practices

1. **API Key Management**:
   - Never commit `.env` files to version control
   - Use environment variables for all sensitive credentials
   - Implement proper key rotation practices for production

2. **Input Validation**:
   - All user input is validated and sanitized
   - Query length limits are enforced to prevent abuse

3. **Error Handling**:
   - Generic error messages are shown to users
   - Detailed error logs are kept for debugging

4. **Rate Limiting**:
   - Implement rate limiting for production deployments
   - Use token bucket algorithm for API endpoint protection

## Troubleshooting

### Common Issues

1. **API Key Issues**:
   - Ensure that at least one of `GOOGLE_API_KEY` or `OPENAI_API_KEY` is set
   - Verify that your keys have the necessary permissions

2. **Port Conflicts**:
   - If port 8000 is in use, modify the `PORT` in your `.env` file
   - For port 3000 conflicts, use `npm run dev -- -p 3001` for an alternative port

3. **Module Not Found Errors**:
   - Ensure all dependencies are installed with `pip install -r requirements.txt`
   - Check that the virtual environment is activated

4. **Frontend Connection Issues**:
   - Verify that the backend URL in the frontend configuration matches your setup
   - Check that CORS settings allow your frontend origin

### Logging

Logs are stored in the following files:
- `api.log`: API server logs
- `server.log`: Detailed server logs including agent activities

For debugging, you can increase log verbosity by adjusting the logger configuration in `api.py`.

## Production Deployment

For production deployments, consider the following additional steps:

1. **Set Production Environment**:
   - Set `ENVIRONMENT=production` in `.env`
   - Generate and set a secure `API_KEY`
   - Set `ALLOWED_ORIGINS` to your production domain

2. **Use Process Manager**:
   - Deploy with PM2 or similar process manager:
     ```bash
     npm install -g pm2
     pm2 start api.py --interpreter python3
     ```

3. **Reverse Proxy**:
   - Set up Nginx or Caddy as a reverse proxy
   - Configure SSL certificates for HTTPS
   - Enable HTTP/2 for improved performance

4. **Monitoring**:
   - Implement monitoring and alerting
   - Set up error reporting to track issues

## Additional Resources

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Gemini API Documentation](https://ai.google.dev/docs/gemini_api_overview)
- [Next.js Documentation](https://nextjs.org/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)