#!/bin/bash
cd /Users/echo/afrobeats-agents
echo "🎵 Starting Afrobeats.no Agent System UI..."
echo "🔗 The UI will be available at: http://localhost:8501"
streamlit run streamlit_ui.py --server.port=8501 --server.address=0.0.0.0 --server.headless=true --theme.primaryColor="#2A2356" --theme.secondaryBackgroundColor="#F8F9FA" --theme.textColor="#0A0A0A" --theme.font="sans serif"