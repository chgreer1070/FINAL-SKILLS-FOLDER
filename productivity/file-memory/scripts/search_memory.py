#!/usr/bin/env python3
"""Search file memory by keyword or semantic similarity."""

import argparse
import json
import math
import os
import pickle
import re
import sys
from pathlib import Path


def _files_dir(root: str) -> Path:
    return Path(root) / ".ai-memory" / "files"


def _cache_path(root: str) -> Path:
    return Path(root) / ".ai-memory" / ".embeddings_cache.pkl"


def _load_entries(root: str, session_filter: str | None = None) -> list[dict]:
    d = _files_dir(root)
    if not d.exists():
        return []
    entries = []
    for p in d.glob("*.json"):
        try:
            e = json.loads(p.read_text())
            entries.append(e)
        except Exception:
            pass
    if session_filter:
        # Load session to get file paths, then restrict
        sess_path = Path(root) / ".ai-memory" / "sessions" / f"{session_filter}.json"
        if sess_path.exists():
            sess = json.loads(sess_path.read_text())
            touched = {f["path"] for f in sess.get("files_touched", [])}
            entries = [e for e in entries if e.get("path") in touched]
    return entries


def _entry_text(e: dict, fields: list[str]) -> str:
    parts = []
    if "path" in fields:
        parts.append(e.get("path", ""))
    if "summary" in fields:
        parts.append(e.get("summary", ""))
    if "notes" in fields:
        for n in e.get("notes", []):
            parts.append(n.get("note", ""))
    if "tags" in fields:
        parts.extend(e.get("tags", []))
    return " ".join(parts).lower()


def keyword_search(entries: list[dict], query: str, fields: list[str]) -> list[tuple[float, dict]]:
    terms = query.lower().split()
    results = []
    for e in entries:
        text = _entry_text(e, fields)
        hits = sum(1 for t in terms if t in text)
        if hits > 0:
            score = hits / len(terms)
            results.append((score, e))
    return sorted(results, key=lambda x: x[0], reverse=True)


def tfidf_search(entries: list[dict], query: str, fields: list[str]) -> list[tuple[float, dict]]:
    """Simple TF-IDF search without sklearn."""
    corpus = [_entry_text(e, fields) for e in entries]
    query_terms = re.findall(r"\w+", query.lower())
    if not query_terms:
        return []

    # IDF
    n = len(corpus)
    df: dict[str, int] = {}
    tokenized = []
    for doc in corpus:
        toks = set(re.findall(r"\w+", doc))
        tokenized.append(toks)
        for t in toks:
            df[t] = df.get(t, 0) + 1

    idf = {t: math.log((n + 1) / (df.get(t, 0) + 1)) for t in query_terms}

    results = []
    for i, (e, toks_set) in enumerate(zip(entries, tokenized)):
        doc_words = re.findall(r"\w+", corpus[i])
        tf = {t: doc_words.count(t) / (len(doc_words) or 1) for t in query_terms}
        score = sum(tf.get(t, 0) * idf.get(t, 0) for t in query_terms)
        if score > 0:
            results.append((score, e))
    return sorted(results, key=lambda x: x[0], reverse=True)


def semantic_search(entries: list[dict], query: str, fields: list[str], cache_path: Path) -> list[tuple[float, dict]]:
    try:
        from sentence_transformers import SentenceTransformer
        import numpy as np

        model_name = "all-MiniLM-L6-v2"

        # Load or build cache
        cache: dict = {}
        if cache_path.exists():
            try:
                with open(cache_path, "rb") as f:
                    cache = pickle.load(f)
            except Exception:
                cache = {}

        model = SentenceTransformer(model_name)
        corpus_texts = [_entry_text(e, fields) for e in entries]
        slugs = [e.get("slug", str(i)) for i, e in enumerate(entries)]

        # Recompute only changed entries
        embeddings = []
        cache_dirty = False
        for slug, text in zip(slugs, corpus_texts):
            key = f"{slug}:{hash(text)}"
            if key in cache:
                embeddings.append(cache[key])
            else:
                emb = model.encode(text, normalize_embeddings=True)
                cache[key] = emb
                embeddings.append(emb)
                cache_dirty = True

        if cache_dirty:
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            with open(cache_path, "wb") as f:
                pickle.dump(cache, f)

        query_emb = model.encode(query, normalize_embeddings=True)
        scores = [float(np.dot(query_emb, emb)) for emb in embeddings]
        results = [(s, e) for s, e in zip(scores, entries) if s > 0.1]
        return sorted(results, key=lambda x: x[0], reverse=True)

    except ImportError:
        # Fall back to built-in TF-IDF
        return tfidf_search(entries, query, fields)


def format_table(results: list[tuple[float, dict]], limit: int) -> str:
    if not results:
        return "no matches found"
    lines = [f"{'Rank':<5} {'Score':>6}  {'Path':<40}  Summary"]
    lines.append("-" * 90)
    for rank, (score, e) in enumerate(results[:limit], 1):
        summary = (e.get("summary") or "")[:55] + ("..." if len(e.get("summary", "")) > 55 else "")
        lines.append(f"{rank:<5} {score:>6.2f}  {e.get('path',''):<40}  {summary}")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Search file memory")
    parser.add_argument("query", nargs="+")
    parser.add_argument("--root", default=".")
    parser.add_argument("--mode", choices=["keyword", "semantic", "both"], default="both")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--fields", default="path,summary,notes,tags")
    parser.add_argument("--format", choices=["table", "json"], default="table")
    parser.add_argument("--session")
    args = parser.parse_args()

    query = " ".join(args.query)
    fields = [f.strip() for f in args.fields.split(",")]
    entries = _load_entries(args.root, args.session)

    if not entries:
        print("no files in memory — use /file-memory:remember-file to start")
        return

    if args.mode == "keyword":
        results = keyword_search(entries, query, fields)
    elif args.mode == "semantic":
        results = semantic_search(entries, query, fields, _cache_path(args.root))
    else:
        kw = keyword_search(entries, query, fields)
        sem = semantic_search(entries, query, fields, _cache_path(args.root))
        # Merge: keyword first, then semantic items not already in results
        kw_slugs = {e.get("slug") for _, e in kw}
        combined = kw + [(s, e) for s, e in sem if e.get("slug") not in kw_slugs]
        results = combined

    if args.format == "json":
        print(json.dumps([e for _, e in results[:args.limit]], indent=2))
    else:
        print(format_table(results, args.limit))


if __name__ == "__main__":
    main()
