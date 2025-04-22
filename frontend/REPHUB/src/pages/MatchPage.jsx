// src/pages/MatchPage.jsx
import React from 'react';
import MatchResults from '../components/MatchResults';

const MatchPage = () => {
    // Mock data for testing
    const mockMatchResults = {
        job_title: "Sample Job",
        company: "Sample Company",
        matched_resumes: []
    };

    return (
        <MatchResults matchResults={mockMatchResults} />
    );
};

export default MatchPage;