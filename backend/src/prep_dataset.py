# src/prep_dataset.py
"""
Build train/valid/test CSVs of (resume, job, label) pairs.
If you already have labelled pairs (AliYun/IntelliPro), just skip this step.
For unlabeled corpora, we create pseudo‑labels:
  – Assume each resume belongs to ONE ground‑truth JD (e.g. application history) → positive
  – Randomly sample k negative JDs for every resume
"""

import random, argparse, pandas as pd
from pathlib import Path
random.seed(42)

def main(resume_file: str, job_file: str, out_dir: str, k_neg: int = 3, val_split=0.1, test_split=0.1):
    resumes = pd.read_csv(resume_file)       # id,text
    jobs    = pd.read_csv(job_file)          # id,text

    print(f"Loaded {len(resumes)} resumes and {len(jobs)} jobs")

    # build positives (handling different dataset sizes)
    positives_list = []
    job_ids = jobs["id"].tolist()
    
    for _, resume_row in resumes.iterrows():
        # Randomly select one job as positive for each resume
        job_id = random.choice(job_ids)
        positives_list.append({
            "resume_id": resume_row["id"],
            "job_id": job_id,
            "label": 1
        })
    
    positives = pd.DataFrame(positives_list)

    # sample negatives
    negatives = []
    for _, row in positives.iterrows():
        # Get job IDs that weren't used as positive for this resume
        available_jobs = [j for j in job_ids if j != row.job_id]
        # If we have fewer jobs than k_neg, adjust k_neg
        actual_k_neg = min(k_neg, len(available_jobs))
        
        if actual_k_neg > 0:
            negs = random.sample(available_jobs, actual_k_neg)
            for jid in negs:
                negatives.append({"resume_id": row.resume_id, "job_id": jid, "label": 0})
    
    negatives = pd.DataFrame(negatives)
    print(f"Created {len(positives)} positive pairs and {len(negatives)} negative pairs")

    df = pd.concat([positives, negatives]).sample(frac=1).reset_index(drop=True)

    # split
    n = len(df)
    test_sz  = int(n * test_split)
    val_sz   = int(n * val_split)
    test_df  = df.iloc[:test_sz]
    val_df   = df.iloc[test_sz:test_sz+val_sz]
    train_df = df.iloc[test_sz+val_sz:]

    Path(out_dir).mkdir(exist_ok=True, parents=True)
    train_df.to_csv(f"{out_dir}/train.csv", index=False)
    val_df.to_csv(  f"{out_dir}/valid.csv", index=False)
    test_df.to_csv( f"{out_dir}/test.csv",  index=False)
    print(f"Saved splits to {out_dir}: {len(train_df)} train, {len(val_df)} validation, {len(test_df)} test samples")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--resumes", default="../data/resumes.csv")
    p.add_argument("--jobs",    default="../data/jobs.csv")
    p.add_argument("--out_dir", default="../data/pairs")
    args = p.parse_args()
    main(args.resumes, args.jobs, args.out_dir)
