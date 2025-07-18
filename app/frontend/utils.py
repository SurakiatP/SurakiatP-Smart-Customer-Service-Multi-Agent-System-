"""
Frontend Utilities

Helper functions for the Streamlit interface.
"""

import streamlit as st
from datetime import datetime
from typing import Dict, Any, Optional
import hashlib
import json

def format_message(content: str, max_length: int = 500) -> str:
    """Format message content for display"""
    if len(content) <= max_length:
        return content
    
    return content[:max_length] + "..."

def calculate_response_time(start_time: datetime, end_time: datetime) -> float:
    """Calculate response time in seconds"""
    delta = end_time - start_time
    return round(delta.total_seconds(), 2)

def get_user_session() -> Dict[str, Any]:
    """Get or create user session data"""
    if "user_session" not in st.session_state:
        # Generate unique user ID based on session
        session_id = hashlib.md5(str(datetime.now()).encode()).hexdigest()[:8]
        
        st.session_state.user_session = {
            "user_id": f"user_{session_id}",
            "session_start": datetime.now(),
            "message_count": 0,
            "preferences": {
                "show_confidence": True,
                "show_agent_info": True,
                "auto_scroll": True
            }
        }
    
    return st.session_state.user_session

def update_message_count():
    """Update message count in session"""
    session = get_user_session()
    session["message_count"] += 1
    st.session_state.user_session = session

def format_timestamp(timestamp: datetime, format_type: str = "time") -> str:
    """Format timestamp for display"""
    if format_type == "time":
        return timestamp.strftime("%H:%M")
    elif format_type == "datetime":
        return timestamp.strftime("%Y-%m-%d %H:%M")
    elif format_type == "relative":
        delta = datetime.now() - timestamp
        if delta.seconds < 60:
            return "Just now"
        elif delta.seconds < 3600:
            return f"{delta.seconds // 60} minutes ago"
        else:
            return f"{delta.seconds // 3600} hours ago"
    
    return timestamp.isoformat()

def create_download_link(data: Any, filename: str, link_text: str) -> str:
    """Create downloadable link for data"""
    if isinstance(data, dict) or isinstance(data, list):
        data = json.dumps(data, indent=2, default=str)
    
    # Convert to base64
    import base64
    b64_data = base64.b64encode(data.encode()).decode()
    
    return f'<a href="data:application/json;base64,{b64_data}" download="{filename}">{link_text}</a>'

def apply_custom_css():
    """Apply custom CSS styling"""
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    
    .chat-message {
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    
    .user-message {
        background-color: #e8f4f8;
        border-left-color: #2e86de;
    }
    
    .assistant-message {
        background-color: #f0f8e8;
        border-left-color: #27ae60;
    }
    
    .metrics-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        border: 1px solid #dee2e6;
    }
    
    .status-healthy {
        color: #27ae60;
        font-weight: bold;
    }
    
    .status-warning {
        color: #f39c12;
        font-weight: bold;
    }
    
    .status-error {
        color: #e74c3c;
        font-weight: bold;
    }
    
    .sidebar-section {
        margin-bottom: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)

def show_typing_indicator():
    """Show typing indicator animation"""
    placeholder = st.empty()
    
    with placeholder.container():
        st.markdown("""
        <div style="display: flex; align-items: center; padding: 1rem;">
            <div style="margin-right: 0.5rem;">AI is typing</div>
            <div class="typing-dots">
                <span>.</span><span>.</span><span>.</span>
            </div>
        </div>
        
        <style>
        .typing-dots span {
            animation: typing 1.4s infinite;
        }
        .typing-dots span:nth-child(2) {
            animation-delay: 0.2s;
        }
        .typing-dots span:nth-child(3) {
            animation-delay: 0.4s;
        }
        
        @keyframes typing {
            0%, 60%, 100% {
                opacity: 0;
            }
            30% {
                opacity: 1;
            }
        }
        </style>
        """, unsafe_allow_html=True)
    
    return placeholder

def validate_user_input(message: str) -> tuple[bool, str]:
    """Validate user input"""
    if not message or not message.strip():
        return False, "Message cannot be empty"
    
    if len(message) > 1000:
        return False, "Message too long (max 1000 characters)"
    
    # Check for spam patterns
    if message.count("!") > 5:
        return False, "Too many exclamation marks"
    
    return True, "Valid"

def get_conversation_summary(messages: list) -> Dict[str, Any]:
    """Get conversation summary statistics"""
    if not messages:
        return {
            "total_messages": 0,
            "user_messages": 0,
            "assistant_messages": 0,
            "avg_response_time": 0,
            "conversation_duration": 0
        }
    
    user_msgs = [m for m in messages if m.get("role") == "user"]
    assistant_msgs = [m for m in messages if m.get("role") == "assistant"]
    
    # Calculate conversation duration
    if len(messages) >= 2:
        start_time = messages[0].get("timestamp", datetime.now())
        end_time = messages[-1].get("timestamp", datetime.now())
        duration = (end_time - start_time).total_seconds() / 60  # in minutes
    else:
        duration = 0
    
    return {
        "total_messages": len(messages),
        "user_messages": len(user_msgs),
        "assistant_messages": len(assistant_msgs),
        "conversation_duration": round(duration, 1),
        "avg_messages_per_minute": round(len(messages) / max(duration, 1), 1)
    }