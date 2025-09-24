"""Conversation service for managing chat workflows."""
import time
from datetime import datetime
from typing import Optional, List
from models import (
    ChatRequest, ChatResponse, ChatMessage, AgentWorkflowStep,
    AgentType, RouterDecision, KnowledgeResponse, MathResponse
)
from agents.router_agent import RouterAgent
from agents.knowledge_agent import KnowledgeAgent
from agents.math_agent import MathAgent
from services.redis_service import RedisService
from utils.logger import StructuredLogger
from utils.error_handler import error_handler

class ConversationService:
    """Service for managing conversation workflows and agent coordination."""
    
    def __init__(self):
        self.redis_service = RedisService()
        self.router_agent = RouterAgent()
        self.knowledge_agent = KnowledgeAgent()
        self.math_agent = MathAgent()
        self.logger = StructuredLogger("ConversationService")
    
    def process_message(self, request: ChatRequest) -> ChatResponse:
        """Process a chat message through the complete workflow."""
        start_time = time.time()
        workflow_steps = []
        
        try:
            # Generate conversation ID if not provided
            conversation_id = request.conversation_id or self.redis_service.generate_conversation_id()
            
            # Create chat message
            chat_message = ChatMessage(
                message=request.message,
                timestamp=datetime.now(),
                user_id=request.user_id,
                conversation_id=conversation_id
            )
            
            # Save user message to conversation history
            self.redis_service.save_message(conversation_id, chat_message)
            
            # Step 1: Router Agent Decision
            router_start = time.time()
            decision = self.router_agent.route_message(chat_message)
            router_time = time.time() - router_start
            
            workflow_steps.append(AgentWorkflowStep(
                agent="RouterAgent",
                decision=decision.agent_type.value,
                execution_time=router_time,
                metadata={
                    "confidence": decision.confidence,
                    "reasoning": decision.reasoning
                }
            ))
            
            # Step 2: Execute with selected agent
            agent_start = time.time()
            source_response = ""
            
            if decision.agent_type == AgentType.KNOWLEDGE:
                response = self.knowledge_agent.answer_question(chat_message)
                source_response = response.answer
                
                workflow_steps.append(AgentWorkflowStep(
                    agent="KnowledgeAgent",
                    execution_time=response.execution_time,
                    metadata={
                        "sources": response.sources,
                        "sources_count": len(response.sources)
                    }
                ))
                
            elif decision.agent_type == AgentType.MATH:
                response = self.math_agent.solve_math_problem(chat_message)
                source_response = response.answer
                
                workflow_steps.append(AgentWorkflowStep(
                    agent="MathAgent",
                    execution_time=response.execution_time,
                    metadata={
                        "expression": response.expression,
                        "result": response.result
                    }
                ))
            
            else:
                raise ValueError(f"Unknown agent type: {decision.agent_type}")
            
            agent_time = time.time() - agent_start
            
            # Add personality to the response
            final_response = self._add_personality(source_response, decision.agent_type)
            
            # Create response message
            response_message = ChatMessage(
                message=final_response,
                timestamp=datetime.now(),
                user_id=request.user_id,
                conversation_id=conversation_id
            )
            
            # Save response to conversation history
            self.redis_service.save_message(conversation_id, response_message)
            
            # Create final response
            chat_response = ChatResponse(
                response=final_response,
                source_agent_response=source_response,
                agent_workflow=workflow_steps,
                conversation_id=conversation_id,
                timestamp=datetime.now(),
                user_id=request.user_id
            )
            
            # Log the complete workflow with full observability
            total_execution_time = time.time() - start_time
            self.logger.log_info(
                f"Message processed successfully",
                agent_type=decision.agent_type,
                conversation_id=conversation_id,
                user_id=request.user_id,
                execution_time=total_execution_time,
                metadata={
                    "agent_type": decision.agent_type.value,
                    "total_execution_time": total_execution_time,
                    "workflow_steps": len(workflow_steps),
                    "routing_confidence": decision.confidence
                }
            )
            
            return chat_response
            
        except Exception as e:
            # Log error with full details for debugging
            error_id = error_handler.log_error_safely(e, {
                "conversation_id": request.conversation_id,
                "user_id": request.user_id,
                "message_length": len(request.message) if request.message else 0
            })
            
            # Return safe error response
            return ChatResponse(
                response="Desculpe, ocorreu um erro interno. Tente novamente em alguns instantes.",
                source_agent_response="Error occurred during processing",
                agent_workflow=workflow_steps,
                conversation_id=request.conversation_id or "error",
                timestamp=datetime.now(),
                user_id=request.user_id
            )
    
    def _add_personality(self, response: str, agent_type: AgentType) -> str:
        """Add personality to the agent response."""
        if agent_type == AgentType.KNOWLEDGE:
            # Add friendly, helpful personality for knowledge responses
            if not response.startswith("Olá") and not response.startswith("Oi"):
                response = f"Olá! {response.lower()}"
            
            # Add helpful closing
            if not response.endswith(".") and not response.endswith("!"):
                response += "."
            
            response += " Se precisar de mais alguma coisa, estou aqui para ajudar! 😊"
            
        elif agent_type == AgentType.MATH:
            # Add enthusiastic personality for math responses
            if "resultado" not in response.lower() and "resposta" not in response.lower():
                response = f"Perfeito! Aqui está a solução:\n\n{response}"
            
            response += "\n\nMatemática é incrível, não é? 🧮✨"
        
        return response
    
    def get_conversation_history(self, conversation_id: str) -> Optional[List[ChatMessage]]:
        """Get conversation history."""
        conversation = self.redis_service.get_conversation_history(conversation_id)
        return conversation.messages if conversation else None
    
    def get_user_conversations(self, user_id: str) -> List[str]:
        """Get all conversation IDs for a user."""
        return self.redis_service.get_user_conversations(user_id)
