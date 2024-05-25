// src/components/MyChats.js
import React from 'react';
import {useStore} from '../store/useStore';

const MyChats = () => {
  const projects = useStore((state) => state.projects);

  return (
    <div className="mt-6">
      <h2 className="text-lg font-bold mb-4">My Chats</h2>
      <div className="bg-white p-4 rounded-lg shadow">
        {projects.length === 0 ? (
          <p className="text-gray-600">No chats available</p>
        ) : (
          projects.map((project, index) => (
            <div key={index} className="mb-2">
              <a href={`/project/${project.id}`} className="text-blue-600">{project.title}</a>
              <p className="text-gray-600">{project.description}</p>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default MyChats;
