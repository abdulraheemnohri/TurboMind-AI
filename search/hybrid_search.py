#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TurboMind AI - Hybrid Search
=============================
Combines semantic and keyword search
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class HybridSearchResult:
    document_id: str
    document_title: str
    content: str
    semantic_score: float
    keyword_score: float
    combined_score: float
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'document_id': self.document_id,
            'document_title': self.document_title,
            'content': self.content[:500] + "..." if len(self.content) > 500 else self.content,
            'semantic_score': self.semantic_score,
            'keyword_score': self.keyword_score,
            'combined_score': self.combined_score,
            'metadata': self.metadata
        }


class HybridSearch:
    def __init__(self, semantic_search=None, keyword_search=None):
        self.semantic_search = semantic_search
        self.keyword_search = keyword_search
        self.semantic_weight = 0.7
        self.keyword_weight = 0.3
        print(" Hybrid Search initialized")
    
    def set_weights(self, semantic_weight: float = 0.7, keyword_weight: float = 0.3) -> None:
        total = semantic_weight + keyword_weight
        if total > 0:
            self.semantic_weight = semantic_weight / total
            self.keyword_weight = keyword_weight / total
        else:
            self.semantic_weight = 0.5
            self.keyword_weight = 0.5
    
    def search(self, query: str, top_k: int = 5) -> List[HybridSearchResult]:
        if not self.semantic_search or not self.keyword_search:
            return []
        try:
            semantic_results = self.semantic_search.search(query, top_k * 2)
            keyword_results = self.keyword_search.search(query, top_k * 2)
            combined_scores: Dict[str, Dict[str, float]] = {}
            for result in semantic_results:
                doc_id = result.document_id
                if doc_id not in combined_scores:
                    combined_scores[doc_id] = {'semantic': 0.0, 'keyword': 0.0}
                combined_scores[doc_id]['semantic'] = result.score
            for result in keyword_results:
                doc_id = result.document_id
                if doc_id not in combined_scores:
                    combined_scores[doc_id] = {'semantic': 0.0, 'keyword': 0.0}
                combined_scores[doc_id]['keyword'] = result.score
            results = []
            for doc_id, scores in combined_scores.items():
                semantic_score = scores['semantic']
                keyword_score = scores['keyword']
                combined_score = (self.semantic_weight * semantic_score + self.keyword_weight * keyword_score)
                doc_info = None
                for result in semantic_results:
                    if result.document_id == doc_id:
                        doc_info = result
                        break
                if doc_info:
                    results.append(HybridSearchResult(
                        document_id=doc_id, document_title=doc_info.document_title,
                        content=doc_info.content, semantic_score=semantic_score,
                        keyword_score=keyword_score, combined_score=combined_score,
                        metadata=doc_info.metadata
                    ))
            results.sort(key=lambda x: x.combined_score, reverse=True)
            return results[:top_k]
        except Exception as e:
            print(f" Error performing hybrid search: {e}")
            return []
    
    def add_document(self, document_id: str, title: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        if self.semantic_search and self.keyword_search:
            return self.semantic_search.add_document(document_id, title, content, metadata) and                    self.keyword_search.add_document(document_id, title, content, metadata)
        return False
    
    def clear_index(self) -> None:
        if self.semantic_search:
            self.semantic_search.clear_index()
        if self.keyword_search:
            self.keyword_search.clear_index()
    
    def get_document_count(self) -> int:
        if self.semantic_search:
            return self.semantic_search.get_document_count()
        return 0