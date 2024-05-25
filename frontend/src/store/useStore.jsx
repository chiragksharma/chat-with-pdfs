// src/store/useStore.js
import {create} from 'zustand';

const useStore = create((set) => ({
    projects: [],
    uploading: false, // Add uploading state
    setUploading: (uploading) => set({ uploading }), // Add setUploading action
    addProject: (project) => set((state) => ({ projects: [...state.projects, project] })),
    setProjects: (projects) => set({ projects }),
}));

export { useStore };
