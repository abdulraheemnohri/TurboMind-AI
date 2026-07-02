#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TurboMind AI - Keyword Search
===============================
Performs keyword-based search
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
import json
import re
import time
from collections import defaultdict


@dataclass
class KeywordSearchResult:
    document_id: str
    document_title: str
    content: str
    score: float
    matched_keywords: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'document_id': self.document_id,
            'document_title': self.document_title,
            'content': self.content[:500] + "..." if len(self.content) > 500 else self.content,
            'score': self.score,
            'matched_keywords': self.matched_keywords,
            'metadata': self.metadata
        }


class KeywordSearch:
    def __init__(self, index_path: Optional[str] = None):
        self.index_path = Path(index_path) if index_path else Path("vector_store/keyword_index.json")
        self.documents: Dict[str, Dict[str, Any]] = {}
        self.inverted_index: Dict[str, List[str]] = defaultdict(list)
        self.index_loaded = False
        print(" Keyword Search initialized")
    
    def load_index(self) -> bool:
        try:
            if self.index_path.exists():
                with open(self.index_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.documents = data.get('documents', {})
                self.inverted_index = defaultdict(list)
                for doc_id, doc in self.documents.items():
                    self._index_document(doc_id, doc)
                self.index_loaded = True
                return True
            return False
        except Exception as e:
            print(f" Error loading index: {e}")
            return False
    
    def save_index(self) -> bool:
        try:
            self.index_path.parent.mkdir(parents=True, exist_ok=True)
            data = {
                'documents': self.documents,
                'metadata': {'created_at': time.time(), 'document_count': len(self.documents)}
            }
            with open(self.index_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
            return True
        except Exception as e:
            print(f" Error saving index: {e}")
            return False
    
    def _index_document(self, doc_id: str, doc: Dict[str, Any]) -> None:
        content = doc.get('content', '')
        title = doc.get('title', '')
        all_text = f"{title} {content}".lower()
        words = re.findall(r'\b[a-zA-Z]{3,}\b', all_text)
        for word in words:
            self.inverted_index[word].append(doc_id)
    
    def add_document(self, document_id: str, title: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        try:
            self.documents[document_id] = {
                'title': title, 'content': content,
                'metadata': metadata or {}, 'added_at': time.time()
            }
            self._index_document(document_id, self.documents[document_id])
            return True
        except Exception as e:
            print(f" Error adding document: {e}")
            return False
    
    def remove_document(self, document_id: str) -> bool:
        if document_id in self.documents:
            del self.documents[document_id]
            for keyword, doc_ids in list(self.inverted_index.items()):
                if document_id in doc_ids:
                    doc_ids.remove(document_id)
                    if not doc_ids:
                        del self.inverted_index[keyword]
            return True
        return False
    
    def search(self, query: str, top_k: int = 5, exact_match: bool = False) -> List[KeywordSearchResult]:
        if not self.documents:
            return []
        try:
            query_lower = query.lower()
            keywords = [query_lower] if exact_match else re.findall(r'\b[a-zA-Z]{3,}\b', query_lower)
            if not keywords:
                return []
            doc_scores: Dict[str, float] = defaultdict(float)
            doc_keywords: Dict[str, List[str]] = defaultdict(list)
            for keyword in keywords:
                if keyword in self.inverted_index:
                    for doc_id in self.inverted_index[keyword]:
                        doc_scores[doc_id] += 1.0
                        if keyword not in doc_keywords[doc_id]:
                            doc_keywords[doc_id].append(keyword)
            sorted_docs = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)
            search_results = []
            for doc_id, score in sorted_docs[:top_k]:
                doc = self.documents[doc_id]
                search_results.append(KeywordSearchResult(
                    document_id=doc_id, document_title=doc['title'],
                    content=doc['content'], score=score,
                    matched_keywords=doc_keywords[doc_id], metadata=doc.get('metadata', {})
                ))
            return search_results
        except Exception as e:
            print(f" Error performing search: {e}")
            return []
    
    def phrase_search(self, phrase: str, top_k: int = 5) -> List[KeywordSearchResult]:
        if not self.documents:
            return []
        try:
            phrase_lower = phrase.lower()
            results = []
            for doc_id, doc in self.documents.items():
                content_lower = f"{doc['title']} {doc['content']}".lower()
                if phrase_lower in content_lower:
                    results.append((doc_id, 1.0))
            results.sort(key=lambda x: x[1], reverse=True)
            search_results = []
            for doc_id, score in results[:top_k]:
                doc = self.documents[doc_id]
                search_results.append(KeywordSearchResult(
                    document_id=doc_id, document_title=doc['title'],
                    content=doc['content'], score=score,
                    matched_keywords=[phrase], metadata=doc.get('metadata', {})
                ))
            return search_results
        except Exception as e:
            print(f" Error performing phrase search: {e}")
            return []
    
    def get_document_count(self) -> int:
        return len(self.documents)
    
    def clear_index(self) -> None:
        self.documents.clear()
        self.inverted_index.clear()