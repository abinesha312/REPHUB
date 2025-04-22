// frontend/src/components/JobDescriptionInput.jsx
import React, { useState } from 'react';
import { 
    Button, 
    Box, 
    Typography, 
    TextField, 
    CircularProgress, 
    Paper, 
    Alert,
    Tab,
    Tabs,
    FormControl,
    InputLabel,
    Input
} from '@mui/material';
import axios from 'axios';

const JobDescriptionInput = ({ userId, onSubmitSuccess }) => {
    const [activeTab, setActiveTab] = useState(0);
    const [jobTitle, setJobTitle] = useState('');
    const [company, setCompany] = useState('');
    const [jobUrl, setJobUrl] = useState('');
    const [file, setFile] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState(false);

    const handleTabChange = (event, newValue) => {
        setActiveTab(newValue);
    };

    const handleFileChange = (event) => {
        setFile(event.target.files[0]);
    };

    const handleSubmit = async () => {
        if ((!jobUrl && !file) || !jobTitle || !company) {
            setError('Please complete all required fields');
            return;
        }

        const formData = new FormData();
        formData.append('user_id', userId);
        formData.append('title', jobTitle);
        formData.append('company', company);
        
        if (activeTab === 0 && jobUrl) {
            formData.append('url', jobUrl);
        } else if (activeTab === 1 && file) {
            formData.append('file', file);
        } else {
            setError('Please provide either a valid job URL or upload a file');
            return;
        }

        setLoading(true);
        setError('');
        setSuccess(false);

        try {
            const response = await axios.post('/api/upload-job-description/', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data'
                }
            });

            setSuccess(true);
            setJobTitle('');
            setCompany('');
            setJobUrl('');
            setFile(null);
            
            if (onSubmitSuccess) {
                onSubmitSuccess(response.data);
            }
        } catch (error) {
            setError(error.response?.data?.detail || 'Error processing job description');
        } finally {
            setLoading(false);
        }
    };

    return (
        <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
                Add Job Description
            </Typography>
            
            <TextField
                label="Job Title"
                variant="outlined"
                fullWidth
                value={jobTitle}
                onChange={(e) => setJobTitle(e.target.value)}
                margin="normal"
                required
            />
            
            <TextField
                label="Company"
                variant="outlined"
                fullWidth
                value={company}
                onChange={(e) => setCompany(e.target.value)}
                margin="normal"
                required
            />
            
            <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2, mt: 3 }}>
                <Tabs value={activeTab} onChange={handleTabChange}>
                    <Tab label="Job URL" />
                    <Tab label="Upload File" />
                </Tabs>
            </Box>
            
            {activeTab === 0 && (
                <TextField
                    label="Job Posting URL"
                    variant="outlined"
                    fullWidth
                    value={jobUrl}
                    onChange={(e) => setJobUrl(e.target.value)}
                    margin="normal"
                    placeholder="https://example.com/job-posting"
                    required
                />
            )}
            
            {activeTab === 1 && (
                <Box sx={{ mb: 2, mt: 2 }}>
                    <FormControl fullWidth margin="normal">
                        <InputLabel htmlFor="job-file-upload">Job Description File</InputLabel>
                        <Input
                            id="job-file-upload"
                            type="file"
                            onChange={handleFileChange}
                            required
                        />
                    </FormControl>
                    {file && (
                        <Typography variant="body2" sx={{ mt: 1 }}>
                            Selected file: {file.name}
                        </Typography>
                    )}
                </Box>
            )}
            
            <Button
                variant="contained"
                color="primary"
                onClick={handleSubmit}
                disabled={loading}
                sx={{ mt: 3, minWidth: 200 }}
            >
                {loading ? <CircularProgress size={24} /> : 'Submit Job Description'}
            </Button>
            
            {error && <Alert severity="error" sx={{ mt: 2 }}>{error}</Alert>}
            {success && <Alert severity="success" sx={{ mt: 2 }}>Job description processed successfully!</Alert>}
        </Paper>
    );
};

export default JobDescriptionInput;
