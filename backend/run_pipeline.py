#!/usr/bin/env python
# run_pipeline.py
"""
A script to run the full data pipeline:
1. Convert raw data to the right format
2. Prepare datasets with train/valid/test splits
3. Fine-tune the sentence-BERT model
"""

import os
import subprocess
import sys
from pathlib import Path

# Ensure required directories exist
os.makedirs("data", exist_ok=True)
os.makedirs("data/raw", exist_ok=True)
os.makedirs("data/pairs", exist_ok=True)
os.makedirs("models", exist_ok=True)

def run_command(cmd, description=None):
    """Run a command and print its output in real-time"""
    if description:
        print(f"\n{'-'*80}\n{description}\n{'-'*80}")
    
    print(f"Running: {cmd}")
    process = subprocess.Popen(
        cmd, 
        shell=True, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1
    )
    
    # Print output in real-time
    for line in process.stdout:
        print(line, end='')
    
    process.wait()
    if process.returncode != 0:
        print(f"Error: Command failed with return code {process.returncode}")
        sys.exit(process.returncode)
    
    return process.returncode

def main():
    # Check if raw data files exist
    if not (Path("data/raw/jobs.csv").exists() and 
            Path("data/raw/UpdatedResumeDataSet.csv").exists()):
        print("Warning: Raw data files not found in data/raw/ directory.")
        print("Please place the following files in data/raw/ directory:")
        print("  - jobs.csv")
        print("  - UpdatedResumeDataSet.csv")
        user_input = input("Continue anyway? (y/n): ")
        if user_input.lower() != 'y':
            return
    
    # Step 1: Convert Kaggle datasets to standard format
    run_command(
        "python scripts/convert_kaggle.py",
        "Step 1: Converting raw data to standard format"
    )
    
    # Step 2: Prepare dataset splits (train/valid/test)
    run_command(
        "python src/prep_dataset.py --resumes data/resumes.csv --jobs data/jobs.csv --out_dir data/pairs",
        "Step 2: Preparing dataset splits"
    )
    
    # Step 3: Fine-tune the sentence-BERT model
    run_command(
        "python src/finetune_sbert.py --train data/pairs/train.csv --valid data/pairs/valid.csv --resumes data/resumes.csv --jobs data/jobs.csv --model sentence-transformers/all-MiniLM-L6-v2 --out_dir models/sbert_finetuned --batch_size 8 --epochs 2",
        "Step 3: Fine-tuning the sentence-BERT model"
    )
    
    print("\nPipeline completed successfully!")
    print("The fine-tuned model is saved in models/sbert_finetuned/")

if __name__ == "__main__":
    main() 