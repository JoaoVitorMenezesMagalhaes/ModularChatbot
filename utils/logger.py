"""Logging utilities for the modular chatbot."""
import json
import logging
import time
from datetime import datetime
from typing import Dict, Any, Optional
from models import AgentLog, AgentType, LogLevel

class StructuredLogger:
    """Structured logger for agent operations."""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # Create console handler
        handler = logging.StreamHandler()
        handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        
        # Add handler to logger
        if not self.logger.handlers:
            self.logger.addHandler(handler)
    
    def log_agent_decision(self, agent_type: AgentType, confidence: float, 
                          reasoning: str, user_message: str, 
                          conversation_id: Optional[str] = None,
                          user_id: Optional[str] = None,
                          execution_time: Optional[float] = None,
                          decision: Optional[str] = None,
                          metadata: Optional[Dict[str, Any]] = None):
        """Log router agent decision with full observability."""
        log_entry = {
            "timestamp": datetime.now().isoformat() + "Z",
            "level": "INFO",
            "agent": "RouterAgent",
            "conversation_id": conversation_id,
            "user_id": user_id,
            "execution_time": execution_time,
            "decision": decision or agent_type.value,
            "confidence": confidence,
            "reasoning": reasoning,
            "processed_content": user_message[:200] + "..." if len(user_message) > 200 else user_message,
            "metadata": metadata or {}
        }
        
        self.logger.info(json.dumps(log_entry, default=str))
    
    def log_agent_execution(self, agent_type: AgentType, message: str,
                           execution_time: float, 
                           conversation_id: Optional[str] = None,
                           user_id: Optional[str] = None,
                           processed_content: Optional[str] = None,
                           metadata: Optional[Dict[str, Any]] = None):
        """Log agent execution details with full observability."""
        log_entry = {
            "timestamp": datetime.now().isoformat() + "Z",
            "level": "INFO",
            "agent": f"{agent_type.value.title()}Agent",
            "conversation_id": conversation_id,
            "user_id": user_id,
            "execution_time": execution_time,
            "processed_content": processed_content or message[:200] + "..." if len(message) > 200 else message,
            "metadata": metadata or {}
        }
        
        self.logger.info(json.dumps(log_entry, default=str))
    
    def log_error(self, agent_type: AgentType, error: str, 
                  conversation_id: Optional[str] = None,
                  user_id: Optional[str] = None,
                  execution_time: Optional[float] = None,
                  metadata: Optional[Dict[str, Any]] = None):
        """Log error messages with full observability."""
        log_entry = {
            "timestamp": datetime.now().isoformat() + "Z",
            "level": "ERROR",
            "agent": f"{agent_type.value.title()}Agent" if agent_type else "System",
            "conversation_id": conversation_id,
            "user_id": user_id,
            "execution_time": execution_time,
            "error": error,
            "metadata": metadata or {}
        }
        
        self.logger.error(json.dumps(log_entry, default=str))
    
    def log_info(self, message: str, agent_type: Optional[AgentType] = None,
                 conversation_id: Optional[str] = None,
                 user_id: Optional[str] = None,
                 execution_time: Optional[float] = None,
                 metadata: Optional[Dict[str, Any]] = None):
        """Log general information with full observability."""
        log_entry = {
            "timestamp": datetime.now().isoformat() + "Z",
            "level": "INFO",
            "agent": f"{agent_type.value.title()}Agent" if agent_type else "System",
            "conversation_id": conversation_id,
            "user_id": user_id,
            "execution_time": execution_time,
            "message": message,
            "metadata": metadata or {}
        }
        
        self.logger.info(json.dumps(log_entry, default=str))
    
    def log_debug(self, message: str, agent_type: Optional[AgentType] = None,
                  conversation_id: Optional[str] = None,
                  user_id: Optional[str] = None,
                  execution_time: Optional[float] = None,
                  metadata: Optional[Dict[str, Any]] = None):
        """Log debug information with full observability."""
        log_entry = {
            "timestamp": datetime.now().isoformat() + "Z",
            "level": "DEBUG",
            "agent": f"{agent_type.value.title()}Agent" if agent_type else "System",
            "conversation_id": conversation_id,
            "user_id": user_id,
            "execution_time": execution_time,
            "message": message,
            "metadata": metadata or {}
        }
        
        self.logger.debug(json.dumps(log_entry, default=str))
