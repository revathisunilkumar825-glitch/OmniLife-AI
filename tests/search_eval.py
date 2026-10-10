"""Search evaluation helpers.

`evaluate(search_fn)` measures how good ANY search function is on the mock
dataset ("Test whether search returns the correct files" - Step 15).

A search function must look like:   search_fn(query: str) -> list[str]
and return document slugs (e.g. "internship_certificate"), best match first.

`keyword_search` is a deliberately simple baseline (word overlap). It shows
the harness works AND gives a number to beat: Member 3's semantic search
should do at least as well, and better on paraphrased queries. Great viva
material for "Why semantic search instead of keyword search?".
"""
import json
import re
from pathlib import Path

DATASET_DIR = Path(__file__).resolve().parent.parent / "documents" / "test_dataset"

STOPWORDS = {"my", "me", "the", "a", "an", "of", "to", "show", "find", "how",
             "much", "did", "is", "for", "and", "in", "on", "what"}


def load_manifest() -> dict:
    return json.loads((DATASET_DIR / "manifest.json").read_text(encoding="utf-8"))


def _words(text: str) -> set:
    return {w for w in re.findall(r"[a-z0-9]+", text.lower()) if w not in STOPWORDS}


def keyword_search(query: str, top_k: int = 5) -> list:
    q = _words(query)
    scored = []
    for doc in load_manifest()["documents"]:
        title_tags = _words(doc["title"] + " " + " ".join(doc["tags"]))
        summary = _words(doc["summary"])
        score = 3 * len(q & title_tags) + len(q & summary)
        if score:
            scored.append((score, doc["slug"]))
    scored.sort(key=lambda s: (-s[0], s[1]))
    return [slug for _, slug in scored[:top_k]]


def evaluate(search_fn, top_k: int = 3, kind: str = None) -> dict:
    """hit@k: a query counts as correct if ANY expected document is in the top k.
    kind = "keyword" | "paraphrase" | None (all queries)."""
    manifest = load_manifest()
    results = []
    for item in manifest["queries"]:
        if kind and item["kind"] != kind:
            continue
        returned = search_fn(item["query"])[:top_k]
        hit = any(slug in item["expected"] for slug in returned)
        results.append({"query": item["query"], "hit": hit, "returned": returned,
                        "expected": item["expected"]})
    hits = sum(r["hit"] for r in results)
    return {"hits": hits, "total": len(results),
            "accuracy": hits / len(results), "details": results}


if __name__ == "__main__":
    for kind in ("keyword", "paraphrase"):
        report = evaluate(keyword_search, kind=kind)
        print(f"Keyword baseline on {kind} queries: {report['hits']}/{report['total']} "
              f"({report['accuracy']:.0%}) hit@3")
        for r in report["details"]:
            print("  " + ("PASS " if r["hit"] else "FAIL ") + r["query"], "->", r["returned"])
