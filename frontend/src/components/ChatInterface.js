import React, { useState, useEffect, useRef } from 'react';
import styled from 'styled-components';
import axios from 'axios';
import Message from './Message';
import MessageInput from './MessageInput';

const ChatContainer = styled.div`
  display: flex;
  flex-direction: column;
  height: 100%;
  background-color: white;
`;

const MessagesContainer = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
`;

const WelcomeMessage = styled.div`
  text-align: center;
  color: #7f8c8d;
  font-size: 1.125rem;
  margin-top: 2rem;
  
  h3 {
    margin-bottom: 0.5rem;
    color: #2c3e50;
  }
  
  p {
    margin-bottom: 0.25rem;
  }
`;

const AgentWorkflow = styled.div`
  background-color: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 0.5rem;
  padding: 0.75rem;
  margin-top: 0.5rem;
  font-size: 0.875rem;
`;

const WorkflowTitle = styled.div`
  font-weight: 600;
  color: #495057;
  margin-bottom: 0.5rem;
`;

const WorkflowStep = styled.div`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.25rem;
  
  &:last-child {
    margin-bottom: 0;
  }
`;

const StepAgent = styled.span`
  background-color: #007bff;
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
`;

const StepDecision = styled.span`
  color: #6c757d;
  font-style: italic;
`;

const LoadingMessage = styled.div`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #6c757d;
  font-style: italic;
  padding: 1rem;
`;

const LoadingDots = styled.div`
  display: inline-block;
  
  &::after {
    content: '...';
    animation: dots 1.5s infinite;
  }
  
  @keyframes dots {
    0%, 20% { content: '.'; }
    40% { content: '..'; }
    60%, 100% { content: '...'; }
  }
`;

function ChatInterface({ conversationId, userId, onNewConversation }) {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    if (conversationId) {
      fetchConversationHistory();
    } else {
      setMessages([]);
    }
  }, [conversationId]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const fetchConversationHistory = async () => {
    try {
      const response = await axios.get(`${process.env.REACT_APP_API_URL || '/api'}/conversations/${conversationId}`);
      setMessages(response.data.messages || []);
    } catch (error) {
      console.error('Failed to fetch conversation history:', error);
      setMessages([]);
    }
  };

  const sendMessage = async (messageText) => {
    if (!messageText.trim()) return;

    const userMessage = {
      message: messageText,
      timestamp: new Date().toISOString(),
      user_id: userId,
      conversation_id: conversationId
    };

    // Add user message immediately
    setMessages(prev => [...prev, userMessage]);
    setLoading(true);

    try {
      const response = await axios.post(`${process.env.REACT_APP_API_URL || '/api'}/chat`, {
        message: messageText,
        user_id: userId,
        conversation_id: conversationId
      });

      // Add bot response
      const botMessage = {
        message: response.data.response,
        timestamp: response.data.timestamp,
        user_id: 'bot',
        conversation_id: conversationId,
        agent_workflow: response.data.agent_workflow,
        source_agent_response: response.data.source_agent_response
      };

      setMessages(prev => [...prev, botMessage]);
      
      // Update conversation ID if it was generated
      if (!conversationId && response.data.conversation_id) {
        onNewConversation(response.data.conversation_id);
      }

    } catch (error) {
      console.error('Failed to send message:', error);
      
      // Add error message
      const errorMessage = {
        message: 'Desculpe, ocorreu um erro ao processar sua mensagem. Tente novamente.',
        timestamp: new Date().toISOString(),
        user_id: 'bot',
        conversation_id: conversationId,
        isError: true
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const renderAgentWorkflow = (workflow) => {
    if (!workflow || workflow.length === 0) return null;

    return (
      <AgentWorkflow>
        <WorkflowTitle>Fluxo de Processamento:</WorkflowTitle>
        {workflow.map((step, index) => (
          <WorkflowStep key={index}>
            <StepAgent>{step.agent}</StepAgent>
            {step.decision && (
              <StepDecision>→ {step.decision}</StepDecision>
            )}
          </WorkflowStep>
        ))}
      </AgentWorkflow>
    );
  };

  if (!conversationId) {
    return (
      <ChatContainer>
        <MessagesContainer>
          <WelcomeMessage>
            <h3>🤖 Bem-vindo ao Modular Chatbot!</h3>
            <p>Este é um assistente inteligente que pode ajudar você com:</p>
            <p>📚 <strong>Perguntas sobre Infinitepay</strong> - Documentação e integração</p>
            <p>🧮 <strong>Cálculos matemáticos</strong> - Expressões e problemas</p>
            <p>💬 <strong>Conversas inteligentes</strong> - Respostas personalizadas</p>
            <br />
            <p>Comece uma nova conversa para começar!</p>
          </WelcomeMessage>
        </MessagesContainer>
        <MessageInput onSendMessage={sendMessage} disabled={true} />
      </ChatContainer>
    );
  }

  return (
    <ChatContainer>
      <MessagesContainer>
        {messages.map((message, index) => (
          <div key={index}>
            <Message 
              message={message.message}
              isUser={message.user_id === userId}
              timestamp={message.timestamp}
              isError={message.isError}
            />
            {message.agent_workflow && renderAgentWorkflow(message.agent_workflow)}
          </div>
        ))}
        
        {loading && (
          <LoadingMessage>
            <LoadingDots />
            Processando sua mensagem...
          </LoadingMessage>
        )}
        
        <div ref={messagesEndRef} />
      </MessagesContainer>
      
      <MessageInput onSendMessage={sendMessage} disabled={loading} />
    </ChatContainer>
  );
}

export default ChatInterface;
