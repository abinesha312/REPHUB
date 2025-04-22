# src/finetune_sbert.py
"""
Fine‑tunes a Sentence‑BERT encoder on resume/JD pairs with
MultipleNegativesRankingLoss (contrastive) + cosine similarity.
"""

from sentence_transformers import SentenceTransformer, InputExample, losses, evaluation
from torch.utils.data import DataLoader
import pandas as pd, argparse, os, torch, tqdm

def read_pairs(csv_path):
    df = pd.read_csv(csv_path)
    examples = [InputExample(texts=[row.resume_text, row.job_text], label=float(row.label))
                for row in df.itertuples()]
    return examples

def main(train_csv, valid_csv, resume_csv, job_csv, model_name, out_dir,
         batch_size=16, epochs=3, lr=2e-5, max_seq_len=256):
    os.makedirs(out_dir, exist_ok=True)

    # map id→text for fast join
    res_text = pd.read_csv(resume_csv).set_index("id")["text"].to_dict()
    job_text = pd.read_csv(job_csv).set_index("id")["text"].to_dict()

    # convert pair CSVs into InputExamples
    def csv_to_examples(path):
        df = pd.read_csv(path)
        rows = []
        for r in df.itertuples():
            rows.append(InputExample(
                texts=[res_text[r.resume_id], job_text[r.job_id]],
                label=float(r.label)))
        return rows

    train_examples = csv_to_examples(train_csv)
    valid_examples = csv_to_examples(valid_csv)

    model = SentenceTransformer(model_name)
    model.max_seq_length = max_seq_len

    train_dl = DataLoader(train_examples, shuffle=True, batch_size=batch_size,
                          drop_last=True)
    train_loss = losses.MultipleNegativesRankingLoss(model)

    evaluator = evaluation.EmbeddingSimilarityEvaluator.from_input_examples(
        valid_examples, batch_size=batch_size, name='val')

    warmup_steps = int(len(train_dl) * epochs * 0.1)
    model.fit(train_objectives=[(train_dl, train_loss)],
              evaluator=evaluator,
              epochs=epochs,
              warmup_steps=warmup_steps,
              optimizer_params={'lr': lr},
              show_progress_bar=True,
              use_amp=True)

    model.save(out_dir)
    print("Model saved to", out_dir)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--train", default="../data/pairs/train.csv")
    ap.add_argument("--valid", default="../data/pairs/valid.csv")
    ap.add_argument("--resumes", default="../data/resumes.csv")
    ap.add_argument("--jobs",    default="../data/jobs.csv")
    ap.add_argument("--model",   default="sentence-transformers/all-MiniLM-L6-v2")
    ap.add_argument("--out_dir", default="../models/sbert_finetuned")
    ap.add_argument("--batch_size", type=int, default=16)
    ap.add_argument("--epochs", type=int, default=4)
    args = ap.parse_args()
    main(args.train, args.valid, args.resumes, args.jobs,
         args.model, args.out_dir, args.batch_size, args.epochs)
