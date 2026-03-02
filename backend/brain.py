import json
import os
import re
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BRAIN_FILE = os.path.join(BASE_DIR, "brain_knowledge.json")

STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "how",
    "i", "in", "is", "it", "me", "my", "of", "on", "or", "that", "the",
    "this", "to", "was", "what", "when", "where", "who", "why", "with", "you",
}


def _default_brain():
    return {"entries": []}


def _tokenize(text):
    words = re.findall(r"[a-z0-9]+", text.lower())
    return [w for w in words if w not in STOPWORDS]


def load_brain():
    if not os.path.exists(BRAIN_FILE):
        return _default_brain()
    try:
        with open(BRAIN_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict) and isinstance(data.get("entries"), list):
                return data
    except json.JSONDecodeError:
        pass
    return _default_brain()


def save_brain(data):
    with open(BRAIN_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def teach_knowledge(text, source="user"):
    clean = text.strip()
    if not clean:
        return False

    data = load_brain()
    existing = {e.get("text", "").strip().lower() for e in data["entries"]}
    key = clean.lower()
    if key in existing:
        return False

    data["entries"].append(
        {
            "text": clean,
            "source": source,
            "created_at": datetime.now().isoformat(),
            "tokens": _tokenize(clean),
        }
    )
    save_brain(data)
    return True


def seed_identity(identity):
    if not isinstance(identity, dict):
        return
    for key, value in identity.items():
        if not value:
            continue
        teach_knowledge(f"user_{key}: {value}", source="identity")


def _score(query_tokens, entry_tokens, query_text, entry_text):
    if not entry_tokens:
        return 0.0
    overlap = len(set(query_tokens) & set(entry_tokens))
    token_score = overlap / max(1, len(set(query_tokens)))
    phrase_bonus = 0.2 if query_text in entry_text or any(t in entry_text for t in query_tokens) else 0.0
    return token_score + phrase_bonus


def search_knowledge(query, limit=3, min_score=0.25):
    query_clean = query.strip().lower()
    if not query_clean:
        return []
    query_tokens = _tokenize(query_clean)
    if not query_tokens:
        return []

    data = load_brain()
    scored = []
    for entry in data["entries"]:
        tokens = entry.get("tokens") or _tokenize(entry.get("text", ""))
        score = _score(query_tokens, tokens, query_clean, entry.get("text", "").lower())
        if score >= min_score:
            scored.append((score, entry))

    scored.sort(key=lambda item: item[0], reverse=True)
    return [entry for _, entry in scored[:limit]]


def answer_from_brain(query, history=None):
    hits = search_knowledge(query, limit=3)
    if not hits:
        return None

    best = hits[0]["text"]
    if len(hits) == 1:
        return f"From what I have learned: {best}"

    extra = "; ".join(entry["text"] for entry in hits[1:3])
    return f"From what I have learned: {best}. Related: {extra}"
