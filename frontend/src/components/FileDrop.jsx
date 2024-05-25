// src/components/FileDrop.js
import React,{useEffect,useState} from 'react';
import { Upload, message } from 'antd';
import { InboxOutlined } from '@ant-design/icons';
import { AtomSpinner } from 'react-epic-spinners';
import  {useStore}  from '../store/useStore'; // Import your zustand store
import { useNavigate } from 'react-router-dom';
import apiClient from '../api/apiClient';



const FileDrop = ({ }) => {
    const [title, setTitle] = useState('');
    const [description, setDescription] = useState('');
    const setUploading = useStore(state => state.setUploading);
    const uploading = useStore(state => state.uploading);
    const addProject = useStore(state => state.addProject); // Use addProject from your store

    const navigate = useNavigate();


    useEffect(() => {
        setUploading(false); // Reset uploading to false when the component mounts
    }, [setUploading]);

    const generateUniqueId = () => {
        return Math.random().toString(36).substr(2, 9); // Generate a random alphanumeric ID
    };

    const handleFileUpload = async (file,name) => {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('title', name);

        try {
            const response = await apiClient.post('/create', formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });

            if (response.data && response.data.document_id) {
                const projectData = {
                    title: name || `Project for ${file.name}`,
                    file_url: response.data.file_url
                };

                addProject(projectData);
                navigate(`/chat-interface/${response.data.document_id}`, { state: { projectData } });
                message.success(`${file.name} file uploaded and project created successfully.`);
            } else {
                message.error(`${file.name} file upload failed.`);
                console.log(`${file.name} File upload failed`);
            }
        } catch (error) {
            message.error(`Error uploading file or creating project: ${error.message}`);
            console.error('Error uploading file or creating project:', error);
        } finally {
            setUploading(false);
        }
    };


    const props = {
        name: 'file',
        multiple: false,
        accept: '.pdf', 
        action: 'http://127.0.0.1:5000/upload',
        beforeUpload: () => {
            setUploading(true);
        return true;
        },
        onChange(info) {
        const { status } = info.file;
        if (status !== 'uploading') {
            console.log("File:", info.file, info.fileList);
        }
        if (status === 'done') {
            if (info.file.response && info.file.response.file_url) {
                message.success(`${info.file.name} file uploaded successfully.`);
                handleFileUpload(info.file.originFileObj, info.file.name)
                .then(() => {
                    setUploading(false); // Only set uploading to false after handleFileUpload completes successfully
                })
                .catch((error) => {
                    message.error(`${info.file.name} file processing failed.`);
                    console.error('File processing failed:', error);
                    setUploading(false); // Set uploading to false even if handleFileUpload fails
                });            
            } else {
                message.error(`${info.file.name} file upload failed.`);
                console.log(`${info.file.name} File upload failed`);
            }
            setUploading(false);
        } else if (status === 'error') {
            message.error(`${info.file.name} file upload failed.`);
            console.log(`${info.file.name} File upload failed`);
            setUploading(false);
        }
        },
        onDrop(e) {
            console.log('Dropped files', e.dataTransfer.files);
        },
      };
    

  return (
    <Upload.Dragger {...props}>
      {uploading ? (
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <AtomSpinner color='blue' style={{ fontSize: '1em' }} />
                <p style={{ margin: '0 0 0 5px',fontSize: '1em' }}>Analyzing...</p>
            </div>
            ) : (
                <>
                    <p className="ant-upload-drag-icon">
                        <InboxOutlined />
                    </p>
                    <p className="ant-upload-text">Click or drag file to this area to upload</p>
                    <p className="ant-upload-hint">
                        Support for a single or bulk upload. Strictly prohibited from uploading company data or other banned files.
                    </p>
                </>
            )}
    </Upload.Dragger>
  );
};

export default FileDrop;

