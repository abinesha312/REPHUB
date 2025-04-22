# src/hybrid_rank.py
"""
1. Parse raw resume files (PDF/DOCX) → structured dicts via PyResparser
2. Embed resumes + JD with the fine‑tuned SBERT
3. Compute hybrid score = w1*semantic + w2*skill + w3*experience
"""

import argparse, json, re, numpy as np, pandas as pd
from sentence_transformers import SentenceTransformer
from pyresparser import ResumeParser
from utils import cosine_sim, extract_required_info

# weights – tune if desired
w_sem, w_skill, w_exp = 0.5, 0.3, 0.2

def rank(jd_path: str, resume_paths, model_dir):
    # 1. embed job description
    jd_text = open(jd_path, encoding="utf8").read()
    model = SentenceTransformer(model_dir)
    jd_vec = model.encode(jd_text)

    # 2. parse JD for skills/exp requirement
    req_exp, req_skills = extract_required_info(jd_text)

    results = []
    for pdf_path in resume_paths:
        parsed = ResumeParser(pdf_path).get_extracted_data()
        res_text = parsed.get("text", "") or open(pdf_path, 'rb').read().decode('latin-1', 'ignore')
        res_vec  = model.encode(res_text)

        # components
        semantic = cosine_sim(jd_vec, res_vec)
        skill_overlap = set(s.lower() for s in parsed.get("skills", [])) & set(req_skills)
        skill_score = len(skill_overlap)/len(req_skills) if req_skills else 0
        exp_years = parsed.get("total_experience", 0) or 0
        exp_score = min(exp_years/req_exp, 1) if req_exp else 1

        final = w_sem*semantic + w_skill*skill_score + w_exp*exp_score
        results.append({
            "file": pdf_path,
            "score": final,
            "semantic": semantic,
            "skill_score": skill_score,
            "exp_score": exp_score,
            "matched_skills": list(skill_overlap),
            "years_exp": exp_years
        })

    ranked = sorted(results, key=lambda x: x["score"], reverse=True)
    return ranked

if __name__ == "__main__":
    pa = argparse.ArgumentParser()
    pa.add_argument("--jd", required=True, help="job_description.txt")
    pa.add_argument("--resumes", nargs="+", required=True, help="list of PDF/DOCX resumes")
    pa.add_argument("--model", default="../models/sbert_finetuned")
    args = pa.parse_args()

    ranks = rank(args.jd, args.resumes, args.model)
    pd.DataFrame(ranks).to_csv("ranked_results.csv", index=False)
    print("\n=== Top candidates ===")
    for r in ranks[:10]:
        print(f"{r['file']} → {r['score']:.3f}  (skills {len(r['matched_skills'])}, exp {r['years_exp']}y)")
