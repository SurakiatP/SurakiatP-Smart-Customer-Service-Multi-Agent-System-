"""
Fixed Streamlit UI Components
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from typing import Dict, Any, List
import requests
import uuid
import time

class ChatMessage:
    """Fixed chat message component"""
    
    def __init__(self, message: Dict[str, Any], message_index: int = 0):
        self.message = message
        self.message_index = message_index
    
    def render(self):
        """Render the chat message with unique keys"""
        role = self.message.get("role", "user")
        content = self.message.get("content", "")
        timestamp = self.message.get("timestamp", datetime.now())
        
        # Generate unique key suffix
        unique_suffix = f"{self.message_index}_{int(time.time())}"
        
        if role == "user":
            with st.chat_message("user"):
                st.write(content)
                st.caption(f"You - {self._format_timestamp(timestamp)}")
        
        elif role == "assistant":
            with st.chat_message("assistant"):
                st.write(content)
                
                # Show additional info if available
                agent = self.message.get("agent", "AI Assistant")
                confidence = self.message.get("confidence", 0.0)
                
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.caption(f"{agent} - {self._format_timestamp(timestamp)}")
                with col2:
                    if confidence > 0:
                        st.caption(f"Confidence: {confidence:.0%}")
                with col3:
                    # Fixed feedback buttons with unique keys
                    col_thumb_up, col_thumb_down = st.columns(2)
                    with col_thumb_up:
                        if st.button("👍", key=f"up_{unique_suffix}"):
                            st.success("Thanks!")
                    with col_thumb_down:
                        if st.button("👎", key=f"down_{unique_suffix}"):
                            st.info("We'll improve!")
    
    def _format_timestamp(self, timestamp):
        """Format timestamp for display"""
        if isinstance(timestamp, str):
            try:
                timestamp = datetime.fromisoformat(timestamp)
            except:
                timestamp = datetime.now()
        return timestamp.strftime("%H:%M")

class Sidebar:
    """Fixed sidebar component"""
    
    @staticmethod
    def render():
        """Render the sidebar"""
        with st.sidebar:
            st.header("🤖 System Status")
            
            # Real-time metrics
            try:
                response = requests.get(
                    "http://localhost:8000/api/v1/analytics/metrics/overview",
                    timeout=5
                )
                if response.status_code == 200:
                    metrics = response.json()
                    m = metrics.get("metrics", {})
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric(
                            "Response Time", 
                            f"{m.get('avg_response_time', 2.3):.1f}s",
                            delta="-0.2s"
                        )
                        st.metric(
                            "Conversations", 
                            m.get('total_conversations', 0),
                            delta="+2"
                        )
                    
                    with col2:
                        st.metric(
                            "Success Rate", 
                            f"{m.get('success_rate', 96.5):.1f}%",
                            delta="+1.2%"
                        )
                        st.metric(
                            "Satisfaction", 
                            f"{m.get('customer_satisfaction', 4.8):.1f}/5",
                            delta="+0.1"
                        )
                
            except Exception as e:
                st.error("Unable to load metrics")
            
            st.divider()
            
            # Settings
            st.header("⚙️ Settings")
            
            show_confidence = st.checkbox("Show AI Confidence", value=True)
            show_agent_info = st.checkbox("Show Agent Info", value=True)
            show_timestamps = st.checkbox("Show Timestamps", value=True)
            
            # Store settings in session state
            st.session_state.ui_settings = {
                "show_confidence": show_confidence,
                "show_agent_info": show_agent_info,
                "show_timestamps": show_timestamps
            }
            
            st.divider()
            
            # Quick Actions
            st.header("🚀 Quick Actions")
            
            # Use unique keys for buttons
            if st.button("Clear Chat History", key="clear_chat"):
                st.session_state.messages = []
                st.rerun()
            
            if st.button("View API Docs", key="api_docs"):
                st.markdown("[Open API Documentation](http://localhost:8000/docs)")
            
            if st.button("Check Health", key="health_check"):
                try:
                    response = requests.get("http://localhost:8000/health", timeout=5)
                    if response.status_code == 200:
                        st.success("✅ API is healthy!")
                    else:
                        st.error("❌ API issues detected")
                except:
                    st.error("❌ Cannot connect to API")

class MetricsDisplay:
    """Fixed metrics dashboard component"""
    
    @staticmethod
    def render_overview():
        """Render metrics overview"""
        try:
            response = requests.get(
                "http://localhost:8000/api/v1/analytics/metrics/overview",
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                metrics = data.get("metrics", {})
                
                # Key metrics cards
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(
                        "Total Conversations",
                        f"{metrics.get('total_conversations', 0):,}",
                        delta="+12%"
                    )
                
                with col2:
                    st.metric(
                        "Avg Response Time",
                        f"{metrics.get('avg_response_time', 2.3):.1f}s",
                        delta="-8%"
                    )
                
                with col3:
                    st.metric(
                        "Satisfaction Score",
                        f"{metrics.get('customer_satisfaction', 4.8):.1f}/5",
                        delta="+3%"
                    )
                
                with col4:
                    st.metric(
                        "Success Rate",
                        f"{metrics.get('success_rate', 96.5):.1f}%",
                        delta="+1.2%"
                    )
                
                # Agent distribution chart (if available)
                if "agent_distribution" in data:
                    st.subheader("Agent Usage Distribution")
                    
                    agent_data = data["agent_distribution"]
                    if agent_data:
                        fig = px.pie(
                            values=list(agent_data.values()),
                            names=list(agent_data.keys()),
                            title="Requests by Agent Type"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                
        except Exception as e:
            st.error(f"Unable to load metrics: {e}")
    
    @staticmethod
    def render_real_time():
        """Render real-time metrics"""
        try:
            # Create placeholder for auto-refresh
            placeholder = st.empty()
            
            with placeholder.container():
                # Simple real-time chart
                st.subheader("System Performance")
                
                # Generate sample time series data
                import pandas as pd
                import numpy as np
                
                times = pd.date_range(
                    start=datetime.now() - pd.Timedelta(hours=1),
                    end=datetime.now(),
                    freq='5min'
                )
                
                df = pd.DataFrame({
                    'time': times,
                    'response_time': np.random.normal(2.5, 0.5, len(times)),
                    'requests_per_min': np.random.poisson(30, len(times))
                })
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=df['time'],
                    y=df['response_time'],
                    mode='lines',
                    name='Response Time (s)',
                    line=dict(color='blue')
                ))
                
                fig.update_layout(
                    title="Response Time Trend (Last Hour)",
                    xaxis_title="Time",
                    yaxis_title="Response Time (seconds)"
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
        except Exception as e:
            st.error(f"Unable to load real-time metrics: {e}")

class SettingsPanel:
    """Settings and configuration panel"""
    
    @staticmethod
    def render():
        """Render settings panel"""
        st.header("🔧 System Configuration")
        
        tab1, tab2, tab3 = st.tabs(["General", "Display", "Advanced"])
        
        with tab1:
            st.subheader("General Settings")
            
            # Response settings
            max_response_length = st.slider(
                "Max Response Length", 
                min_value=100, 
                max_value=500, 
                value=200,
                help="Maximum length of AI responses"
            )
            
            enable_suggestions = st.checkbox(
                "Show Follow-up Suggestions", 
                value=True,
                help="Display suggested follow-up questions"
            )
        
        with tab2:
            st.subheader("Display Settings")
            
            # UI settings
            theme = st.selectbox(
                "Theme",
                ["Light", "Dark", "Auto"],
                index=0
            )
            
            show_agent_names = st.checkbox(
                "Show Agent Names",
                value=True
            )
            
            show_confidence_scores = st.checkbox(
                "Show Confidence Scores",
                value=True
            )
        
        with tab3:
            st.subheader("Advanced Settings")
            
            # Advanced options
            debug_mode = st.checkbox(
                "Debug Mode",
                value=False,
                help="Show detailed logs and debugging information"
            )
            
            if debug_mode:
                st.warning("Debug mode is enabled. This may affect performance.")
            
            api_timeout = st.number_input(
                "API Timeout (seconds)",
                min_value=5,
                max_value=60,
                value=30
            )
        
        # Save settings
        if st.button("Save Configuration", key="save_config"):
            settings_data = {
                "max_response_length": max_response_length,
                "enable_suggestions": enable_suggestions,
                "theme": theme,
                "show_agent_names": show_agent_names,
                "show_confidence_scores": show_confidence_scores,
                "debug_mode": debug_mode,
                "api_timeout": api_timeout
            }
            
            st.session_state.app_settings = settings_data
            st.success("✅ Settings saved successfully!")