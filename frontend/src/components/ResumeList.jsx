import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  List,
  ListItem,
  ListItemText,
  Button,
  Chip,
  Divider,
  CircularProgress,
  Alert
} from '@mui/material';
import DownloadIcon from '@mui/icons-material/Download';
import FolderIcon from '@mui/icons-material/Folder';
import axios from 'axios';

const ResumeList = ({ userId, refresh }) => {
  const [resumes, setResumes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchResumes = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await axios.get('/api/resumes/list', {
        params: { user_id: userId }
      });
      setResumes(response.data.resumes || []);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load resumes');
      console.error('Fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchResumes();
  }, [userId, refresh]);

  const handleDownload = async (resumeId, filename) => {
    try {
      const response = await axios.get(`/api/resumes/download/${resumeId}`, {
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      alert('Download failed: ' + (err.response?.data?.detail || err.message));
    }
  };

  const groupByFormat = (resumes) => {
    const groups = {};
    resumes.forEach(resume => {
      if (!groups[resume.format]) {
        groups[resume.format] = [];
      }
      groups[resume.format].push(resume);
    });
    return groups;
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return <Alert severity="error">{error}</Alert>;
  }

  if (resumes.length === 0) {
    return (
      <Alert severity="info">
        No resumes uploaded yet. Upload your first version above!
      </Alert>
    );
  }

  const groupedResumes = groupByFormat(resumes);

  return (
    <Paper elevation={3} sx={{ p: 3 }}>
      <Typography variant="h5" gutterBottom>
        My Resume Repository
      </Typography>
      
      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
        {resumes.length} version{resumes.length !== 1 ? 's' : ''} across {Object.keys(groupedResumes).length} format{Object.keys(groupedResumes).length !== 1 ? 's' : ''}
      </Typography>

      {Object.entries(groupedResumes).map(([format, formatResumes]) => (
        <Box key={format} sx={{ mb: 3 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
            <FolderIcon sx={{ mr: 1, color: 'primary.main' }} />
            <Typography variant="h6" sx={{ textTransform: 'uppercase' }}>
              {format}
            </Typography>
            <Chip 
              label={`${formatResumes.length} version${formatResumes.length !== 1 ? 's' : ''}`} 
              size="small" 
              sx={{ ml: 1 }}
            />
          </Box>
          
          <List>
            {formatResumes
              .sort((a, b) => b.version - a.version)
              .map((resume) => (
                <ListItem
                  key={resume.id}
                  sx={{
                    border: '1px solid',
                    borderColor: 'divider',
                    borderRadius: 1,
                    mb: 1
                  }}
                  secondaryAction={
                    <Button
                      variant="outlined"
                      size="small"
                      startIcon={<DownloadIcon />}
                      onClick={() => handleDownload(resume.id, resume.filename)}
                    >
                      Download
                    </Button>
                  }
                >
                  <ListItemText
                    primary={
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Chip 
                          label={`v_${resume.version}`} 
                          size="small" 
                          color="primary" 
                        />
                        <Typography variant="body1">{resume.filename}</Typography>
                      </Box>
                    }
                    secondary={
                      <Typography variant="caption" color="text.secondary">
                        Uploaded: {new Date(resume.uploaded_at).toLocaleString()} • 
                        {resume.file_size ? ` ${(resume.file_size / 1024).toFixed(1)} KB • ` : ' '}
                        {resume.has_embedding ? '✓ Embedded' : '⚠ No embedding'}
                      </Typography>
                    }
                  />
                </ListItem>
              ))}
          </List>
          
          <Divider sx={{ my: 2 }} />
        </Box>
      ))}
    </Paper>
  );
};

export default ResumeList;
