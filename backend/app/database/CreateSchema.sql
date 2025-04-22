-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Resumes table
CREATE TABLE resumes (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    version INTEGER NOT NULL,
    file_path VARCHAR(255) NOT NULL,
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    parsed_data JSONB,
    UNIQUE(user_id, version)
);

-- Job descriptions table
CREATE TABLE job_descriptions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    title VARCHAR(100),
    company VARCHAR(100),
    url VARCHAR(255),
    description TEXT,
    parsed_data JSONB,
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Resume-job matches table
CREATE TABLE matches (
    id SERIAL PRIMARY KEY,
    resume_id INTEGER REFERENCES resumes(id),
    job_id INTEGER REFERENCES job_descriptions(id),
    match_score FLOAT,
    match_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create a trigger function to automatically update the version number
CREATE OR REPLACE FUNCTION update_resume_version()
RETURNS TRIGGER AS $$
BEGIN

