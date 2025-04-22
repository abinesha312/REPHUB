// frontend/REPHUB/src/pages/ResumesPage.jsx
import React, { useState, useEffect } from 'react';
import ResumeUploader from '../components/ResumeUploader';
import ResumeList from '../components/ResumeList';

const ResumesPage = ({ userId }) => {
    const [resumes, setResumes] = useState([]);

    // In a real app, you would fetch resumes from API
    useEffect(() => {
        // Mock data for development
        const mockResumes = [];
        setResumes(mockResumes);
    }, [userId]);

    const handleUploadSuccess = (newResume) => {
        setResumes([...resumes, newResume]);
    };

    return (
        <>
            <ResumeUploader userId={userId} onUploadSuccess={handleUploadSuccess} />
            <ResumeList resumes={resumes} />
        </>
    );
};

export default ResumesPage;