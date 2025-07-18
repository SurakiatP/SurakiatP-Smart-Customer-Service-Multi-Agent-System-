"""
External API Integrations

Handles integration with third-party services and APIs.
"""

import httpx
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.core.logger import get_logger
from app.core.exceptions import CustomerServiceAIException

logger = get_logger(__name__)

class ExternalAPIClient:
    """Client for external API integrations"""
    
    def __init__(self):
        self.timeout = httpx.Timeout(30.0)
        self.base_headers = {
            "User-Agent": "CustomerServiceAI/1.0",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
    
    async def get_order_details(self, order_id: str) -> Optional[Dict[str, Any]]:
        """Get order details from e-commerce system"""
        # Mock implementation - replace with actual API
        
        mock_orders = {
            "ORD001": {
                "order_id": "ORD001",
                "customer_email": "customer@example.com",
                "total_amount": 99.99,
                "status": "completed",
                "order_date": "2024-01-15T10:30:00Z",
                "items": [
                    {
                        "product_id": "prod_001",
                        "name": "Premium Plan",
                        "quantity": 1,
                        "price": 99.99
                    }
                ],
                "refund_eligible": True,
                "refund_deadline": "2024-01-29T10:30:00Z"
            },
            "ORD002": {
                "order_id": "ORD002",
                "customer_email": "user@test.com",
                "total_amount": 49.99,
                "status": "pending",
                "order_date": "2024-01-20T14:15:00Z",
                "items": [
                    {
                        "product_id": "prod_002",
                        "name": "Standard Plan",
                        "quantity": 1,
                        "price": 49.99
                    }
                ],
                "refund_eligible": False,
                "refund_deadline": None
            }
        }
        
        return mock_orders.get(order_id)
    
    async def process_refund(self, order_id: str, amount: float, reason: str) -> Dict[str, Any]:
        """Process refund through payment system"""
        try:
            # Mock refund processing
            logger.info(f"Processing refund for order {order_id}: ${amount}")
            
            # Simulate API delay
            await asyncio.sleep(2)
            
            # Mock response
            refund_data = {
                "refund_id": f"REF_{order_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "order_id": order_id,
                "amount": amount,
                "reason": reason,
                "status": "processed",
                "processed_at": datetime.now().isoformat(),
                "estimated_completion": "3-5 business days",
                "reference_number": f"REF{datetime.now().strftime('%Y%m%d%H%M%S')}"
            }
            
            return refund_data
            
        except Exception as e:
            logger.error(f"Refund processing failed: {e}")
            raise CustomerServiceAIException(f"Failed to process refund: {e}")
    
    async def get_inventory_status(self, product_id: str) -> Dict[str, Any]:
        """Get product inventory status"""
        # Mock inventory data
        inventory_data = {
            "prod_001": {
                "product_id": "prod_001",
                "name": "Premium Plan",
                "available": True,
                "stock_level": "unlimited",  # Digital product
                "price": 99.99,
                "discount": None,
                "last_updated": datetime.now().isoformat()
            },
            "prod_002": {
                "product_id": "prod_002", 
                "name": "Standard Plan",
                "available": True,
                "stock_level": "unlimited",
                "price": 49.99,
                "discount": 10,  # 10% discount
                "last_updated": datetime.now().isoformat()
            },
            "prod_003": {
                "product_id": "prod_003",
                "name": "Basic Plan",
                "available": True,
                "stock_level": "unlimited",
                "price": 19.99,
                "discount": None,
                "last_updated": datetime.now().isoformat()
            }
        }
        
        return inventory_data.get(product_id, {
            "product_id": product_id,
            "available": False,
            "stock_level": "out_of_stock",
            "error": "Product not found"
        })
    
    async def send_notification(self, user_id: str, message: str, channel: str = "email") -> bool:
        """Send notification to user"""
        try:
            logger.info(f"Sending {channel} notification to {user_id}: {message[:50]}...")
            
            # Mock notification sending
            await asyncio.sleep(1)
            
            notification_data = {
                "user_id": user_id,
                "message": message,
                "channel": channel,
                "sent_at": datetime.now().isoformat(),
                "status": "sent"
            }
            
            # In production, integrate with email service, SMS, etc.
            return True
            
        except Exception as e:
            logger.error(f"Notification sending failed: {e}")
            return False
    
    async def validate_customer(self, email: str) -> Dict[str, Any]:
        """Validate customer information"""
        # Mock customer validation
        mock_customers = {
            "customer@example.com": {
                "customer_id": "CUST001",
                "email": "customer@example.com",
                "name": "John Doe",
                "status": "active",
                "tier": "premium",
                "join_date": "2023-06-15T00:00:00Z",
                "total_orders": 5,
                "lifetime_value": 499.95
            },
            "user@test.com": {
                "customer_id": "CUST002",
                "email": "user@test.com", 
                "name": "Jane Smith",
                "status": "active",
                "tier": "standard",
                "join_date": "2023-12-01T00:00:00Z",
                "total_orders": 2,
                "lifetime_value": 99.98
            }
        }
        
        return mock_customers.get(email, {
            "error": "Customer not found",
            "email": email,
            "status": "unknown"
        })
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get external system status"""
        # Mock system status check
        systems_status = {
            "payment_gateway": {
                "status": "operational",
                "response_time": 150,
                "last_check": datetime.now().isoformat()
            },
            "inventory_system": {
                "status": "operational", 
                "response_time": 89,
                "last_check": datetime.now().isoformat()
            },
            "email_service": {
                "status": "operational",
                "response_time": 234,
                "last_check": datetime.now().isoformat()
            },
            "crm_system": {
                "status": "degraded",
                "response_time": 1200,
                "last_check": datetime.now().isoformat(),
                "issues": ["High response times"]
            }
        }
        
        return {
            "overall_status": "operational",
            "systems": systems_status,
            "last_updated": datetime.now().isoformat()
        }