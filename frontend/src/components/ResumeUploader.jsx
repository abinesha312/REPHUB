import React, { useState } from 'react';
import {
  Box,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Typography,
  Alert,
  CircularProgress,
  Paper
} from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import axios from 'axios';

const ResumeUploader = ({ userId, onUploadSuccess }) => {
  const [file, setFile] = useState(null);
  const [format, setFormat] = useState('pdf');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];
    setFile(selectedFile);
    setError('');
    setSuccess(false);
    
    // Auto-detect format from extension
    if (selectedFile) {
      const ext = selectedFile.name.split('.').pop().toLowerCase();
      if (['pdf', 'doc', 'docx', 'tex'].includes(ext)) {
        setFormat(ext === 'tex' ? 'latex' : ext);
      }
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file to upload');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);
    formData.append('user_id', userId);
    formData.append('format', format);

    setLoading(true);
    setError('');
    setSuccess(false);

    try {
      const response = await axios.post('/api/resumes/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      setSuccess(true);
      setFile(null);
      if (onUploadSuccess) {
        onUploadSuccess(response.data);
      }
      
      // Reset file input
      document.getElementById('resume-upload').value = '';
    } catch (err) {
      setError(err.response?.data?.detail || 'Error uploading resume');
      console.error('Upload error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
      <Typography variant="h5" gutterBottom>
        Upload New Resume Version
      </Typography>
      
      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
        Upload a new version of your resume. The system will automatically version it as v_1, v_2, v_3, etc.
      </Typography>

      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
        <FormControl fullWidth>
          <InputLabel>Resume Format</InputLabel>
          <Select
            value={format}
            label="Resume Format"
            onChange={(e) => setFormat(e.target.value)}
          >
            <MenuItem value="pdf">PDF</MenuItem>
            <MenuItem value="latex">LaTeX / TeX</MenuItem>
            <MenuItem value="doc">DOC</MenuItem>
            <MenuItem value="docx">DOCX</MenuItem>
          </Select>
        </FormControl>

        <Box>
          <input
            accept=".pdf,.doc,.docx,.tex,.txt"
            style={{ display: 'none' }}
            id="resume-upload"
            type="file"
            onChange={handleFileChange}
          />
          <label htmlFor="resume-upload">
            <Button
              variant="outlined"
              component="span"
              startIcon={<CloudUploadIcon />}
              fullWidth
            >
              Select File
            </Button>
          </label>
        </Box>

        {file && (
          <Alert severity="info">
            Selected: {file.name} ({(file.size / 1024).toFixed(1)} KB)
          </Alert>
        )}

        <Button
          variant="contained"
          onClick={handleUpload}
          disabled={!file || loading}
          fullWidth
        >
          {loading ? <CircularProgress size={24} /> : 'Upload Resume'}
        </Button>

        {error && <Alert severity="error">{error}</Alert>}
        {success && (
          <Alert severity="success">
            Resume uploaded successfully! Version created.
          </Alert>
        )}
      </Box>
    </Paper>
  );
};

export default ResumeUploader;
