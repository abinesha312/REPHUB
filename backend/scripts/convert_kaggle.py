# scripts/convert_kaggle.py
import pandas as pd
import uuid
import pathlib
import os

# Create necessary directories
pathlib.Path("data").mkdir(exist_ok=True)
os.makedirs("data/raw/jobs-and-job-description", exist_ok=True)
os.makedirs("data/raw/resume-dataset", exist_ok=True)

# First file processing - jobs from jobs.csv
try:
    df1 = pd.read_csv("data/raw/jobs.csv")
    print(f"Columns in jobs.csv: {df1.columns.tolist()}")
    
    # Assuming the actual text column is 'Description' instead of 'Resume_str'
    # Check if 'Resume_str' exists, otherwise try common column names
    if 'Resume_str' in df1.columns:
        text_col = 'Resume_str'
    elif 'Description' in df1.columns:
        text_col = 'Description'
    elif 'description' in df1.columns:
        text_col = 'description'
    else:
        # If no known column is found, use the first text-like column
        text_cols = [col for col in df1.columns if df1[col].dtype == 'object']
        if text_cols:
            text_col = text_cols[0]
            print(f"Using column '{text_col}' as text source")
        else:
            raise ValueError("No suitable text column found in jobs.csv")
    
    df1 = df1.rename(columns={text_col: "text"})
    df1 = df1.assign(id=lambda d: [uuid.uuid4().hex for _ in range(len(d))])
    df1[["id", "text"]].to_csv("data/resumes.csv", index=False)
    print("Successfully created data/resumes.csv")
except Exception as e:
    print(f"Error processing jobs.csv: {e}")

# Second file processing - resumes from UpdatedResumeDataSet.csv
try:
    df2 = pd.read_csv("data/raw/UpdatedResumeDataSet.csv")
    print(f"Columns in UpdatedResumeDataSet.csv: {df2.columns.tolist()}")
    
    # Similar approach for the second file
    if 'description' in df2.columns:
        text_col = 'description'
    elif 'Description' in df2.columns:
        text_col = 'Description'
    elif 'Resume' in df2.columns:
        text_col = 'Resume'
    else:
        # If no known column is found, use the first text-like column
        text_cols = [col for col in df2.columns if df2[col].dtype == 'object']
        if text_cols:
            text_col = text_cols[0]
            print(f"Using column '{text_col}' as text source")
        else:
            raise ValueError("No suitable text column found in UpdatedResumeDataSet.csv")
    
    df2 = df2.rename(columns={text_col: "text"})
    df2 = df2.assign(id=lambda d: [uuid.uuid4().hex for _ in range(len(d))])
    df2[["id", "text"]].to_csv("data/jobs.csv", index=False)
    print("Successfully created data/jobs.csv")
except Exception as e:
    print(f"Error processing UpdatedResumeDataSet.csv: {e}")
