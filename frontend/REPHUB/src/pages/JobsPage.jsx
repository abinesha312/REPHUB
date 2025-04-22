// src/pages/JobsPage.jsx
import React from 'react';
import JobDescriptionInput from '../components/JobDescriptionInput';

const JobsPage = ({ userId }) => {
    return (
        <JobDescriptionInput userId={userId} onSubmitSuccess={() => { }} />
    );
};

export default JobsPage;