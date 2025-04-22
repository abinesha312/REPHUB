// ResumeUploader.jsx
import React, { useState } from 'react';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import axios from 'axios';
import './ResumeUploader.css';

const ResumeUploader = ({ userId, onUploadSuccess }) => {
    const [file, setFile] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState(false);

    const handleFileChange = (event) => {
        setFile(event.target.files[0]);
        setError('');
        setSuccess(false);
    };

    const handleUpload = async () => {
        if (!file) {
            setError('Please select a file to upload');
            return;
        }

        const formData = new FormData();
        formData.append('file', file);
        formData.append('user_id', userId);

        setLoading(true);
        setError('');
        setSuccess(false);

        try {
            const response = await axios.post('/api/upload-resume/', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data'
                }
            });

            setSuccess(true);
            setFile(null);
            if (onUploadSuccess) {
                onUploadSuccess(response.data);
            }
        } catch (error) {
            setError(error.response?.data?.detail || 'Error uploading resume');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="uploader-container">
            <h2 className="uploader-title">Upload New Resume Version</h2>

            <div className="upload-area">
                <input
                    accept=".pdf,.doc,.docx"
                    style={{ display: 'none' }}
                    id="resume-upload"
                    type="file"
                    onChange={handleFileChange}
                />
                <label htmlFor="resume-upload">
                    <div className="file-button">
                        <CloudUploadIcon style={{ marginRight: '8px' }} />
                        Select Resume
                    </div>
                </label>

                {file && (
                    <div className="file-name">
                        Selected file: {file.name}
                    </div>
                )}

                <button
                    className="upload-button"
                    onClick={handleUpload}
                    disabled={!file || loading}
                >
                    {loading ? 'Uploading...' : 'Upload Resume'}
                </button>
            </div>

            {error && <div className="alert alert-error">{error}</div>}
            {success && <div className="alert alert-success">Resume uploaded successfully!</div>}
        </div>
    );
};

export default ResumeUploader;