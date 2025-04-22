// frontend/REPHUB/src/pages/HomePage.jsx
import React from 'react';
import { Typography, Container, Paper, Box } from '@mui/material';

const HomePage = () => {
    return (
        <Container maxWidth="md">
            <Paper elevation={3} sx={{ p: 4, mt: 4 }}>
                <Typography variant="h4" component="h1" gutterBottom>
                    Welcome to REPHUB
                </Typography>
                <Typography variant="body1" paragraph>
                    Upload your resume and job descriptions to find the perfect match!
                </Typography>
                <Box sx={{ mt: 2 }}>
                    <Typography variant="subtitle1">Get started by:</Typography>
                    <ul>
                        <li>Uploading your resume in the Resumes section</li>
                        <li>Adding job descriptions in the Jobs section</li>
                        <li>Viewing match results in the Match section</li>
                    </ul>
                </Box>
            </Paper>
        </Container>
    );
};

export default HomePage;