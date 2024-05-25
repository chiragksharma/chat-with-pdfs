// src/components/ProjectsDashboard.js
import React, { useEffect } from 'react';
import apiClient from '../api/apiClient';
import {useStore} from '../store/useStore';
import MyChats from './MyChats';
import FileDrop from './FileDrop';

const ProjectsDashboard = () => {
  // const setProjects = useStore((state) => state.setProjects);

  // useEffect(() => {
  //   apiClient.get('/projects')
  //     .then(response => setProjects(response.data))
  //     .catch(error => console.error('Error fetching projects:', error));
  // }, [setProjects]);

  // const handleFileUpload = (file) => {
  //   const formData = new FormData();
  //   formData.append('file', file);

  //   apiClient.post('/projects', formData)
  //     .then(response => {
  //       console.log('File uploaded successfully', response);
  //     })
  //     .catch(error => {
  //       console.error('Error uploading file:', error);
  //     });
  // };

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">Chat with any PDF</h1>
      <p className="mb-6">Join millions of students, researchers, and professionals to instantly answer questions and understand research with AI</p>
      <FileDrop />
      <MyChats />
    </div>
  );
};

export default ProjectsDashboard;
