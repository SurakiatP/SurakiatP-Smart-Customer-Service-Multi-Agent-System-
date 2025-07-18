# Streamlit Customer Service AI - Working Version
import streamlit as st
import requests
import json
from datetime import datetime
import time
import uuid

# Page configuration
st.set_page_config(
    page_title="🤖 AI Customer Service",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    /* Main container */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* Chat messages */
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 20px 20px 5px 20px;
        margin: 0.5rem 0 0.5rem 20%;
        box-shadow: 0 2px 10px rgba(102, 126, 234, 0.3);
        font-size: 16px;
        line-height: 1.5;
    }
    
    .assistant-message {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 20px 20px 20px 5px;
        margin: 0.5rem 20% 0.5rem 0;
        box-shadow: 0 2px 10px rgba(240, 147, 251, 0.3);
        font-size: 16px;
        line-height: 1.5;
    }
    
    .agent-info {
        font-size: 12px;
        opacity: 0.8;
        margin-top: 0.5rem;
        font-style: italic;
    }
    
    .confidence-badge {
        display: inline-block;
        background: rgba(255, 255, 255, 0.2);
        padding: 0.2rem 0.5rem;
        border-radius: 10px;
        font-size: 11px;
        margin-left: 0.5rem;
    }
    
    /* Header styling */
    .main-header {
        text-align: center;
        color: #2c3e50;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .subtitle {
        text-align: center;
        color: #7f8c8d;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    
    /* Sidebar styling */
    .sidebar .sidebar-content {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    /* Metrics styling */
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
        text-align: center;
    }
    
    .metric-value {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2c3e50;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #7f8c8d;
        margin-top: 0.25rem;
    }
    
    /* Chat input styling */
    .stChatInput > div > div > textarea {
        border-radius: 25px;
        border: 2px solid #e3e6ea;
        font-size: 16px;
        padding: 0.75rem 1rem;
    }
    
    .stChatInput > div > div > textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
    }
    
    /* Buttons */
    .stButton > button {
        border-radius: 20px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    
    /* Success/Error messages */
    .stAlert {
        border-radius: 10px;
        font-size: 14px;
    }
    
    /* Loading spinner */
    .stSpinner > div {
        border-color: #667eea !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "user_id" not in st.session_state:
    st.session_state.user_id = f"user_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = f"conv_{uuid.uuid4().hex[:8]}"

# Sidebar
with st.sidebar:
    st.markdown("### 📊 System Dashboard")
    
    # Try to get real metrics
    try:
        metrics_response = requests.get(
            "http://localhost:8000/api/v1/analytics/metrics/overview",
            timeout=5
        )
        if metrics_response.status_code == 200:
            metrics = metrics_response.json()["metrics"]
            
            # Display metrics with custom styling
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{metrics.get('avg_response_time', 2.3)}s</div>
                <div class="metric-label">Avg Response Time</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{metrics.get('customer_satisfaction', 4.8)}/5</div>
                <div class="metric-label">Satisfaction Score</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{metrics.get('total_conversations', 0)}</div>
                <div class="metric-label">Total Conversations</div>
            </div>
            """, unsafe_allow_html=True)
            
        else:
            # Fallback metrics
            st.metric("Response Time", "2.3s", delta="-0.5s")
            st.metric("Satisfaction", "4.8/5", delta="+0.2")
            st.metric("Conversations", "1,247", delta="+12%")
            
    except:
        # Offline metrics
        st.metric("Response Time", "2.3s", delta="-0.5s")
        st.metric("Satisfaction", "4.8/5", delta="+0.2")
        st.metric("Conversations", "1,247", delta="+12%")
    
    st.markdown("---")
    
    # Settings
    st.markdown("### ⚙️ Settings")
    show_confidence = st.checkbox("Show AI Confidence", value=True)
    show_agent_info = st.checkbox("Show Agent Info", value=True)
    show_timestamps = st.checkbox("Show Timestamps", value=False)
    
    st.markdown("---")
    
    # Quick actions
    st.markdown("### 🚀 Quick Actions")
    
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.conversation_id = f"conv_{uuid.uuid4().hex[:8]}"
        st.rerun()
    
    if st.button("📊 View Analytics", use_container_width=True):
        st.info("Analytics dashboard coming soon!")
    
    if st.button("💡 Example Queries", use_container_width=True):
        example_queries = [
            "What's the price of premium plan?",
            "I want to return my order",
            "I can't log into my account"
        ]
        st.write("Try these example queries:")
        for query in example_queries:
            st.code(query)

# Main header
st.markdown('<h1 class="main-header">🤖 Smart Customer Service AI</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Get instant help with products, refunds, and technical issues</p>', unsafe_allow_html=True)

# Health check
try:
    health_response = requests.get("http://localhost:8000/health", timeout=3)
    if health_response.status_code == 200:
        st.success("✅ AI Service is online and ready to help!")
    else:
        st.warning("⚠️ AI Service is experiencing issues")
except:
    st.error("❌ Cannot connect to AI Service. Please check if the backend is running.")

# Chat container
chat_container = st.container()

# Display chat messages
with chat_container:
    if st.session_state.messages:
        for i, message in enumerate(st.session_state.messages):
            if message["role"] == "user":
                # User message (right side)
                col1, col2 = st.columns([1, 4])
                with col2:
                    timestamp_str = ""
                    if show_timestamps and "timestamp" in message:
                        timestamp_str = message["timestamp"].strftime(" • %H:%M")
                    
                    st.markdown(f"""
                    <div class="user-message">
                        <strong>You{timestamp_str}</strong><br>
                        {message["content"]}
                    </div>
                    """, unsafe_allow_html=True)
            
            elif message["role"] == "assistant":
                # Assistant message (left side)
                col1, col2 = st.columns([4, 1])
                with col1:
                    agent_info = ""
                    confidence_badge = ""
                    timestamp_str = ""
                    
                    if show_agent_info and "agent" in message:
                        agent_info = f" ({message['agent']})"
                    
                    if show_confidence and "confidence" in message:
                        confidence_pct = int(message["confidence"] * 100)
                        confidence_badge = f'<span class="confidence-badge">{confidence_pct}% confident</span>'
                    
                    if show_timestamps and "timestamp" in message:
                        timestamp_str = message["timestamp"].strftime(" • %H:%M")
                    
                    st.markdown(f"""
                    <div class="assistant-message">
                        <strong>AI Assistant{agent_info}{timestamp_str}</strong>{confidence_badge}<br>
                        {message["content"]}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Add suggestions if available
                    if "suggestions" in message and message["suggestions"]:
                        st.markdown("**💡 Suggestions:**")
                        cols = st.columns(len(message["suggestions"][:3]))  # Max 3 suggestions
                        for j, suggestion in enumerate(message["suggestions"][:3]):
                            with cols[j]:
                                if st.button(f"💬 {suggestion}", key=f"suggestion_{i}_{j}"):
                                    # Add suggestion as new user message
                                    suggestion_message = {
                                        "role": "user",
                                        "content": suggestion,
                                        "timestamp": datetime.now()
                                    }
                                    st.session_state.messages.append(suggestion_message)
                                    st.rerun()
    else:
        # Welcome message
        st.markdown("""
        <div class="assistant-message">
            <strong>AI Assistant</strong><br>
            👋 Welcome! I'm your AI customer service assistant. I can help you with:
            <br><br>
            • 💰 <strong>Product Information</strong> - Pricing, features, comparisons<br>
            • 🔄 <strong>Refunds & Returns</strong> - Policy info and processing<br>
            • 🛠️ <strong>Technical Support</strong> - Troubleshooting and help<br>
            <br>
            What can I help you with today?
        </div>
        """, unsafe_allow_html=True)

# Chat input
st.markdown("### 💬 Ask me anything...")
if prompt := st.chat_input("Type your message here... (e.g., 'What's the price of premium plan?')"):
    # Generate unique message ID
    message_id = f"msg_{int(time.time() * 1000)}_{len(st.session_state.messages)}"
    
    # Add user message to chat
    user_message = {
        "id": message_id,
        "role": "user",
        "content": prompt,
        "timestamp": datetime.now()
    }
    st.session_state.messages.append(user_message)
    
    # Call API for AI response
    with st.spinner("🤖 AI is thinking..."):
        try:
            response = requests.post(
                "http://localhost:8000/api/v1/chat",
                json={
                    "message": prompt,
                    "user_id": st.session_state.user_id,
                    "conversation_id": st.session_state.conversation_id
                },
                timeout=30
            )
            
            if response.status_code == 200:
                ai_response = response.json()
                
                # Generate AI message ID
                ai_message_id = f"msg_{int(time.time() * 1000) + 1}_{len(st.session_state.messages)}"
                
                # Add AI response to chat
                assistant_message = {
                    "id": ai_message_id,
                    "role": "assistant",
                    "content": ai_response["response"],
                    "agent": ai_response["agent_used"],
                    "confidence": ai_response["confidence"],
                    "suggestions": ai_response.get("suggestions", []),
                    "timestamp": datetime.now()
                }
                st.session_state.messages.append(assistant_message)
                
                # Update conversation ID
                st.session_state.conversation_id = ai_response.get("conversation_id", st.session_state.conversation_id)
                
                # Rerun to show new messages
                st.rerun()
            
            else:
                st.error(f"❌ API Error: {response.status_code}")
                
        except requests.exceptions.Timeout:
            st.error("⏰ Request timed out. Please try again.")
        except requests.exceptions.ConnectionError:
            st.error("🔌 Cannot connect to AI service. Please check if the backend is running on http://localhost:8000")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #7f8c8d; font-size: 14px; padding: 1rem;">
    🤖 <strong>Smart Customer Service AI</strong> | 
    Built with FastAPI, LangChain & Streamlit | 
    <a href="http://localhost:8000/docs" target="_blank">API Documentation</a>
</div>
""", unsafe_allow_html=True)