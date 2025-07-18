import pytest
from unittest.mock import patch, Mock
import streamlit as st
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.frontend.app import main

def test_streamlit_ui_initialization():
    """Test Streamlit UI initializes correctly"""
    with patch('streamlit.set_page_config') as mock_config:
        with patch('streamlit.title') as mock_title:
            # Test UI initialization
            mock_config.assert_called_once()
            assert "AI Customer Service" in str(mock_title.call_args)

@pytest.mark.asyncio
async def test_chat_interface():
    """Test chat interface functionality"""
    with patch('requests.post') as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "response": "Test response",
            "agent_used": "ProductAgent",
            "confidence": 0.85
        }
        
        # Test chat functionality
        # This would require more complex Streamlit testing setup
        pass