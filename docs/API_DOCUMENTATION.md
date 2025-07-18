# API Documentation

> **Smart Customer Service AI API Reference**

## **Base URL**
```
Development: http://localhost:8000
Production: https://your-domain.com
```

## **Authentication**
Currently uses session-based authentication. API keys planned for production.

---

## **Chat Endpoints**

### **POST /api/v1/chat**
Send a message to the AI customer service system.

#### **Request**
```http
POST /api/v1/chat
Content-Type: application/json

{
  "message": "What's the price of premium plan?",
  "user_id": "user123",
  "conversation_id": "optional-conversation-id"
}
```

#### **Response**
```json
{
  "response": "Our Premium plan costs $99/month and includes 24/7 priority support, advanced analytics dashboard, custom integrations, and a dedicated account manager.",
  "agent_used": "ProductAgent",
  "confidence": 0.92,
  "response_time": 2.3,
  "conversation_id": "conv_abc123",
  "suggestions": [
    "Compare with other products",
    "Check current promotions",
    "View product reviews"
  ]
}
```

#### **Parameters**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `message` | string | ✅ | User's message (1-1000 chars) |
| `user_id` | string | ✅ | Unique user identifier |
| `conversation_id` | string | ❌ | Continue existing conversation |

#### **Response Fields**
| Field | Type | Description |
|-------|------|-------------|
| `response` | string | AI-generated response |
| `agent_used` | string | Which agent handled the request |
| `confidence` | float | AI confidence score (0-1) |
| `response_time` | float | Processing time in seconds |
| `conversation_id` | string | Conversation identifier |
| `suggestions` | array | Follow-up suggestions |

---

### **GET /api/v1/chat/history/{user_id}**
Retrieve conversation history for a user.

#### **Request**
```http
GET /api/v1/chat/history/user123?limit=10
```

#### **Response**
```json
{
  "history": [
    {
      "id": "msg_001",
      "content": "Hello, I need help with pricing",
      "type": "user",
      "timestamp": "2024-01-15T10:30:00Z",
      "conversation_id": "conv_abc123"
    },
    {
      "id": "msg_002", 
      "content": "I'd be happy to help with pricing information...",
      "type": "assistant",
      "timestamp": "2024-01-15T10:30:15Z",
      "agent_used": "ProductAgent",
      "confidence": 0.88
    }
  ],
  "total_messages": 24,
  "conversation_count": 3
}
```

#### **Query Parameters**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | integer | 10 | Max messages to return |
| `conversation_id` | string | - | Filter by specific conversation |

---

## **Health & Monitoring**

### **GET /health**
Basic health check.

#### **Response**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "service": "Customer Service AI",
  "version": "1.0.0"
}
```

### **GET /health/detailed**
Comprehensive system health.

#### **Response**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "services": {
    "redis": "connected",
    "chromadb": "connected",
    "huggingface": "available"
  },
  "uptime_seconds": 86400
}
```

---

## **Analytics Endpoints**

### **GET /api/v1/analytics/metrics/overview**
System performance overview.

#### **Response**
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "metrics": {
    "total_conversations": 1247,
    "avg_response_time": 2.3,
    "customer_satisfaction": 4.8,
    "first_contact_resolution": 85.2,
    "cost_savings_monthly": 4167
  },
  "agent_distribution": {
    "ProductAgent": 45.2,
    "TechnicalAgent": 32.1,
    "RefundAgent": 18.5,
    "GeneralAgent": 4.2
  }
}
```

### **GET /api/v1/analytics/metrics/real-time**
Real-time system metrics.

#### **Response**
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "current_metrics": {
    "active_conversations": 15,
    "avg_response_time_last_hour": 2.1,
    "requests_per_minute": 25,
    "success_rate": 97.8
  },
  "system_health": {
    "api_latency": 120,
    "cache_hit_rate": 82.5,
    "database_connections": 12
  }
}
```

### **POST /api/v1/analytics/feedback**
Submit user feedback.

#### **Request**
```json
{
  "conversation_id": "conv_abc123",
  "rating": 5,
  "user_id": "user123",
  "comment": "Great help with my question!",
  "agent_used": "ProductAgent"
}
```

#### **Response**
```json
{
  "status": "success",
  "message": "Feedback recorded successfully",
  "feedback_id": "fb_abc123"
}
```

---

## **Error Responses**

### **Standard Error Format**
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Message cannot be empty",
    "details": {
      "field": "message",
      "provided": "",
      "expected": "1-1000 characters"
    }
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### **Common Error Codes**
| Code | Status | Description |
|------|--------|-------------|
| `VALIDATION_ERROR` | 422 | Invalid request data |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |
| `AGENT_UNAVAILABLE` | 503 | AI service temporarily unavailable |
| `INTERNAL_ERROR` | 500 | Server error |

---

## **Rate Limits**
- **Default**: 60 requests per minute per user
- **Burst**: Up to 100 requests in 10-second window
- **Headers**: `X-RateLimit-Remaining`, `X-RateLimit-Reset`

## **SDK Examples**

### **Python**
```python
import httpx

async def chat_with_ai(message: str, user_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/v1/chat",
            json={
                "message": message,
                "user_id": user_id
            }
        )
        return response.json()

# Usage
result = await chat_with_ai("What's the price of premium plan?", "user123")
print(result["response"])
```

### **JavaScript**
```javascript
async function chatWithAI(message, userId) {
  const response = await fetch('http://localhost:8000/api/v1/chat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      message: message,
      user_id: userId
    })
  });
  
  return await response.json();
}

// Usage
const result = await chatWithAI("What's the price of premium plan?", "user123");
console.log(result.response);
```

### **cURL**
```bash
# Send chat message
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is the price of premium plan?",
    "user_id": "user123"
  }'

# Get conversation history
curl "http://localhost:8000/api/v1/chat/history/user123?limit=5"

# Check system health
curl "http://localhost:8000/health"
```

---

## **Additional Resources**

- **Interactive Docs**: `http://localhost:8000/docs` (Swagger UI)
- **OpenAPI Schema**: `http://localhost:8000/openapi.json`
- **Health Dashboard**: `http://localhost:8501` (Streamlit UI)
