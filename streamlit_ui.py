import streamlit as st
import time
import os
from dotenv import load_dotenv
from agent_graph import run_agent_graph

# Load environment variables
load_dotenv()

# Set page config (MUST be the first Streamlit command)
st.set_page_config(
    page_title="Afrobeats.no | DJ Booking & Events",
    page_icon="🎵",
    layout="wide",
)

# Custom CSS for Afrobeats.no styling
st.markdown("""
<style>
    /* Custom color palette */
    :root {
        --primary: #2A2356;
        --secondary: #FFD700;
        --tertiary: #E25822;
        --neutral: #F8F9FA;
        --dark: #0A0A0A;
    }
    
    /* Background pattern with African-inspired elements */
    .stApp {
        background-image: 
            radial-gradient(circle at center, 
                rgba(234, 179, 8, 0.1) 0%, 
                transparent 70%),
            linear-gradient(45deg, 
                transparent 48%, 
                rgba(42, 35, 86, 0.1) 50%, 
                transparent 52%);
        background-attachment: fixed;
    }
    
    /* Glassmorphism card effect */
    div.css-1r6slb0.e1tzin5v2 {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 20px;
        margin: 10px 0;
        transition: transform 0.3s ease;
    }
    
    div.css-1r6slb0.e1tzin5v2:hover {
        transform: translateY(-5px);
    }
    
    /* Header styling */
    h1 {
        color: var(--primary);
        font-family: 'Poppins', sans-serif;
        font-weight: 800;
        letter-spacing: -0.5px;
    }
    
    h2, h3, h4 {
        color: var(--primary);
        font-family: 'Poppins', sans-serif;
        font-weight: 600;
    }
    
    /* Button styling */
    .stButton>button {
        color: #FFFFFF;
        background-color: var(--primary);
        border: none;
        border-radius: 50px;
        padding: 8px 16px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        background-color: var(--secondary);
        color: var(--dark);
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: rgba(42, 35, 86, 0.95);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3 {
        color: var(--neutral);
    }
    
    section[data-testid="stSidebar"] .stMarkdown {
        color: var(--neutral);
    }
    
    /* Custom progress bar */
    .stProgress > div > div {
        background-color: var(--tertiary);
    }
    
    /* Input field styling */
    .stTextInput > div > div > input {
        border-radius: 50px;
        border: 1px solid rgba(42, 35, 86, 0.2);
        padding: 15px 20px;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: var(--secondary);
        box-shadow: 0 0 0 2px rgba(255, 215, 0, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# Check for required API keys
has_google_key = os.environ.get("GOOGLE_API_KEY") is not None
has_openai_key = os.environ.get("OPENAI_API_KEY") is not None

if not (has_google_key or has_openai_key):
    st.error("⚠️ API keys not found! Please set either GOOGLE_API_KEY or OPENAI_API_KEY environment variable.")
    st.stop()

# Hero section with header
col1, col2 = st.columns([2, 1])
with col1:
    st.title("🎵 Afrobeats.no")
    st.markdown("""
    <h3 style="font-weight: 400; margin-top: -10px; color: #666;">
    The ultimate platform for Afrobeats & Amapiano in Oslo
    </h3>
    """, unsafe_allow_html=True)

with col2:
    # API status indicators
    if has_google_key:
        st.success("✅ Gemini AI Connected")
    else:
        st.warning("❌ Gemini API not connected")
        
    if has_openai_key:
        st.success("✅ OpenAI Connected")
    else:
        st.warning("❌ OpenAI not connected")

# Main content area
st.markdown("### How can I assist with your Afrobeats journey today?")

# Query input with modern styling
query = st.text_input("", 
                    placeholder="e.g., 'Find me an Amapiano DJ for a party next weekend in Oslo'",
                    key="query_input")

# Create three columns for the example sections
col1, col2, col3 = st.columns(3)

# Column 1: DJ Booking options
with col1:
    st.markdown("#### 🎧 DJ Booking")
    if st.button("Find a DJ for a wedding"):
        query = "I need a DJ who specializes in Afrobeats for a wedding in Oslo next month. Budget is around 10000 NOK."
    if st.button("Top Amapiano DJs"):
        query = "Who are the highest-rated Amapiano DJs in Oslo right now?"

# Column 2: Events options
with col2:
    st.markdown("#### 📅 Events & Venues")
    if st.button("Discover upcoming events"):
        query = "What are the upcoming Afrobeats events in Oslo this weekend?"
    if st.button("Best venues for Afrobeats"):
        query = "What are the best venues for Afrobeats nights in Oslo?"

# Column 3: Music & Artists options
with col3:
    st.markdown("#### 🎵 Music & Artists")
    if st.button("Create a playlist"):
        query = "Help me create an Amapiano playlist for a workout session."
    if st.button("Artist submissions"):
        query = "I'm an artist and want to submit my music to afrobeats.no. How do I do that?"

# Process query
if query:
    # Input validation
    if len(query) > 500:
        st.warning("Query is too long. Please limit your query to 500 characters.")
        query = query[:500] + "..."
    
    # Sanitize input
    sanitized_query = ''.join(c for c in query if c.isprintable())
    
    # Create a glassmorphism card for results
    st.markdown("---")
    st.markdown("### 🔍 Results")
    result_container = st.container()
    
    # Create a spinner while processing
    with st.spinner("Processing your query..."):
        # Stream the response
        message_placeholder = result_container.empty()
        
        start_time = time.time()
        try:
            # Run the agent graph with the sanitized query
            final_state = run_agent_graph(sanitized_query, stream=False)
            
            # Display the final response
            if final_state and "final_response" in final_state:
                message_placeholder.markdown(final_state["final_response"])
            else:
                message_placeholder.error("No response received. Please try again.")
                
            # Display which agents were used
            used_agents = []
            for key in final_state:
                if key.endswith("_results") and final_state[key]:
                    agent_name = key.replace("_results", "").replace("_", " ").title()
                    used_agents.append(agent_name)
            
            if used_agents:
                st.success(f"✨ Agents used: {', '.join(used_agents)}")
                
            # Execution time
            end_time = time.time()
            st.info(f"⏱️ Query processed in {end_time - start_time:.2f} seconds")
            
        except Exception as e:
            # Log the full error but show a generic message to the user
            print(f"Error details: {str(e)}")
            st.error("Sorry, I encountered an error processing your query. Please try again with a different question.")

# Display project information in the sidebar
with st.sidebar:
    st.title("Afrobeats.no")
    st.markdown("""
    <p style="margin-top: -20px; color: rgba(255,255,255,0.7);">Agent System</p>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    This multi-agent AI system helps you with:
    - 🎧 DJ Booking for events in Oslo
    - 📅 Event discovery and promotion
    - 🎵 Playlist curation and recommendations
    - ⭐ DJ ratings and reviews
    - 📰 Content about the Oslo scene
    - 🌐 Social media integration
    - 📊 Analytics and insights
    - 👩‍🎤 Artist discovery
    """)
    
    # Model selection
    st.subheader("Model Settings")
    selected_model = st.selectbox(
        "AI Model",
        ["Gemini 2.5 Pro", "Gemini 2.5 Flash"],
        index=0,
        help="Models map to: Gemini 2.5 Pro -> models/gemini-2.5-pro-preview-03-25, Gemini 2.5 Flash -> models/gemini-2.0-flash"
    )
    
    # Temperature slider with styled slider
    temperature = st.slider("Creativity Level", 0.0, 1.0, 0.7, 0.1)
    
    # Save settings to session state
    if "model_settings" not in st.session_state:
        st.session_state.model_settings = {}
    
    st.session_state.model_settings["model"] = selected_model
    st.session_state.model_settings["temperature"] = temperature
    
    # Security notice
    st.subheader("Security Status")
    st.markdown("""
    🔒 **Secure Mode Enabled**:
    - Input validation & sanitization
    - API key protection
    - Error isolation
    
    [View Security Policy](https://github.com/your-org/afrobeats-agents/blob/main/SECURITY.md)
    """)
    
    st.markdown("---")
    
    # Footer
    st.markdown("""
    <div style="text-align: center; color: rgba(255,255,255,0.5); font-size: 0.8em;">
        <p>© 2025 Afrobeats.no</p>
        <p>Oslo, Norway</p>
    </div>
    """, unsafe_allow_html=True)