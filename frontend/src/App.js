// src/App.js
import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import ProjectsDashboard from './components/ProjectDashboard';
import CreateProject from './components/CreateProject';
import ChatInterface from './components/ChatInterface';

function App() {
  return (
    <Router>
        <Routes>
          <Route path="/" element={<ProjectsDashboard />} />
          <Route path="/create" element={<CreateProject />} />
          <Route path="/chat-interface/:id" element={<ChatInterface />} /> 
          {/* <Route path="/my-chats" element={<MyChats />} />  */}
        </Routes>
    </Router>
  );
}

export default App;
