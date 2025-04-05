import os
import sys
import time
from dotenv import load_dotenv
from agent_graph import run_agent_graph

# Load environment variables from .env file if present
load_dotenv()

def check_environment():
    """Check that required environment variables are set."""
    # Check if either GOOGLE_API_KEY or OPENAI_API_KEY is set
    has_google_key = os.environ.get("GOOGLE_API_KEY") is not None
    has_openai_key = os.environ.get("OPENAI_API_KEY") is not None
    
    if not (has_google_key or has_openai_key):
        print("Error: You must set either GOOGLE_API_KEY or OPENAI_API_KEY")
        print("Please set at least one of these before running the application.")
        print("You can set them in a .env file or directly in your environment.")
        sys.exit(1)
    
    # Print which APIs are available
    if has_google_key:
        print("✅ Gemini API key found")
    else:
        print("❌ Gemini API key not found, will skip Gemini API calls")
        
    if has_openai_key:
        print("✅ OpenAI API key found")
    else:
        print("❌ OpenAI API key not found, will skip OpenAI API calls")
        
    # Print which model is being used
    model = os.environ.get("GEMINI_MODEL", "Gemini 2.5 Pro")
    print(f"Using model: {model}")

def interactive_mode():
    """Run the agent system in interactive mode, where users can type queries."""
    model_name = os.environ.get("GEMINI_MODEL", "Gemini 2.5 Pro")
    temperature = os.environ.get("GEMINI_TEMPERATURE", "0.7")
    
    print("\n🎵 Welcome to the Afrobeats.no Agent System 🎵")
    print("------------------------------------------------")
    print(f"Using {model_name} with temperature {temperature}")
    print("Ask anything about Afrobeats/Amapiano DJs, events in Oslo,")
    print("playlists, DJ ratings, or content from the Oslo scene.")
    print("Type 'exit' to quit.")
    print("------------------------------------------------\n")
    
    while True:
        user_query = input("Your question: ")
        
        if user_query.lower() in ["exit", "quit", "q"]:
            print("\nThank you for using the Afrobeats.no Agent System. Goodbye!")
            break
        
        if not user_query.strip():
            continue
        
        print("\nProcessing your query...\n")
        start_time = time.time()
        
        try:
            # Run the agent graph with the user query
            final_state = run_agent_graph(user_query, stream=False)
            
            # Display the final response
            print("\n" + final_state["final_response"])
            
            # Display which agents were used
            used_agents = []
            for key in final_state:
                if key.endswith("_results") and final_state[key]:
                    agent_name = key.replace("_results", "").replace("_", " ").title()
                    used_agents.append(agent_name)
            
            if used_agents:
                print(f"\nAgents used: {', '.join(used_agents)}")
            
            processing_time = time.time() - start_time
            print(f"\n[Query processed in {processing_time:.2f} seconds]\n")
            
        except Exception as e:
            print(f"\nError processing your query: {str(e)}")
            print("Please try again with a different question.\n")

def process_single_query(query):
    """Process a single query and return the result."""
    # Input validation
    if not query or not isinstance(query, str):
        return "Error: Invalid query. Please provide a valid text query."
    
    # Sanitize input - remove potentially harmful characters
    sanitized_query = ''.join(c for c in query if c.isprintable())
    
    try:
        # Run the agent graph with the sanitized query
        final_state = run_agent_graph(sanitized_query, stream=False)
        return final_state["final_response"]
    except Exception as e:
        # Generic error message that doesn't expose implementation details
        print(f"Internal error: {str(e)}")  # Log full error for debugging
        return "Sorry, I encountered an error processing your query. Please try again with a different question."

def main():
    """Main entry point for the application."""
    # Check environment variables
    check_environment()
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--query" and len(sys.argv) > 2:
            # Process a single query from command line
            query = " ".join(sys.argv[2:])
            print(process_single_query(query))
        elif sys.argv[1] == "--model":
            if len(sys.argv) > 2:
                if sys.argv[2] in ["pro", "flash"]:
                    model = "Gemini 2.5 Pro" if sys.argv[2] == "pro" else "Gemini 2.5 Flash"
                    os.environ["GEMINI_MODEL"] = model
                    print(f"Using model: {model}")
                    # Run in interactive mode with the specified model
                    interactive_mode()
                else:
                    print(f"Unknown model: {sys.argv[2]}")
                    print("Available models: pro, flash")
            else:
                print("Please specify a model: pro or flash")
        elif sys.argv[1] == "--help":
            print("Usage:")
            print("  python run.py                   # Run in interactive mode")
            print("  python run.py --query \"...\"     # Process a single query")
            print("  python run.py --model pro       # Use Gemini 2.5 Pro model")
            print("  python run.py --model flash     # Use Gemini 2.5 Flash model")
            print("  python run.py --help            # Show this help message")
        else:
            print(f"Unknown argument: {sys.argv[1]}")
            print("Use --help to see available options.")
    else:
        # Run in interactive mode
        interactive_mode()

if __name__ == "__main__":
    main()