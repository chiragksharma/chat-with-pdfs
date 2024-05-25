import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import apiClient from '../api/apiClient';
import ChatList from './ChatList';
import PdfViewer from './pdfViewer';
import ChatBox from './ChatBox';

const ChatInterface = () => {


  return (
      <div className="flex h-screen">
        <ChatList />
        <PdfViewer />
        <ChatBox />
    </div>
  );
};

export default ChatInterface;