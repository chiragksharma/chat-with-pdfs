// PdfViewer.js
import React from 'react';
import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import apiClient from '../api/apiClient';



const PdfViewer = () => {
    const { id } = useParams(); // Access the dynamic id parameter from the route
    const [pdfUrl, setPdfUrl] = useState(null);

    useEffect(() => {
        const fetchDocument = async () => {
          try {
            const res = await apiClient.get(`/read/documents/${id}`);
            setPdfUrl(res.data.metadata.file_url); // Assuming the file URL is in metadata.file_url
          } catch (error) {
            console.error('Error fetching document:', error);
          }
        };
    
        fetchDocument();
      }, [id]);


  return (
    <div className="w-1/2 p-4">
      <h2 className="text-xl font-bold mb-4">Document</h2>
      {pdfUrl ? (
        <iframe
          src={pdfUrl}
          width="100%"
          height="600px"
          className="border border-gray-300 rounded-md"
        />
      ) : (
        <p>Loading...</p>
      )}
    </div>
  );
};

export default PdfViewer;
