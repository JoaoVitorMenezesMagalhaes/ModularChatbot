import React from 'react';
import styled from 'styled-components';

const HeaderContainer = styled.header`
  background-color: #34495e;
  color: white;
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
`;

const Title = styled.h1`
  font-size: 1.5rem;
  font-weight: 600;
  margin: 0;
`;

const UserInfo = styled.div`
  display: flex;
  align-items: center;
  gap: 1rem;
`;

const UserId = styled.span`
  background-color: #3498db;
  padding: 0.25rem 0.75rem;
  border-radius: 1rem;
  font-size: 0.875rem;
  font-weight: 500;
`;

const Status = styled.div`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
`;

const StatusDot = styled.div`
  width: 8px;
  height: 8px;
  background-color: #2ecc71;
  border-radius: 50%;
  animation: pulse 2s infinite;
  
  @keyframes pulse {
    0% { opacity: 1; }
    50% { opacity: 0.5; }
    100% { opacity: 1; }
  }
`;

function Header({ userId }) {
  return (
    <HeaderContainer>
      <Title>🤖 Modular Chatbot</Title>
      <UserInfo>
        <Status>
          <StatusDot />
          Online
        </Status>
        <UserId>ID: {userId}</UserId>
      </UserInfo>
    </HeaderContainer>
  );
}

export default Header;
