import React from 'react';
import {
  Box,
  Paper,
  Typography,
  List,
  ListItem,
  ListItemText,
  Button,
  Chip,
  LinearProgress,
  Alert
} from '@mui/material';
import DownloadIcon from '@mui/icons-material/Download';
import StarIcon from '@mui/icons-material/Star';
import axios from 'axios';

const MatchResults = ({ results }) => {
  if (!results) {
    return null;
  }

  const { matches, total_candidates, job_description } = results;

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

  const getScoreColor = (score) => {
    if (score >= 0.8) return 'success';
    if (score >= 0.6) return 'primary';
    if (score >= 0.4) return 'warning';
    return 'default';
  };

  const getScoreLabel = (score) => {
    if (score >= 0.8) return 'Excellent Match';
    if (score >= 0.6) return 'Good Match';
    if (score >= 0.4) return 'Fair Match';
    return 'Weak Match';
  };

  if (matches.length === 0) {
    return (
      <Alert severity="info">
        No matching resumes found. Try uploading some resumes first!
      </Alert>
    );
  }

  return (
    <Paper elevation={3} sx={{ p: 3 }}>
      <Typography variant="h5" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <StarIcon color="primary" />
        Match Results
      </Typography>
      
      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
        Found {matches.length} match{matches.length !== 1 ? 'es' : ''} out of {total_candidates} candidate{total_candidates !== 1 ? 's' : ''}
      </Typography>

      <Box sx={{ mb: 3, p: 2, bgcolor: 'grey.100', borderRadius: 1 }}>
        <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 'bold' }}>
          JOB DESCRIPTION
        </Typography>
        <Typography variant="body2" sx={{ mt: 1, whiteSpace: 'pre-wrap' }}>
          {job_description.length > 300 
            ? job_description.substring(0, 300) + '...' 
            : job_description}
        </Typography>
      </Box>

      <List>
        {matches.map((match, index) => (
          <ListItem
            key={match.resume_id}
            sx={{
              border: '2px solid',
              borderColor: index === 0 ? 'primary.main' : 'divider',
              borderRadius: 2,
              mb: 2,
              flexDirection: 'column',
              alignItems: 'stretch'
            }}
          >
            <Box sx={{ display: 'flex', justifyContent: 'space-between', width: '100%', mb: 1 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Chip 
                  label={`#${index + 1}`} 
                  size="small" 
                  color={index === 0 ? 'primary' : 'default'}
                />
                <Typography variant="h6">{match.filename}</Typography>
              </Box>
              
              <Button
                variant={index === 0 ? 'contained' : 'outlined'}
                size="small"
                startIcon={<DownloadIcon />}
                onClick={() => handleDownload(match.resume_id, match.filename)}
              >
                Download
              </Button>
            </Box>

            <Box sx={{ width: '100%', mb: 1 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                <Typography variant="caption" color="text.secondary">
                  Similarity Score
                </Typography>
                <Chip 
                  label={getScoreLabel(match.similarity_score)}
                  size="small"
                  color={getScoreColor(match.similarity_score)}
                />
              </Box>
              <LinearProgress 
                variant="determinate" 
                value={match.similarity_score * 100}
                color={getScoreColor(match.similarity_score)}
                sx={{ height: 8, borderRadius: 1 }}
              />
              <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5 }}>
                {(match.similarity_score * 100).toFixed(1)}% match
              </Typography>
            </Box>

            <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
              <Chip label={`v_${match.version}`} size="small" variant="outlined" />
              <Chip label={match.format.toUpperCase()} size="small" variant="outlined" />
              <Chip 
                label={new Date(match.uploaded_at).toLocaleDateString()} 
                size="small" 
                variant="outlined" 
              />
            </Box>
          </ListItem>
        ))}
      </List>
    </Paper>
  );
};

export default MatchResults;
