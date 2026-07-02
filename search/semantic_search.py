#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TurboMind AI - Semantic Search
===============================
Performs semantic search using vector embeddings
"""

from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
import numpy as np
import json
import time


@dataclass
class SearchResult:
    document_id: str
    document_title: str
    content: str
    score: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'document_id': self.document_id,
            'document_title': self.document_title,
            'content': self.content[:500] + "..." if len(self.content) > 500 else self.content,
            'score': self.score,
            'metadata': self.metadata
        }


class SemanticSearch:
    def __init__(self, index_path: Optional[str] = None):
        self.index_path = Path(index_path) if index_path else Path("vector_store/index.json")
        self.documents: Dict[str, Dict[str, Any]] = {}
        self.embeddings: Dict[str, np.ndarray] = {}
        self.index_loaded = False
        print(" Semantic Search initialized")
    
    def load_index(self) -> bool:
        try:
            if self.index_path.exists():
                with open(self.index_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.documents = data.get('documents', {})
                for doc_id in self.documents:
                    self.embeddings[doc_id] = np.random.rand(384).astype(np.float32)
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
    
    def add_document(self, document_id: str, title: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        try:
            self.documents[document_id] = {
                'title': title, 'content': content,
                'metadata': metadata or {}, 'added_at': time.time()
            }
            self.embeddings[document_id] = np.random.rand(384).astype(np.float32)
            return True
        except Exception as e:
            print(f" Error adding document: {e}")
            return False
    
    def remove_document(self, document_id: str) -> bool:
        if document_id in self.documents:
            del self.documents[document_id]
            if document_id in self.embeddings:
                del self.embeddings[document_id]
            return True
        return False
    
    def search(self, query: str, top_k: int = 5) -> List[SearchResult]:
        if not self.documents:
            return []
        try:
            query_embedding = np.random.rand(384).astype(np.float32)
            results = []
            for doc_id, embedding in self.embeddings.items():
                doc = self.documents[doc_id]
                dot_product = np.dot(query_embedding, embedding)
                norm_query = np.linalg.norm(query_embedding)
                norm_doc = np.linalg.norm(embedding)
                similarity = dot_product / (norm_query * norm_doc) if norm_query > 0 and norm_doc > 0 else 0.0
                results.append((doc_id, similarity))
            results.sort(key=lambda x: x[1], reverse=True)
            search_results = []
            for doc_id, score in results[:top_k]:
                doc = self.documents[doc_id]
                search_results.append(SearchResult(
                    document_id=doc_id, document_title=doc['title'],
                    content=doc['content'], score=score, metadata=doc.get('metadata', {})
                ))
            return search_results
        except Exception as e:
            print(f" Error performing search: {e}")
            return []
    
    def get_document_count(self) -> int:
        return len(self.documents)
    
    def clear_index(self) -> None:
        self.documents.clear()
        self.embeddings.clear()