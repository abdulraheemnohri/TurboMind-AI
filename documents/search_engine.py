#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TurboMind AI - Document Search Engine
=====================================
Handles keyword and semantic search in documents
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
import re
from collections import defaultdict
import numpy as np


@dataclass
class SearchResult:
    """Represents a search result"""
    document_id: str
    document_name: str
    score: float
    snippet: str
    section: str = ""
    page: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SearchQuery:
    """Represents a search query"""
    query: str
    filters: Dict[str, Any] = field(default_factory=dict)
    limit: int = 10
    offset: int = 0
    
    def __post_init__(self):
        if not self.filters:
            self.filters = {}


class DocumentSearchEngine:
    """
    Search engine for documents.
    Supports both keyword-based and semantic search.
    """
    
    def __init__(self):
        """Initialize the search engine"""
        # Inverted index for keyword search
        self.inverted_index: Dict[str, Dict[str, List[int]]] = defaultdict(lambda: defaultdict(list))
        
        # Document store
        self.documents: Dict[str, Dict[str, Any]] = {}
        
        # Embeddings for semantic search (would be populated with actual embeddings)
        self.embeddings: Dict[str, np.ndarray] = {}
        
        # Token frequency
        self.token_freq: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        
        # Document frequency
        self.doc_freq: Dict[str, int] = defaultdict(int)
        
        print("🔍 Document Search Engine initialized")
    
    def add_document(self, document_id: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Add a document to the search index.
        
        Args:
            document_id: Unique identifier for the document
            content: Text content of the document
            metadata: Optional metadata (name, type, etc.)
        """
        if metadata is None:
            metadata = {}
        
        # Store document
        self.documents[document_id] = {
            'content': content,
            'metadata': metadata
        }
        
        # Tokenize content
        tokens = self._tokenize(content)
        
        # Update inverted index
        for token in tokens:
            self.inverted_index[token][document_id].append(len(self.inverted_index[token][document_id]))
            self.token_freq[document_id][token] += 1
            self.doc_freq[token] += 1
        
        print(f"📄 Added document: {document_id}")
    
    def remove_document(self, document_id: str) -> bool:
        """Remove a document from the search index"""
        if document_id not in self.documents:
            return False
        
        # Remove from inverted index
        for token, docs in self.inverted_index.items():
            if document_id in docs:
                del docs[document_id]
                if not docs:
                    del self.inverted_index[token]
        
        # Remove from token frequency
        if document_id in self.token_freq:
            del self.token_freq[document_id]
        
        # Remove from embeddings
        if document_id in self.embeddings:
            del self.embeddings[document_id]
        
        # Remove from documents
        del self.documents[document_id]
        
        print(f"🗑️  Removed document: {document_id}")
        return True
    
    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text into words/tokens"""
        # Simple tokenization
        text = text.lower()
        tokens = re.findall(r'[\w\-]+', text)
        return tokens
    
    def keyword_search(self, query: Union[str, SearchQuery]) -> List[SearchResult]:
        """
        Perform keyword-based search.
        
        Args:
            query: Search query (string or SearchQuery object)
            
        Returns:
            List of SearchResult objects
        """
        if isinstance(query, str):
            query = SearchQuery(query=query)
        
        # Tokenize query
        query_tokens = self._tokenize(query.query)
        
        if not query_tokens:
            return []
        
        # Get documents containing all query tokens (AND search)
        matching_docs = None
        for token in query_tokens:
            if token not in self.inverted_index:
                return []  # Token not found
            
            if matching_docs is None:
                matching_docs = set(self.inverted_index[token].keys())
            else:
                matching_docs &= set(self.inverted_index[token].keys())
        
        if not matching_docs:
            return []
        
        # Score documents
        results = []
        for doc_id in matching_docs:
            score = self._score_document(doc_id, query_tokens)
            
            # Get snippet
            snippet = self._get_snippet(self.documents[doc_id]['content'], query_tokens)
            
            results.append(SearchResult(
                document_id=doc_id,
                document_name=self.documents[doc_id]['metadata'].get('name', doc_id),
                score=score,
                snippet=snippet,
                metadata=self.documents[doc_id]['metadata']
            ))
        
        # Sort by score
        results.sort(key=lambda r: r.score, reverse=True)
        
        return results[:query.limit]
    
    def _score_document(self, document_id: str, query_tokens: List[str]) -> float:
        """Calculate score for a document based on query tokens"""
        score = 0.0
        
        # TF-IDF scoring
        for token in query_tokens:
            if token in self.token_freq[document_id]:
                tf = self.token_freq[document_id][token]
                idf = np.log(len(self.documents) / (1 + self.doc_freq[token])) if self.doc_freq[token] > 0 else 0
                score += tf * idf
        
        return score
    
    def _get_snippet(self, content: str, query_tokens: List[str], max_length: int = 200) -> str:
        """Extract a snippet containing query tokens"""
        # Find positions of query tokens
        positions = []
        for token in query_tokens:
            for match in re.finditer(r'\b' + re.escape(token) + r'\b', content, re.IGNORECASE):
                positions.append(match.start())
        
        if not positions:
            return content[:max_length] + "..."
        
        # Find the best position (with most tokens nearby)
        positions.sort()
        
        # Try to find a window containing multiple query tokens
        best_start = 0
        best_score = 0
        
        for i, pos in enumerate(positions):
            # Count how many query tokens are nearby
            nearby = sum(1 for p in positions if abs(p - pos) < max_length)
            if nearby > best_score:
                best_score = nearby
                best_start = max(0, pos - max_length // 2)
        
        # Extract snippet
        snippet = content[best_start:best_start + max_length]
        
        # Add ellipsis if truncated
        if best_start > 0:
            snippet = "..." + snippet
        if best_start + max_length < len(content):
            snippet = snippet + "..."
        
        return snippet
    
    def semantic_search(self, query: Union[str, SearchQuery], embeddings: Optional[Dict[str, np.ndarray]] = None) -> List[SearchResult]:
        """
        Perform semantic search using embeddings.
        
        Args:
            query: Search query
            embeddings: Optional embeddings dictionary
            
        Returns:
            List of SearchResult objects
        """
        if isinstance(query, str):
            query = SearchQuery(query=query)
        
        # For demo, fall back to keyword search
        # In production, would use actual embeddings
        return self.keyword_search(query)
    
    def hybrid_search(self, query: Union[str, SearchQuery]) -> List[SearchResult]:
        """
        Perform hybrid search (keyword + semantic).
        
        Args:
            query: Search query
            
        Returns:
            List of SearchResult objects
        """
        # For demo, just use keyword search
        return self.keyword_search(query)
    
    def search(self, query: Union[str, SearchQuery], method: str = "keyword") -> List[SearchResult]:
        """
        Perform search using specified method.
        
        Args:
            query: Search query
            method: Search method ('keyword', 'semantic', 'hybrid')
            
        Returns:
            List of SearchResult objects
        """
        if method == "keyword":
            return self.keyword_search(query)
        elif method == "semantic":
            return self.semantic_search(query)
        else:  # hybrid
            return self.hybrid_search(query)
    
    def advanced_search(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        method: str = "keyword",
        limit: int = 10
    ) -> List[SearchResult]:
        """
        Perform advanced search with filters.
        
        Args:
            query: Search query
            filters: Filter criteria
            method: Search method
            limit: Maximum results
            
        Returns:
            List of SearchResult objects
        """
        search_query = SearchQuery(
            query=query,
            filters=filters or {},
            limit=limit
        )
        
        results = self.search(search_query, method)
        
        # Apply filters
        if filters:
            filtered_results = []
            for result in results:
                match = True
                for key, value in filters.items():
                    if key in result.metadata:
                        if result.metadata[key] != value:
                            match = False
                            break
                if match:
                    filtered_results.append(result)
            results = filtered_results
        
        return results[:limit]
    
    def get_suggestions(self, query: str, limit: int = 5) -> List[str]:
        """
        Get search suggestions for a query.
        
        Args:
            query: Partial query
            limit: Maximum suggestions
            
        Returns:
            List of suggestion strings
        """
        # Tokenize query
        query_tokens = self._tokenize(query)
        
        if not query_tokens:
            return []
        
        # Find tokens that start with the last query token
        last_token = query_tokens[-1]
        suggestions = []
        
        for token in self.inverted_index.keys():
            if token.startswith(last_token):
                suggestions.append(token)
        
        return suggestions[:limit]
    
    def clear_index(self) -> None:
        """Clear the entire search index"""
        self.inverted_index.clear()
        self.documents.clear()
        self.embeddings.clear()
        self.token_freq.clear()
        self.doc_freq.clear()
        
        print("🧹 Search index cleared")
    
    def get_index_stats(self) -> Dict[str, Any]:
        """Get statistics about the search index"""
        return {
            'document_count': len(self.documents),
            'unique_tokens': len(self.inverted_index),
            'total_occurrences': sum(len(docs) for docs in self.inverted_index.values()),
            'embedding_count': len(self.embeddings)
        }
    
    def add_embedding(self, document_id: str, embedding: np.ndarray) -> None:
        """Add embedding for a document"""
        self.embeddings[document_id] = embedding
    
    def get_embedding(self, document_id: str) -> Optional[np.ndarray]:
        """Get embedding for a document"""
        return self.embeddings.get(document_id)
