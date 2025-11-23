"""
Whoosh-based full text search for FAQ entries.
Functions to create and query a Whoosh index for FAQ questions, answers, and categories.
"""

from __future__ import annotations

import os
import importlib

from typing import Iterable, List

from whoosh.fields import Schema
from whoosh.fields import TEXT
from whoosh.fields import ID

from whoosh.analysis import StemmingAnalyzer

from whoosh.index import create_in
from whoosh.index import open_dir
from whoosh.index import exists_in

from whoosh.qparser import MultifieldParser

from vts.database import AppDatabase

# Provide a fallback QuerySyntaxError class and override it
# if Whoosh exposes a more specific exception
class QuerySyntaxError(Exception):
    """Fallback for Whoosh query syntax errors when unavailable."""

try:
    qparser_module = importlib.import_module("whoosh.qparser")
    qs_except = getattr(qparser_module, "QuerySyntaxError", None)
    if qs_except is not None:
        QuerySyntaxError = qs_except
except (ImportError, ModuleNotFoundError):
    pass

# Index directory name under Flask instance path
INDEX_DIR_NAME = "whoosh_index"


# Return Whoosh schema for FAQ entries
def _schema() -> Schema:
    "Return Whoosh schema for FAQ entries."
    return Schema(
        faq_id=ID(stored=True, unique=True),
        # Fields to be searched, uses StemmingAnalyzer for optimally matching words
        # StemmingAnalyzer reduces words to their root forms
        # So it can handle typos in searches better
        question=TEXT(stored=False, analyzer=StemmingAnalyzer()),
        answer=TEXT(stored=False, analyzer=StemmingAnalyzer()),
        category=TEXT(stored=False, analyzer=StemmingAnalyzer()),
    )


# Get index directory path from Flask instance path
def _index_path(instance_path: str) -> str:
    "Get index directory path from Flask instance path."
    return os.path.join(instance_path, INDEX_DIR_NAME)


# Rebuild Whoosh index from FAQ entries
def build_index(db: AppDatabase, instance_path: str) -> None:
    "Rebuild Whoosh index from FAQ entries."
    index_path = _index_path(instance_path)
    if not os.path.exists(index_path):
        os.makedirs(index_path, exist_ok=True)
    else:
        # Remove index contents if exists
        for filename in os.listdir(index_path):
            file_path = os.path.join(index_path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.remove(file_path)
                elif os.path.isdir(file_path):
                    # Remove nested dirs if present
                    for inner in os.listdir(file_path):
                        os.remove(os.path.join(file_path, inner))
                    os.rmdir(file_path)
            except OSError:
                pass

    ix = create_in(index_path, _schema())
    writer = ix.writer()

    # Map category id to name
    name_to_id = db.faq_categories_by_name()
    id_to_name = {cid: name for name, cid in name_to_id.items()}

    for entry in db.faq_entries():
        category_name = id_to_name.get(entry['category_id'], '')
        writer.add_document(
            faq_id=str(entry['id']),
            question=entry['question_text'],
            answer=entry['answer_text'],
            category=category_name,
        )
    writer.commit()


# Create index if missing
def ensure_index(db: AppDatabase, instance_path: str) -> None:
    "Create index if missing."
    index_path = _index_path(instance_path)
    if not os.path.exists(index_path):
        os.makedirs(index_path, exist_ok=True)
    if not exists_in(index_path):
        build_index(db, instance_path)

# Add a single FAQ entry to the index if it exists
def add_faq_to_index(db: AppDatabase, faq_id: int, instance_path: str) -> None:
    "Add a single FAQ entry to the index if it exists already."
    index_path = _index_path(instance_path)
    if not exists_in(index_path):
        return
    entries = db.faq_entry(faq_id)
    if not entries:
        return
    entry = entries[0]
    # Category name lookup
    categories = {c['id']: c['category_name'] for c in db.faq_categories()}
    category_name = categories.get(entry['category_id'], '')
    ix = open_dir(index_path)
    writer = ix.writer()
    writer.add_document(
        faq_id=str(entry['id']),
        question=entry['question_text'],
        answer=entry['answer_text'],
        category=category_name,
    )
    writer.commit()

# Update a single FAQ entry in the index
def update_faq_in_index(db: AppDatabase, faq_id: int, instance_path: str) -> None:
    "Update a single FAQ entry in the index."
    index_path = _index_path(instance_path)
    if not exists_in(index_path):
        return
    entries = db.faq_entry(faq_id)
    if not entries:
        return
    entry = entries[0]
    categories = {c['id']: c['category_name'] for c in db.faq_categories()}
    category_name = categories.get(entry['category_id'], '')
    ix = open_dir(index_path)
    writer = ix.writer()
    writer.update_document(
        faq_id=str(entry['id']),
        question=entry['question_text'],
        answer=entry['answer_text'],
        category=category_name,
    )
    writer.commit()

# Remove a single FAQ entry from the index
def remove_faq_from_index(faq_id: int, instance_path: str) -> None:
    "Remove a single FAQ entry from the index."
    index_path = _index_path(instance_path)
    if not exists_in(index_path):
        return
    ix = open_dir(index_path)
    writer = ix.writer()
    writer.delete_by_term('faq_id', str(faq_id))
    writer.commit()


# Get FAQ entry IDs matching query
def search_faq_ids(query: str, instance_path: str, limit: int = 50) -> List[int]:
    "Get FAQ entry IDs matching query."
    if not query:
        return []
    index_path = _index_path(instance_path)
    if not exists_in(index_path):
        return []
    ix = open_dir(index_path)
    parser = MultifieldParser(["question", "answer", "category"], schema=ix.schema)
    try:
        q = parser.parse(query)
    except (QuerySyntaxError, SyntaxError, ValueError):
        # Ignore malformed user queries
        return []
    results: List[int] = []
    with ix.searcher() as searcher:
        for hit in searcher.search(q, limit=limit):
            try:
                results.append(int(hit["faq_id"]))
            except (ValueError, KeyError):
                continue
    return results


# Fetch FAQ entries by ID
def fetch_entries_by_ids(db: AppDatabase, ids: Iterable[int]) -> list[dict]:
    "Fetch FAQ entries by ID."
    output: list[dict] = []
    for faq_id in ids:
        entries = db.faq_entry(faq_id)
        if entries:
            output.extend(entries)
    return output
