import React from 'react';
import styled from 'styled-components';

const MessageContainer = styled.div`
  display: flex;
  justify-content: ${props => props.isUser ? 'flex-end' : 'flex-start'};
  margin-bottom: 1rem;
`;

const MessageBubble = styled.div`
  max-width: 70%;
  padding: 0.75rem 1rem;
  border-radius: 1rem;
  background-color: ${props => 
    props.isUser 
      ? '#007bff' 
      : props.isError 
        ? '#dc3545' 
        : '#f8f9fa'
  };
  color: ${props => 
    props.isUser 
      ? 'white' 
      : props.isError 
        ? 'white' 
        : '#212529'
  };
  border: ${props => 
    props.isUser 
      ? 'none' 
      : props.isError 
        ? 'none' 
        : '1px solid #e9ecef'
  };
  word-wrap: break-word;
  white-space: pre-wrap;
`;

const MessageHeader = styled.div`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
  opacity: 0.8;
`;

const UserIcon = styled.span`
  font-size: 1rem;
`;

const Timestamp = styled.span`
  font-size: 0.75rem;
  opacity: 0.7;
`;

const MessageContent = styled.div`
  line-height: 1.4;
`;

function Message({ message, isUser, timestamp, isError = false }) {
  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('pt-BR', { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  const getUserIcon = () => {
    if (isUser) return '👤';
    if (isError) return '⚠️';
    return '🤖';
  };

  const getUserLabel = () => {
    if (isUser) return 'Você';
    if (isError) return 'Erro';
    return 'Assistente';
  };

  return (
    <MessageContainer isUser={isUser}>
      <MessageBubble isUser={isUser} isError={isError}>
        <MessageHeader>
          <UserIcon>{getUserIcon()}</UserIcon>
          <span>{getUserLabel()}</span>
          <Timestamp>{formatTimestamp(timestamp)}</Timestamp>
        </MessageHeader>
        <MessageContent>{message}</MessageContent>
      </MessageBubble>
    </MessageContainer>
  );
}

export default Message;
