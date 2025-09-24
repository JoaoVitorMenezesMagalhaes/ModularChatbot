"""Main application entry point for the modular chatbot."""
import os
from datetime import datetime
from typing import Optional, List
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from models import ChatRequest, ChatResponse, ChatMessage
from services.conversation_service import ConversationService
from services.redis_service import RedisService
from utils.logger import StructuredLogger
from utils.error_handler import error_handler
from middleware.security_middleware import SecurityMiddleware, InputValidationMiddleware
from config import Config

# Initialize FastAPI app
app = FastAPI(
    title="Modular Chatbot with Router",
    description="A modular chatbot that routes messages to specialized agents",
    version="1.0.0"
)

# Add security middleware
app.add_middleware(SecurityMiddleware, rate_limit_per_minute=60)
app.add_middleware(InputValidationMiddleware)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize logger
logger = StructuredLogger("MainApp")

# Initialize services
conversation_service = ConversationService()
redis_service = RedisService()

# Dependency for Redis health check
def get_redis_service() -> RedisService:
    return redis_service

# Error handlers
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return error_handler.handle_http_exception(request, exc)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return error_handler.handle_validation_error(request, exc)

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return error_handler.handle_general_exception(request, exc)

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Modular Chatbot with Router API",
        "version": "1.0.0",
        "available_agents": ["router", "knowledge", "math"],
        "endpoints": {
            "chat": "/chat",
            "health": "/health",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check(redis: RedisService = Depends(get_redis_service)):
    """Health check endpoint."""
    redis_healthy = redis.health_check()
    
    return {
        "status": "healthy" if redis_healthy else "degraded",
        "timestamp": datetime.now(),
        "services": {
            "redis": "healthy" if redis_healthy else "unhealthy",
            "conversation": "active"
        }
    }

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Main chat endpoint that routes messages to appropriate agents."""
    try:
        return conversation_service.process_message(request)
    except Exception as e:
        # Error handling is now managed by the global exception handler
        # This ensures no raw exceptions are exposed to clients
        raise

@app.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    """Get conversation history by ID."""
    try:
        messages = conversation_service.get_conversation_history(conversation_id)
        if messages is None:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        return {
            "conversation_id": conversation_id,
            "messages": messages,
            "message_count": len(messages)
        }
    except HTTPException:
        raise
    except Exception as e:
        # Error handling is now managed by the global exception handler
        raise

@app.get("/conversations/user/{user_id}")
async def get_user_conversations(user_id: str):
    """Get all conversations for a user."""
    try:
        conversation_ids = conversation_service.get_user_conversations(user_id)
        return {
            "user_id": user_id,
            "conversation_ids": conversation_ids,
            "count": len(conversation_ids)
        }
    except Exception as e:
        # Error handling is now managed by the global exception handler
        raise

if __name__ == "__main__":
    import uvicorn
    
    # Check if OpenAI API key is configured
    if not Config.OPENAI_API_KEY:
        logger.log_error(AgentType.KNOWLEDGE, "OpenAI API key not configured. Please set OPENAI_API_KEY environment variable.")
        exit(1)
    
    logger.log_info("Starting Modular Chatbot with Router API...")
    
    uvicorn.run(
        "main:app",
        host=Config.API_HOST,
        port=Config.API_PORT,
        reload=Config.API_DEBUG,
        log_level="info"
    )
