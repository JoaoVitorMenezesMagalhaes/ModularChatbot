"""Redis service for conversation management and logging."""
import json
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
import redis
from redis.exceptions import RedisError
from models import ChatMessage, ConversationHistory, AgentLog
from config import Config
from utils.logger import StructuredLogger

class RedisService:
    """Redis service for managing conversations and logs."""
    
    def __init__(self):
        self.logger = StructuredLogger("RedisService")
        self.redis_client = self._create_redis_client()
    
    def _create_redis_client(self) -> redis.Redis:
        """Create Redis client with proper configuration."""
        try:
            client = redis.Redis(
                host=Config.REDIS_HOST,
                port=Config.REDIS_PORT,
                db=Config.REDIS_DB,
                password=Config.REDIS_PASSWORD,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True
            )
            
            # Test connection
            client.ping()
            self.logger.log_info("Redis connection established successfully")
            return client
            
        except RedisError as e:
            self.logger.log_error(None, f"Redis connection failed: {str(e)}")
            raise
    
    def generate_conversation_id(self) -> str:
        """Generate a unique conversation ID."""
        return f"conv-{uuid.uuid4().hex[:8]}"
    
    def save_message(self, conversation_id: str, message: ChatMessage) -> bool:
        """Save a message to conversation history."""
        try:
            key = f"conversation:{conversation_id}"
            
            # Get existing conversation or create new one
            conversation_data = self.redis_client.hget(key, "data")
            if conversation_data:
                conversation = ConversationHistory.parse_raw(conversation_data)
            else:
                conversation = ConversationHistory(
                    conversation_id=conversation_id,
                    user_id=message.user_id or "anonymous",
                    messages=[],
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
            
            # Add new message
            conversation.messages.append(message)
            conversation.updated_at = datetime.now()
            
            # Save back to Redis
            self.redis_client.hset(
                key,
                mapping={
                    "data": conversation.json(),
                    "updated_at": conversation.updated_at.isoformat()
                }
            )
            
            # Set expiration (30 days)
            self.redis_client.expire(key, 30 * 24 * 60 * 60)
            
            return True
            
        except Exception as e:
            self.logger.log_error(None, f"Failed to save message: {str(e)}")
            return False
    
    def get_conversation_history(self, conversation_id: str) -> Optional[ConversationHistory]:
        """Get conversation history by ID."""
        try:
            key = f"conversation:{conversation_id}"
            conversation_data = self.redis_client.hget(key, "data")
            
            if conversation_data:
                return ConversationHistory.parse_raw(conversation_data)
            return None
            
        except Exception as e:
            self.logger.log_error(None, f"Failed to get conversation history: {str(e)}")
            return None
    
    def get_user_conversations(self, user_id: str) -> List[str]:
        """Get all conversation IDs for a user."""
        try:
            pattern = f"conversation:*"
            keys = self.redis_client.keys(pattern)
            conversation_ids = []
            
            for key in keys:
                conversation_data = self.redis_client.hget(key, "data")
                if conversation_data:
                    conversation = ConversationHistory.parse_raw(conversation_data)
                    if conversation.user_id == user_id:
                        conversation_ids.append(conversation.conversation_id)
            
            return conversation_ids
            
        except Exception as e:
            self.logger.log_error(None, f"Failed to get user conversations: {str(e)}")
            return []
    
    def save_agent_log(self, log: AgentLog) -> bool:
        """Save agent log to Redis."""
        try:
            key = f"logs:{log.agent_type.value}:{datetime.now().strftime('%Y-%m-%d')}"
            log_data = log.json()
            
            # Add to list with timestamp
            self.redis_client.lpush(key, log_data)
            
            # Keep only last 1000 logs per agent per day
            self.redis_client.ltrim(key, 0, 999)
            
            # Set expiration (7 days)
            self.redis_client.expire(key, 7 * 24 * 60 * 60)
            
            return True
            
        except Exception as e:
            self.logger.log_error(None, f"Failed to save agent log: {str(e)}")
            return False
    
    def get_agent_logs(self, agent_type: str, date: Optional[str] = None) -> List[AgentLog]:
        """Get agent logs for a specific date."""
        try:
            if not date:
                date = datetime.now().strftime('%Y-%m-%d')
            
            key = f"logs:{agent_type}:{date}"
            logs_data = self.redis_client.lrange(key, 0, -1)
            
            logs = []
            for log_data in logs_data:
                try:
                    log = AgentLog.parse_raw(log_data)
                    logs.append(log)
                except Exception:
                    continue  # Skip invalid logs
            
            return logs
            
        except Exception as e:
            self.logger.log_error(None, f"Failed to get agent logs: {str(e)}")
            return []
    
    def health_check(self) -> bool:
        """Check Redis connection health."""
        try:
            self.redis_client.ping()
            return True
        except Exception:
            return False
