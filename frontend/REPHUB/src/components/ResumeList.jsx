// frontend/src/components/ResumeList.jsx
import React from 'react';
import {
    Box,
    Typography,
    Paper,
    List,
    ListItem,
    ListItemText,
    Chip,
    Divider
} from '@mui/material';
import { format } from 'date-fns';

const ResumeList = ({ resumes }) => {
    if (!resumes || resumes.length === 0) {
        return (
            <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
                <Typography variant="h6" gutterBottom>
                    Your Resumes
                </Typography>
                <Typography variant="body1" color="text.secondary">
                    No resumes uploaded yet. Upload your first resume to get started.
                </Typography>
            </Paper>
        );
    }

    return (
        <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
                Your Resumes
            </Typography>

            <List>
                {resumes.map((resume, index) => (
                    <React.Fragment key={resume.id}>
                        {index > 0 && <Divider component="li" />}
                        <ListItem alignItems="flex-start">
                            <ListItemText
                                primary={
                                    <Box display="flex" alignItems="center">
                                        <Typography variant="subtitle1" component="span">
                                            Version {resume.version}
                                        </Typography>
                                        <Chip
                                            label={`V${resume.version}`}
                                            color="primary"
                                            size="small"
                                            sx={{ ml: 1 }}
                                        />
                                    </Box>
                                }
                                secondary={
                                    <>
                                        <Typography
                                            component="span"
                                            variant="body2"
                                            color="text.primary"
                                        >
                                            Uploaded on: {format(new Date(resume.upload_date), 'MMM dd, yyyy HH:mm')}
                                        </Typography>
                                        {resume.parsed_data?.entities?.skills && (
                                            <Box mt={1}>
                                                {resume.parsed_data.entities.skills.slice(0, 5).map((skill, i) => (
                                                    <Chip
                                                        key={i}
                                                        label={skill}
                                                        size="small"
                                                        sx={{ mr: 0.5, mb: 0.5 }}
                                                    />
                                                ))}
                                                {resume.parsed_data.entities.skills.length > 5 && (
                                                    <Chip
                                                        label={`+${resume.parsed_data.entities.skills.length - 5} more`}
                                                        size="small"
                                                        variant="outlined"
                                                    />
                                                )}
                                            </Box>
                                        )}
                                    </>
                                }
                            />
                        </ListItem>
                    </React.Fragment>
                ))}
            </List>
        </Paper>
    );
};

export default ResumeList;
