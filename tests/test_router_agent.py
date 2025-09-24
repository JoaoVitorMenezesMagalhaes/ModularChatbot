"""Unit tests for RouterAgent."""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from agents.router_agent import RouterAgent
from models import AgentType, ChatMessage

class TestRouterAgent:
    """Test cases for RouterAgent decision logic."""
    
    @pytest.fixture
    def router_agent(self):
        """Create RouterAgent instance for testing."""
        with patch('agents.router_agent.OpenAI'):
            return RouterAgent()
    
    @pytest.fixture
    def sample_chat_message(self):
        """Create sample chat message for testing."""
        return ChatMessage(
            message="How do I integrate with Infinitepay API?",
            timestamp=datetime.now(),
            user_id="test_user",
            conversation_id="conv_test"
        )
    
    def test_math_expression_detection(self, router_agent):
        """Test detection of mathematical expressions."""
        # Test basic math expressions
        assert router_agent._is_math_expression("How much is 65 x 3.11?") == True
        assert router_agent._is_math_expression("Calculate 70 + 12") == True
        assert router_agent._is_math_expression("(42 * 2) / 6") == True
        assert router_agent._is_math_expression("What is 100 - 25?") == True
        
        # Test non-math expressions
        assert router_agent._is_math_expression("How do I integrate with Infinitepay?") == False
        assert router_agent._is_math_expression("What is the API documentation?") == False
        assert router_agent._is_math_expression("Hello world") == False
    
    def test_knowledge_query_detection(self, router_agent):
        """Test detection of knowledge base queries."""
        # Test knowledge queries
        assert router_agent._is_knowledge_query("How do I integrate with Infinitepay?") == True
        assert router_agent._is_knowledge_query("What is the API documentation?") == True
        assert router_agent._is_knowledge_query("Help me with webhooks") == True
        assert router_agent._is_knowledge_query("Explain authentication") == True
        
        # Test non-knowledge queries
        assert router_agent._is_knowledge_query("65 x 3.11") == False
        assert router_agent._is_knowledge_query("Calculate something") == False
        assert router_agent._is_knowledge_query("Hello") == False
    
    def test_rule_based_decision_math(self, router_agent):
        """Test rule-based decision for math expressions."""
        agent_type, confidence, reasoning = router_agent._rule_based_decision("How much is 65 x 3.11?")
        
        assert agent_type == AgentType.MATH
        assert confidence == 0.8
        assert "Mathematical expression detected" in reasoning
    
    def test_rule_based_decision_knowledge(self, router_agent):
        """Test rule-based decision for knowledge queries."""
        agent_type, confidence, reasoning = router_agent._rule_based_decision("How do I integrate with Infinitepay?")
        
        assert agent_type == AgentType.KNOWLEDGE
        assert confidence == 0.7
        assert "Knowledge query detected" in reasoning
    
    def test_rule_based_decision_default(self, router_agent):
        """Test rule-based decision for ambiguous queries."""
        agent_type, confidence, reasoning = router_agent._rule_based_decision("Hello")
        
        assert agent_type == AgentType.KNOWLEDGE
        assert confidence == 0.5
        assert "Default to knowledge agent" in reasoning
    
    @patch('agents.router_agent.OpenAI')
    def test_llm_decision_success(self, mock_openai, router_agent, sample_chat_message):
        """Test successful LLM decision making."""
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '{"agent": "KNOWLEDGE_AGENT", "confidence": 0.85, "reasoning": "User asked about Infinitepay"}'
        mock_openai.return_value.chat.completions.create.return_value = mock_response
        
        agent_type, confidence, reasoning = router_agent._get_llm_decision("How do I integrate with Infinitepay?")
        
        assert agent_type == AgentType.KNOWLEDGE
        assert confidence == 0.85
        assert "User asked about Infinitepay" in reasoning
    
    @patch('agents.router_agent.OpenAI')
    def test_llm_decision_fallback(self, mock_openai, router_agent):
        """Test LLM decision fallback to rule-based."""
        # Mock OpenAI to raise exception
        mock_openai.return_value.chat.completions.create.side_effect = Exception("API Error")
        
        agent_type, confidence, reasoning = router_agent._rule_based_decision("How much is 65 x 3.11?")
        
        assert agent_type == AgentType.MATH
        assert confidence == 0.8
        assert "Mathematical expression detected" in reasoning
    
    def test_route_message_success(self, router_agent, sample_chat_message):
        """Test successful message routing."""
        with patch.object(router_agent, '_get_llm_decision') as mock_llm:
            mock_llm.return_value = (AgentType.KNOWLEDGE, 0.85, "Test reasoning")
            
            decision = router_agent.route_message(sample_chat_message)
            
            assert decision.agent_type == AgentType.KNOWLEDGE
            assert decision.confidence == 0.85
            assert decision.reasoning == "Test reasoning"
            assert decision.conversation_id == "conv_test"
            assert decision.user_id == "test_user"
    
    def test_route_message_error_handling(self, router_agent, sample_chat_message):
        """Test error handling in message routing."""
        with patch.object(router_agent, '_get_llm_decision') as mock_llm:
            mock_llm.side_effect = Exception("Test error")
            
            decision = router_agent.route_message(sample_chat_message)
            
            # Should return fallback decision
            assert decision.agent_type == AgentType.KNOWLEDGE
            assert decision.confidence == 0.1
            assert "Error occurred" in decision.reasoning
    
    def test_math_keywords_detection(self, router_agent):
        """Test detection of math-related keywords."""
        math_messages = [
            "calculate 2 + 2",
            "compute the result",
            "solve this equation",
            "mathematical problem",
            "addition of numbers",
            "multiplication table",
            "division by zero",
            "equals 42"
        ]
        
        for message in math_messages:
            assert router_agent._is_math_expression(message), f"Failed to detect math in: {message}"
    
    def test_knowledge_keywords_detection(self, router_agent):
        """Test detection of knowledge-related keywords."""
        knowledge_messages = [
            "help me understand",
            "how does this work",
            "what is the documentation",
            "explain the process",
            "guide me through",
            "tutorial for beginners",
            "support for integration",
            "api reference"
        ]
        
        for message in knowledge_messages:
            assert router_agent._is_knowledge_query(message), f"Failed to detect knowledge query in: {message}"
