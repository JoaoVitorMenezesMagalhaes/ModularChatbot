"""Data models for the modular chatbot."""
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum

class AgentType(str, Enum):
    """Available agent types."""
    KNOWLEDGE = "knowledge"
    MATH = "math"

class LogLevel(str, Enum):
    """Log levels."""
    INFO = "info"
    DEBUG = "debug"
    WARNING = "warning"
    ERROR = "error"

class RouterDecision(BaseModel):
    """Router agent decision structure."""
    agent_type: AgentType
    confidence: float
    reasoning: str
    timestamp: datetime
    user_message: str

class KnowledgeResponse(BaseModel):
    """Knowledge agent response structure."""
    answer: str
    sources: list[str]
    execution_time: float
    timestamp: datetime
    user_message: str

class MathResponse(BaseModel):
    """Math agent response structure."""
    answer: str
    expression: str
    result: float
    execution_time: float
    timestamp: datetime
    user_message: str

class ChatMessage(BaseModel):
    """Chat message structure."""
    message: str
    timestamp: datetime
    user_id: Optional[str] = None
    conversation_id: Optional[str] = None

class AgentWorkflowStep(BaseModel):
    """Single step in agent workflow."""
    agent: str
    decision: Optional[str] = None
    execution_time: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None

class ChatRequest(BaseModel):
    """Request model for chat messages."""
    message: str
    user_id: Optional[str] = None
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    """Response model for chat messages."""
    response: str
    source_agent_response: str
    agent_workflow: list[AgentWorkflowStep]
    conversation_id: str
    timestamp: datetime
    user_id: Optional[str] = None

class ConversationHistory(BaseModel):
    """Conversation history structure."""
    conversation_id: str
    user_id: str
    messages: list[ChatMessage]
    created_at: datetime
    updated_at: datetime

class AgentLog(BaseModel):
    """Structured log entry."""
    level: LogLevel
    message: str
    agent_type: AgentType
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None
