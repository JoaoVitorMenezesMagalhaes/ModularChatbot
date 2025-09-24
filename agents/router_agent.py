"""Router Agent - decides which agent should handle user messages."""
import time
from typing import Tuple
from openai import OpenAI
from models import AgentType, RouterDecision, ChatMessage
from utils.logger import StructuredLogger
from utils.security import SecurityValidator
from config import Config

class RouterAgent:
    """Router agent that decides which specialized agent should handle user messages."""
    
    def __init__(self):
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.logger = StructuredLogger("RouterAgent")
        self.security_validator = SecurityValidator()
        
        # Keywords that indicate mathematical operations
        self.math_keywords = [
            "calculate", "compute", "solve", "math", "mathematical",
            "addition", "subtraction", "multiplication", "division",
            "plus", "minus", "times", "divided", "equals", "=",
            "sum", "difference", "product", "quotient", "percentage",
            "percent", "%", "+", "-", "*", "/", "(", ")"
        ]
        
        # Keywords that indicate knowledge base queries
        self.knowledge_keywords = [
            "help", "how", "what", "where", "when", "why", "explain",
            "documentation", "guide", "tutorial", "support", "api",
            "infinitepay", "payment", "integration", "webhook",
            "authentication", "token", "credentials"
        ]
    
    def _is_math_expression(self, message: str) -> bool:
        """Check if the message contains mathematical expressions."""
        message_lower = message.lower()
        
        # Check for mathematical operators
        has_operators = any(op in message for op in ["+", "-", "*", "/", "=", "(", ")"])
        
        # Check for math keywords
        has_math_keywords = any(keyword in message_lower for keyword in self.math_keywords)
        
        # Check for numbers
        has_numbers = any(char.isdigit() for char in message)
        
        return (has_operators and has_numbers) or (has_math_keywords and has_numbers)
    
    def _is_knowledge_query(self, message: str) -> bool:
        """Check if the message is a knowledge base query."""
        message_lower = message.lower()
        
        # Check for knowledge keywords
        has_knowledge_keywords = any(keyword in message_lower for keyword in self.knowledge_keywords)
        
        # Check for question patterns
        is_question = message.strip().endswith("?")
        
        return has_knowledge_keywords or is_question
    
    def _get_llm_decision(self, message: str) -> Tuple[AgentType, float, str]:
        """Use LLM to make routing decision with confidence score."""
        try:
            # Create secure prompt
            system_prompt = """
            You are a routing agent that decides which specialized agent should handle user messages.
            
            Available agents:
            1. MATH_AGENT: For mathematical calculations, expressions, and arithmetic operations
            2. KNOWLEDGE_AGENT: For questions about Infinitepay API, documentation, and general help
            
            Analyze the user message and respond with JSON format:
            {
                "agent": "MATH_AGENT" or "KNOWLEDGE_AGENT",
                "confidence": 0.0 to 1.0,
                "reasoning": "Brief explanation of why this agent was chosen"
            }
            """
            
            prompt = self.security_validator.create_safe_prompt(message, system_prompt)
            
            response = self.client.chat.completions.create(
                model=Config.ROUTER_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=200
            )
            
            # Parse LLM response
            import json
            result = json.loads(response.choices[0].message.content.strip())
            
            agent_type = AgentType.MATH if result["agent"] == "MATH_AGENT" else AgentType.KNOWLEDGE
            confidence = float(result["confidence"])
            reasoning = result["reasoning"]
            
            return agent_type, confidence, reasoning
            
        except Exception as e:
            self.logger.log_error(AgentType.KNOWLEDGE, f"LLM decision failed: {str(e)}")
            # Fallback to rule-based decision
            return self._rule_based_decision(message)
    
    def _rule_based_decision(self, message: str) -> Tuple[AgentType, float, str]:
        """Fallback rule-based decision making."""
        if self._is_math_expression(message):
            return AgentType.MATH, 0.8, "Mathematical expression detected"
        elif self._is_knowledge_query(message):
            return AgentType.KNOWLEDGE, 0.7, "Knowledge query detected"
        else:
            # Default to knowledge agent for general queries
            return AgentType.KNOWLEDGE, 0.5, "Default to knowledge agent for general queries"
    
    def route_message(self, chat_message: ChatMessage) -> RouterDecision:
        """Route user message to appropriate agent."""
        start_time = time.time()
        
        try:
            # Get routing decision
            agent_type, confidence, reasoning = self._get_llm_decision(chat_message.message)
            
            # Create decision object
            decision = RouterDecision(
                agent_type=agent_type,
                confidence=confidence,
                reasoning=reasoning,
                timestamp=chat_message.timestamp,
                user_message=chat_message.message
            )
            
            # Log the decision with full observability
            execution_time = time.time() - start_time
            self.logger.log_agent_decision(
                agent_type=agent_type,
                confidence=confidence,
                reasoning=reasoning,
                user_message=chat_message.message,
                conversation_id=chat_message.conversation_id,
                user_id=chat_message.user_id,
                execution_time=execution_time,
                decision=agent_type.value,
                metadata={"routing_method": "llm"}
            )
            
            return decision
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.log_error(
                AgentType.KNOWLEDGE, 
                f"Routing failed: {str(e)}",
                conversation_id=chat_message.conversation_id,
                user_id=chat_message.user_id,
                execution_time=execution_time,
                metadata={"error_type": "routing_failure"}
            )
            
            # Return fallback decision
            return RouterDecision(
                agent_type=AgentType.KNOWLEDGE,
                confidence=0.1,
                reasoning="Error occurred, defaulting to knowledge agent",
                timestamp=chat_message.timestamp,
                user_message=chat_message.message
            )
