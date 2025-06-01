import json
import os


def get_score_file(mode):
    return f"scores_{mode}.json"


def load_scores(mode):
    score_file = get_score_file(mode)
    if not os.path.exists(score_file):
        return []
    with open(score_file, "r", encoding="utf-8") as f:
        return json.load(f)


def save_score(name, score, mode):
    score_file = get_score_file(mode)
    scores = load_scores(mode)
    scores.append({"name": name, "score": score})
    scores = sorted(scores, key=lambda s: s["score"], reverse=True)[:5]
    with open(score_file, "w", encoding="utf-8") as f:
        json.dump(scores, f, indent=2, ensure_ascii=False)


def get_scoreboard_text(mode):
    scores = load_scores(mode)
    return [f"{i+1}. {s['name']} - {s['score']}" for i, s in enumerate(scores)]
