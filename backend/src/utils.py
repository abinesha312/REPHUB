import re, numpy as np

def cosine_sim(a, b):
    a, b = np.asarray(a), np.asarray(b)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

_skill_re = re.compile(r"\*\*(.*?)\*\*|[-•]\s*([A-Za-z][\w\+\# ]{1,25})", re.S|re.I)
_exp_re   = re.compile(r"(\d+)\+?\s*years?", re.I)

def extract_required_info(jd_text: str):
    """Return (required_years:int|None, [skills] lowercase)."""
    m = _exp_re.search(jd_text)
    years = int(m.group(1)) if m else None

    skills = []
    for s1, s2 in _skill_re.findall(jd_text):
        token = (s1 or s2).strip().lower()
        if token and 1 <= len(token.split()) <= 3:
            skills.append(token)
    return years, sorted(set(skills))
