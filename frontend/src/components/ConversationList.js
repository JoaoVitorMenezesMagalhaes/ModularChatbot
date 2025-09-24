import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { v4 as uuidv4 } from 'uuid';
import axios from 'axios';

const ConversationListContainer = styled.div`
  padding: 1rem;
`;

const Title = styled.h2`
  font-size: 1.25rem;
  margin-bottom: 1rem;
  color: #ecf0f1;
`;

const NewConversationButton = styled.button`
  width: 100%;
  padding: 0.75rem;
  background-color: #3498db;
  color: white;
  border: none;
  border-radius: 0.5rem;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  margin-bottom: 1rem;
  transition: background-color 0.2s;

  &:hover {
    background-color: #2980b9;
  }
`;

const ConversationItem = styled.div`
  padding: 0.75rem;
  margin-bottom: 0.5rem;
  background-color: ${props => props.active ? '#3498db' : '#34495e'};
  border-radius: 0.5rem;
  cursor: pointer;
  transition: background-color 0.2s;
  border-left: 3px solid ${props => props.active ? '#2ecc71' : 'transparent'};

  &:hover {
    background-color: ${props => props.active ? '#3498db' : '#2c3e50'};
  }
`;

const ConversationId = styled.div`
  font-size: 0.875rem;
  font-weight: 500;
  color: #ecf0f1;
  margin-bottom: 0.25rem;
`;

const ConversationPreview = styled.div`
  font-size: 0.75rem;
  color: #bdc3c7;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
`;

const EmptyState = styled.div`
  text-align: center;
  color: #7f8c8d;
  font-size: 0.875rem;
  margin-top: 2rem;
`;

function ConversationList({ userId, currentConversationId, onSelectConversation }) {
  const [conversations, setConversations] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchConversations();
  }, [userId]);

  const fetchConversations = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${process.env.REACT_APP_API_URL || '/api'}/conversations/user/${userId}`);
      setConversations(response.data.conversation_ids || []);
    } catch (error) {
      console.error('Failed to fetch conversations:', error);
      setConversations([]);
    } finally {
      setLoading(false);
    }
  };

  const createNewConversation = () => {
    const newConversationId = `conv-${uuidv4().substr(0, 8)}`;
    onSelectConversation(newConversationId);
  };

  const handleConversationSelect = (conversationId) => {
    onSelectConversation(conversationId);
  };

  if (loading) {
    return (
      <ConversationListContainer>
        <Title>Conversas</Title>
        <EmptyState>Carregando...</EmptyState>
      </ConversationListContainer>
    );
  }

  return (
    <ConversationListContainer>
      <Title>Conversas</Title>
      <NewConversationButton onClick={createNewConversation}>
        + Nova Conversa
      </NewConversationButton>
      
      {conversations.length === 0 ? (
        <EmptyState>
          Nenhuma conversa encontrada.<br />
          Comece uma nova conversa!
        </EmptyState>
      ) : (
        conversations.map((conversationId) => (
          <ConversationItem
            key={conversationId}
            active={conversationId === currentConversationId}
            onClick={() => handleConversationSelect(conversationId)}
          >
            <ConversationId>{conversationId}</ConversationId>
            <ConversationPreview>
              Clique para abrir esta conversa
            </ConversationPreview>
          </ConversationItem>
        ))
      )}
    </ConversationListContainer>
  );
}

export default ConversationList;
