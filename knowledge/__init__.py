# TurboMind AI - Knowledge Base Package
# =====================================

"""
Knowledge Base Package for TurboMind AI.
Handles personal knowledge management, vector storage, and semantic search.

Features:
- Local Knowledge Graph
- Vector Embeddings Store
- File Indexing (PDF, DOCX, TXT, Markdown)
- Semantic Search
- Knowledge Silos
- Auto-Indexing
- Neural Graph Visualization
"""

from .knowledge_base import KnowledgeBase
from .vector_store import VectorStore
from .indexer import FileIndexer
from .graph import KnowledgeGraph

__all__ = [
    'KnowledgeBase',
    'VectorStore',
    'FileIndexer',
    'KnowledgeGraph'
]
__version__ = '1.0.0'
