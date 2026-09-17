import React, { useState } from 'react';
import { Container, Box, Typography } from '@mui/material';
import ResumeUploader from '../components/ResumeUploader';
import ResumeList from '../components/ResumeList';

const ResumePage = ({ userId }) => {
  const [refresh, setRefresh] = useState(0);

  const handleUploadSuccess = () => {
    setRefresh(prev => prev + 1);
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h3" gutterBottom>
        Resume Repository
      </Typography>
      
      <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
        Upload and manage your resume versions. Each format (PDF, LaTeX, etc.) maintains its own version history.
      </Typography>

      <ResumeUploader userId={userId} onUploadSuccess={handleUploadSuccess} />
      <ResumeList userId={userId} refresh={refresh} />
    </Container>
  );
};

export default ResumePage;
