#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TurboMind AI - Search Index Manager
===================================
Manages search indexes and document indexing
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
import json
import time


class SearchIndex:
    def __init__(self, index_dir: Optional[str] = None):
        self.index_dir = Path(index_dir) if index_dir else Path("vector_store")
        self.index_dir.mkdir(parents=True, exist_ok=True)
        from .semantic_search import SemanticSearch
        from .keyword_search import KeywordSearch
        from .hybrid_search import HybridSearch
        self.semantic_search = SemanticSearch(self.index_dir / "semantic_index.json")
        self.keyword_search = KeywordSearch(self.index_dir / "keyword_index.json")
        self.hybrid_search = HybridSearch(self.semantic_search, self.keyword_search)
        self.semantic_search.load_index()
        self.keyword_search.load_index()
        print(" Search Index Manager initialized")
    
    def add_document(self, document_id: str, title: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        try:
            return self.semantic_search.add_document(document_id, title, content, metadata) and                    self.keyword_search.add_document(document_id, title, content, metadata)
        except Exception as e:
            print(f" Error indexing document: {e}")
            return False
    
    def remove_document(self, document_id: str) -> bool:
        try:
            return self.semantic_search.remove_document(document_id) and                    self.keyword_search.remove_document(document_id)
        except Exception as e:
            print(f" Error removing document: {e}")
            return False
    
    def semantic_search(self, query: str, top_k: int = 5) -> List[Any]:
        return self.semantic_search.search(query, top_k)
    
    def keyword_search(self, query: str, top_k: int = 5, exact_match: bool = False) -> List[Any]:
        return self.keyword_search.search(query, top_k, exact_match)
    
    def phrase_search(self, phrase: str, top_k: int = 5) -> List[Any]:
        return self.keyword_search.phrase_search(phrase, top_k)
    
    def hybrid_search(self, query: str, top_k: int = 5) -> List[Any]:
        return self.hybrid_search.search(query, top_k)
    
    def set_hybrid_weights(self, semantic_weight: float = 0.7, keyword_weight: float = 0.3) -> None:
        self.hybrid_search.set_weights(semantic_weight, keyword_weight)
    
    def save_all_indexes(self) -> bool:
        try:
            return self.semantic_search.save_index() and self.keyword_search.save_index()
        except Exception as e:
            print(f" Error saving indexes: {e}")
            return False
    
    def clear_all_indexes(self) -> None:
        self.semantic_search.clear_index()
        self.keyword_search.clear_index()
    
    def get_statistics(self) -> Dict[str, Any]:
        return {
            'semantic_documents': self.semantic_search.get_document_count(),
            'keyword_documents': self.keyword_search.get_document_count(),
            'total_documents': max(self.semantic_search.get_document_count(), self.keyword_search.get_document_count())
        }