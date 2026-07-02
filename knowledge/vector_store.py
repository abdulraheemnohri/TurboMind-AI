#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TurboMind AI - Vector Store
============================
Stores and retrieves vector embeddings for semantic search
"""

from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass, field
import numpy as np
import json
import time
import hashlib


@dataclass
class VectorEntry:
    """A vector embedding entry"""
    id: str
    vector: np.ndarray
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'vector': self.vector.tolist(),
            'metadata': self.metadata,
            'timestamp': self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VectorEntry':
        """Create from dictionary"""
        return cls(
            id=data.get('id', ''),
            vector=np.array(data.get('vector', [])),
            metadata=data.get('metadata', {}),
            timestamp=data.get('timestamp', time.time())
        )


class VectorStore:
    """
    Stores vector embeddings for semantic search.
    Supports efficient similarity search and indexing.
    """
    
    def __init__(self, storage_path: str = "vector_store"):
        """
        Initialize the vector store.
        
        Args:
            storage_path: Path to store vector data
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Vector entries
        self.entries: Dict[str, VectorEntry] = {}
        
        # Index for fast search
        self.index: Dict[str, List[str]] = {}  # For filtering by metadata
        
        # Embedding model
        self.embedding_model = None
        self._init_embedding_model()
        
        # Stats
        self.stats = {
            'total_vectors': 0,
            'dimension': 0,
            'last_updated': 0
        }
        
        # Load existing data
        self._load_data()
        
        print(f"📊 Vector Store initialized at {storage_path}")
    
    def _init_embedding_model(self):
        """Initialize embedding model"""
        try:
            # Try to use Sentence Transformers
            from sentence_transformers import SentenceTransformer
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            self.stats['dimension'] = 384  # Dimension of all-MiniLM-L6-v2
            print("✅ Sentence Transformers model loaded")
        except ImportError:
            print("⚠️  Sentence Transformers not installed. Using mock embeddings.")
            self.embedding_model = None
            self.stats['dimension'] = 384  # Default dimension
    
    def _load_data(self):
        """Load vector data from storage"""
        vectors_file = self.storage_path / "vectors.json"
        if vectors_file.exists():
            with open(vectors_file, 'r', encoding='utf-8') as f:
                vectors_data = json.load(f)
            
            for entry_data in vectors_data:
                entry = VectorEntry.from_dict(entry_data)
                self.entries[entry.id] = entry
            
            self.stats['total_vectors'] = len(self.entries)
            print(f"📂 Loaded {self.stats['total_vectors']} vectors")
    
    def save(self):
        """Save vector data to storage"""
        vectors_file = self.storage_path / "vectors.json"
        with open(vectors_file, 'w', encoding='utf-8') as f:
            json.dump([entry.to_dict() for entry in self.entries.values()], f, indent=2)
        
        print(f"💾 Vector store saved")
    
    def _generate_id(self, text: str) -> str:
        """Generate a unique ID for text"""
        return hashlib.sha256(text.encode()).hexdigest()[:16]
    
    def generate_embedding(self, text: str) -> np.ndarray:
        """
        Generate an embedding vector for text.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector as numpy array
        """
        if self.embedding_model:
            return self.embedding_model.encode(text, convert_to_numpy=True)
        else:
            # Generate mock embedding
            return np.random.rand(self.stats['dimension']).astype(np.float32)
    
    def add_vector(
        self,
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
        vector: Optional[np.ndarray] = None
    ) -> str:
        """
        Add a vector to the store.
        
        Args:
            text: Text to embed
            metadata: Optional metadata
            vector: Optional pre-computed vector
            
        Returns:
            ID of the added vector
        """
        # Generate ID
        vector_id = self._generate_id(text)
        
        # Generate or use provided vector
        if vector is None:
            vector = self.generate_embedding(text)
        
        # Create entry
        entry = VectorEntry(
            id=vector_id,
            vector=vector,
            metadata=metadata or {}
        )
        
        self.entries[vector_id] = entry
        self.stats['total_vectors'] += 1
        self.stats['last_updated'] = time.time()
        
        # Update index
        for key, value in entry.metadata.items():
            if key not in self.index:
                self.index[key] = []
            if vector_id not in self.index[key]:
                self.index[key].append(vector_id)
        
        print(f"🆕 Added vector: {vector_id}")
        return vector_id
    
    def get_vector(self, vector_id: str) -> Optional[VectorEntry]:
        """Get a vector by ID"""
        return self.entries.get(vector_id)
    
    def delete_vector(self, vector_id: str) -> bool:
        """Delete a vector from the store"""
        if vector_id not in self.entries:
            return False
        
        # Remove from index
        entry = self.entries[vector_id]
        for key in entry.metadata.keys():
            if key in self.index and vector_id in self.index[key]:
                self.index[key].remove(vector_id)
                if not self.index[key]:
                    del self.index[key]
        
        del self.entries[vector_id]
        self.stats['total_vectors'] -= 1
        self.stats['last_updated'] = time.time()
        
        print(f"🗑️  Deleted vector: {vector_id}")
        return True
    
    def calculate_similarity(self, vec1: Union[np.ndarray, List], vec2: Union[np.ndarray, List]) -> float:
        """
        Calculate cosine similarity between two vectors.
        
        Args:
            vec1: First vector
            vec2: Second vector
            
        Returns:
            Similarity score (0-1)
        """
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        
        # Normalize vectors
        vec1_norm = vec1 / (np.linalg.norm(vec1) + 1e-8)
        vec2_norm = vec2 / (np.linalg.norm(vec2) + 1e-8)
        
        # Calculate cosine similarity
        similarity = np.dot(vec1_norm, vec2_norm)
        
        return float(similarity)
    
    def find_similar(
        self,
        query: Union[str, np.ndarray, List],
        limit: int = 10,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[float, VectorEntry]]:
        """
        Find vectors similar to the query.
        
        Args:
            query: Query text or vector
            limit: Maximum results
            filter_metadata: Optional metadata filter
            
        Returns:
            List of (similarity, VectorEntry) tuples
        """
        # Generate query vector if needed
        if isinstance(query, str):
            query_vector = self.generate_embedding(query)
        else:
            query_vector = np.array(query)
        
        # Calculate similarities
        results = []
        for entry in self.entries.values():
            similarity = self.calculate_similarity(query_vector, entry.vector)
            results.append((similarity, entry))
        
        # Sort by similarity
        results.sort(key=lambda x: x[0], reverse=True)
        
        # Apply metadata filter
        if filter_metadata:
            filtered_results = []
            for similarity, entry in results:
                match = True
                for key, value in filter_metadata.items():
                    if key not in entry.metadata or entry.metadata[key] != value:
                        match = False
                        break
                if match:
                    filtered_results.append((similarity, entry))
            results = filtered_results
        
        return results[:limit]
    
    def search(
        self,
        query: str,
        limit: int = 10,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar vectors.
        
        Args:
            query: Search query
            limit: Maximum results
            filter_metadata: Optional metadata filter
            
        Returns:
            List of result dictionaries
        """
        results = self.find_similar(query, limit, filter_metadata)
        
        return [
            {
                'id': entry.id,
                'similarity': similarity,
                'metadata': entry.metadata
            }
            for similarity, entry in results
        ]
    
    def batch_add(self, texts: List[str], metadatas: Optional[List[Dict[str, Any]]] = None) -> List[str]:
        """
        Add multiple vectors at once.
        
        Args:
            texts: List of texts to embed
            metadatas: Optional list of metadata dictionaries
            
        Returns:
            List of vector IDs
        """
        ids = []
        for i, text in enumerate(texts):
            metadata = metadatas[i] if metadatas and i < len(metadatas) else {}
            vector_id = self.add_vector(text, metadata)
            ids.append(vector_id)
        
        return ids
    
    def get_stats(self) -> Dict[str, Any]:
        """Get vector store statistics"""
        return {
            **self.stats,
            'index_keys': list(self.index.keys())
        }
    
    def clear(self):
        """Clear all vectors"""
        self.entries.clear()
        self.index.clear()
        self.stats = {
            'total_vectors': 0,
            'dimension': self.stats.get('dimension', 0),
            'last_updated': 0
        }
        
        print("🧹 Vector store cleared")
    
    def get_all_vectors(self) -> List[VectorEntry]:
        """Get all vector entries"""
        return list(self.entries.values())
    
    def export_vectors(self, output_path: str) -> bool:
        """Export vectors to a file"""
        try:
            output_file = Path(output_path)
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump([entry.to_dict() for entry in self.entries.values()], f, indent=2)
            
            print(f"📤 Vectors exported to {output_path}")
            return True
        except Exception as e:
            print(f"❌ Export failed: {e}")
            return False
    
    def import_vectors(self, input_path: str) -> bool:
        """Import vectors from a file"""
        try:
            input_file = Path(input_path)
            with open(input_file, 'r', encoding='utf-8') as f:
                vectors_data = json.load(f)
            
            for entry_data in vectors_data:
                entry = VectorEntry.from_dict(entry_data)
                self.entries[entry.id] = entry
            
            self.stats['total_vectors'] = len(self.entries)
            self.stats['last_updated'] = time.time()
            
            print(f"📥 Vectors imported from {input_path}")
            return True
        except Exception as e:
            print(f"❌ Import failed: {e}")
            return False
