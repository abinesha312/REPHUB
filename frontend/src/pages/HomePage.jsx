import React from 'react';
import { Container, Box, Typography, Paper, Grid, Button } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import FolderIcon from '@mui/icons-material/Folder';
import SearchIcon from '@mui/icons-material/Search';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';

const HomePage = () => {
  const navigate = useNavigate();

  const features = [
    {
      icon: <CloudUploadIcon sx={{ fontSize: 60, color: 'primary.main' }} />,
      title: 'Version Control',
      description: 'Upload and manage multiple versions of your resume. Organize by format: PDF, LaTeX, DOCX.',
      action: () => navigate('/resumes'),
      buttonText: 'Manage Resumes'
    },
    {
      icon: <SearchIcon sx={{ fontSize: 60, color: 'primary.main' }} />,
      title: 'Smart Matching',
      description: 'Use AI-powered semantic search to find the best resume version for any job description.',
      action: () => navigate('/match'),
      buttonText: 'Find Matches'
    },
    {
      icon: <FolderIcon sx={{ fontSize: 60, color: 'primary.main' }} />,
      title: 'Organized Repository',
      description: 'Keep all your resume versions organized with automatic versioning (v_1, v_2, v_3...).',
      action: () => navigate('/resumes'),
      buttonText: 'View Repository'
    }
  ];

  return (
    <Container maxWidth="lg" sx={{ py: 6 }}>
      <Box sx={{ textAlign: 'center', mb: 6 }}>
        <Typography variant="h2" gutterBottom>
          Resume Repository
        </Typography>
        <Typography variant="h5" color="text.secondary" sx={{ mb: 2 }}>
          GitHub for Your Resumes
        </Typography>
        <Typography variant="body1" color="text.secondary">
          A production-grade system for versioning, organizing, and matching resumes using AI-powered semantic search.
        </Typography>
      </Box>

      <Grid container spacing={4}>
        {features.map((feature, index) => (
          <Grid item xs={12} md={4} key={index}>
            <Paper
              elevation={3}
              sx={{
                p: 3,
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                textAlign: 'center'
              }}
            >
              <Box sx={{ mb: 2 }}>{feature.icon}</Box>
              <Typography variant="h5" gutterBottom>
                {feature.title}
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2, flexGrow: 1 }}>
                {feature.description}
              </Typography>
              <Button
                variant="contained"
                onClick={feature.action}
                fullWidth
              >
                {feature.buttonText}
              </Button>
            </Paper>
          </Grid>
        ))}
      </Grid>

      <Paper elevation={1} sx={{ mt: 6, p: 3, bgcolor: 'grey.100' }}>
        <Typography variant="h6" gutterBottom>
          How It Works
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} md={4}>
            <Typography variant="subtitle1" sx={{ fontWeight: 'bold' }}>
              1. Upload
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Upload your resume in any format (PDF, LaTeX, DOCX). The system extracts text and generates embeddings.
            </Typography>
          </Grid>
          <Grid item xs={12} md={4}>
            <Typography variant="subtitle1" sx={{ fontWeight: 'bold' }}>
              2. Version
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Each upload creates a new version (v_1, v_2, v_3...). Keep your entire resume history organized by format.
            </Typography>
          </Grid>
          <Grid item xs={12} md={4}>
            <Typography variant="subtitle1" sx={{ fontWeight: 'bold' }}>
              3. Match
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Paste a job description and instantly find your best matching resume using pgvector similarity search.
            </Typography>
          </Grid>
        </Grid>
      </Paper>
    </Container>
  );
};

export default HomePage;
