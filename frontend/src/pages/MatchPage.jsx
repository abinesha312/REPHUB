import React, { useState } from 'react';
import { Container, Box, Typography } from '@mui/material';
import JobDescriptionInput from '../components/JobDescriptionInput';
import MatchResults from '../components/MatchResults';

const MatchPage = ({ userId }) => {
  const [matchResults, setMatchResults] = useState(null);

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h3" gutterBottom>
        Job Match
      </Typography>
      
      <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
        Find the best resume version for a specific job description using AI-powered semantic matching.
      </Typography>

      <JobDescriptionInput 
        userId={userId} 
        onMatchResults={setMatchResults} 
      />
      
      {matchResults && <MatchResults results={matchResults} />}
    </Container>
  );
};

export default MatchPage;
