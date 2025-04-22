// frontend/src/components/MatchResults.jsx
import React from 'react';
import {
    Box,
    Typography,
    Paper,
    List,
    ListItem,
    ListItemText,
    Chip,
    Divider,
    LinearProgress,
    Grid
} from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import WarningIcon from '@mui/icons-material/Warning';
import { green, orange, red } from '@mui/material/colors';

const MatchResults = ({ matchResults }) => {
    if (!matchResults || !matchResults.matched_resumes || matchResults.matched_resumes.length === 0) {
        return null;
    }

    return (
        <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
                Resume Match Results
            </Typography>

            <Box sx={{ mb: 3 }}>
                <Typography variant="subtitle1">
                    Job: {matchResults.job_title} at {matchResults.company}
                </Typography>
            </Box>

            <List>
                {matchResults.matched_resumes.map((resume, index) => {
                    const score = Math.round(resume.overall_score * 100);
                    let scoreColor = green[500];
                    let scoreIcon = <CheckCircleIcon sx={{ color: green[500] }} />;

                    if (score < 60) {
                        scoreColor = red[500];
                        scoreIcon = <WarningIcon sx={{ color: red[500] }} />;
                    } else if (score < 80) {
                        scoreColor = orange[500];
                        scoreIcon = <WarningIcon sx={{ color: orange[500] }} />;
                    }

                    return (
                        <React.Fragment key={resume.resume_id}>
                            {index > 0 && <Divider component="li" />}
                            <ListItem alignItems="flex-start">
                                <ListItemText
                                    primary={
                                        <Box display="flex" alignItems="center">
                                            <Typography variant="subtitle1" component="span">
                                                Resume Version {resume.version}
                                            </Typography>
                                            <Chip
                                                label={`Match: ${score}%`}
                                                size="small"
                                                sx={{ ml: 1, backgroundColor: scoreColor, color: 'white' }}
                                            />
                                            <Box sx={{ ml: 'auto' }}>
                                                {scoreIcon}
                                            </Box>
                                        </Box>
                                    }
                                    secondary={
                                        <>
                                            <Box sx={{ mt: 2, mb: 1 }}>
                                                <LinearProgress
                                                    variant="determinate"
                                                    value={score}
                                                    sx={{
                                                        height: 10,
                                                        borderRadius: 5,
                                                        backgroundColor: '#e0e0e0',
                                                        '& .MuiLinearProgress-bar': {
                                                            backgroundColor: scoreColor
                                                        }
                                                    }}
                                                />
                                            </Box>

                                            <Grid container spacing={2} sx={{ mt: 1 }}>
                                                <Grid item xs={4}>
                                                    <Typography variant="body2" color="text.secondary">
                                                        Keyword Match:
                                                    </Typography>
                                                    <Typography variant="body2" color="text.primary">
                                                        {Math.round(resume.details.keyword_match * 100)}%
                                                    </Typography>
                                                </Grid>
                                                <Grid item xs={4}>
                                                    <Typography variant="body2" color="text.secondary">
                                                        Content Similarity:
                                                    </Typography>
                                                    <Typography variant="body2" color="text.primary">
                                                        {Math.round(resume.details.tfidf_similarity * 100)}%
                                                    </Typography>
                                                </Grid>
                                                <Grid item xs={4}>
                                                    <Typography variant="body2" color="text.secondary">
                                                        Semantic Match:
                                                    </Typography>
                                                    <Typography variant="body2" color="text.primary">
                                                        {Math.round(resume.details.semantic_similarity * 100)}%
                                                    </Typography>
                                                </Grid>
                                            </Grid>
                                        </>
                                    }
                                />
                            </ListItem>
                        </React.Fragment>
                    );
                })}
            </List>
        </Paper>
    );
};

export default MatchResults;
