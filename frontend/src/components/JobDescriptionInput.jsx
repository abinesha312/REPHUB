import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  CircularProgress,
  Alert
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import axios from 'axios';

const JobDescriptionInput = ({ userId, onMatchResults }) => {
  const [jobDescription, setJobDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleMatch = async () => {
    if (!jobDescription.trim() || jobDescription.length < 10) {
      setError('Please enter at least 10 characters');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await axios.post('/api/match/', {
        job_description: jobDescription,
        user_id: userId,
        limit: 10
      });

      onMatchResults(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Match failed');
      console.error('Match error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
      <Typography variant="h5" gutterBottom>
        Find Matching Resumes
      </Typography>
      
      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
        Paste a job description to find the best matching resume versions using AI-powered semantic search.
      </Typography>

      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
        <TextField
          multiline
          rows={8}
          fullWidth
          placeholder="Paste job description here...&#10;&#10;Example:&#10;We're looking for a Senior Software Engineer with 5+ years experience in Python, React, and cloud infrastructure..."
          value={jobDescription}
          onChange={(e) => {
            setJobDescription(e.target.value);
            setError('');
          }}
          variant="outlined"
        />

        <Button
          variant="contained"
          size="large"
          startIcon={loading ? <CircularProgress size={20} color="inherit" /> : <SearchIcon />}
          onClick={handleMatch}
          disabled={loading || jobDescription.length < 10}
        >
          {loading ? 'Searching...' : 'Find Best Matches'}
        </Button>

        {error && <Alert severity="error">{error}</Alert>}
      </Box>
    </Paper>
  );
};

export default JobDescriptionInput;
