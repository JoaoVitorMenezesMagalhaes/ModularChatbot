import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import styled from 'styled-components';
import ChatInterface from './components/ChatInterface';
import ConversationList from './components/ConversationList';
import Header from './components/Header';

const AppContainer = styled.div`
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: #f5f5f5;
`;

const MainContent = styled.div`
  display: flex;
  flex: 1;
  overflow: hidden;
`;

const Sidebar = styled.div`
  width: 300px;
  background-color: #2c3e50;
  color: white;
  overflow-y: auto;
  border-right: 1px solid #34495e;
`;

const ChatArea = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
`;

function App() {
  const [currentConversationId, setCurrentConversationId] = useState(null);
  const [userId] = useState('user-' + Math.random().toString(36).substr(2, 9));

  return (
    <Router>
      <AppContainer>
        <Header userId={userId} />
        <MainContent>
          <Sidebar>
            <ConversationList 
              userId={userId}
              currentConversationId={currentConversationId}
              onSelectConversation={setCurrentConversationId}
            />
          </Sidebar>
          <ChatArea>
            <ChatInterface 
              conversationId={currentConversationId}
              userId={userId}
              onNewConversation={() => setCurrentConversationId(null)}
            />
          </ChatArea>
        </MainContent>
      </AppContainer>
    </Router>
  );
}

export default App;
