#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TurboMind AI - Knowledge Base
=============================
Main knowledge base class for managing personal knowledge
"""

from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
import time
import json
import hashlib


@dataclass
class KnowledgeItem:
    """Represents a single piece of knowledge"""
    id: str
    title: str
    content: str
    source: str  # file path or URL
    source_type: str  # 'file', 'text', 'web'
    tags: List[str] = field(default_factory=list)
    category: str = "general"
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'source': self.source,
            'source_type': self.source_type,
            'tags': self.tags,
            'category': self.category,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'embedding': self.embedding,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'KnowledgeItem':
        """Create from dictionary"""
        return cls(
            id=data.get('id', ''),
            title=data.get('title', ''),
            content=data.get('content', ''),
            source=data.get('source', ''),
            source_type=data.get('source_type', 'text'),
            tags=data.get('tags', []),
            category=data.get('category', 'general'),
            created_at=data.get('created_at', time.time()),
            updated_at=data.get('updated_at', time.time()),
            embedding=data.get('embedding'),
            metadata=data.get('metadata', {})
        )


@dataclass
class KnowledgeSilo:
    """Represents a knowledge silo (collection of related knowledge)"""
    id: str
    name: str
    description: str = ""
    color: str = "#2196F3"
    icon: str = "folder"
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    item_count: int = 0
    size_bytes: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'color': self.color,
            'icon': self.icon,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'item_count': self.item_count,
            'size_bytes': self.size_bytes
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'KnowledgeSilo':
        """Create from dictionary"""
        return cls(
            id=data.get('id', ''),
            name=data.get('name', ''),
            description=data.get('description', ''),
            color=data.get('color', '#2196F3'),
            icon=data.get('icon', 'folder'),
            created_at=data.get('created_at', time.time()),
            updated_at=data.get('updated_at', time.time()),
            item_count=data.get('item_count', 0),
            size_bytes=data.get('size_bytes', 0)
        )


class KnowledgeBase:
    """
    Main knowledge base class.
    Manages personal knowledge, silos, and indexing.
    """
    
    def __init__(self, storage_path: str = "knowledge_base"):
        """
        Initialize the knowledge base.
        
        Args:
            storage_path: Path to store knowledge data
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Knowledge items
        self.items: Dict[str, KnowledgeItem] = {}
        
        # Knowledge silos
        self.silos: Dict[str, KnowledgeSilo] = {}
        
        # Index
        self.index: Dict[str, List[str]] = {}  # token -> [item_ids]
        
        # Vector store
        self.vector_store = None
        
        # Stats
        self.stats = {
            'total_items': 0,
            'total_silos': 0,
            'total_size': 0,
            'indexed_items': 0,
            'last_updated': 0
        }
        
        # Initialize components
        self._init_vector_store()
        self._load_data()
        
        print(f"🧠 Knowledge Base initialized at {storage_path}")
    
    def _init_vector_store(self):
        """Initialize vector store"""
        try:
            from .vector_store import VectorStore
            self.vector_store = VectorStore(str(self.storage_path / "vectors"))
        except Exception as e:
            print(f"⚠️  Could not initialize vector store: {e}")
            self.vector_store = None
    
    def _load_data(self):
        """Load knowledge base data from storage"""
        # Load items
        items_file = self.storage_path / "items.json"
        if items_file.exists():
            with open(items_file, 'r', encoding='utf-8') as f:
                items_data = json.load(f)
            
            for item_data in items_data:
                item = KnowledgeItem.from_dict(item_data)
                self.items[item.id] = item
            
            self.stats['total_items'] = len(self.items)
        
        # Load silos
        silos_file = self.storage_path / "silos.json"
        if silos_file.exists():
            with open(silos_file, 'r', encoding='utf-8') as f:
                silos_data = json.load(f)
            
            for silo_data in silos_data:
                silo = KnowledgeSilo.from_dict(silo_data)
                self.silos[silo.id] = silo
            
            self.stats['total_silos'] = len(self.silos)
        
        # Load index
        index_file = self.storage_path / "index.json"
        if index_file.exists():
            with open(index_file, 'r', encoding='utf-8') as f:
                self.index = json.load(f)
        
        print(f"📂 Loaded {self.stats['total_items']} items, {self.stats['total_silos']} silos")
    
    def save(self):
        """Save knowledge base data to storage"""
        # Save items
        items_file = self.storage_path / "items.json"
        with open(items_file, 'w', encoding='utf-8') as f:
            json.dump([item.to_dict() for item in self.items.values()], f, indent=2)
        
        # Save silos
        silos_file = self.storage_path / "silos.json"
        with open(silos_file, 'w', encoding='utf-8') as f:
            json.dump([silo.to_dict() for silo in self.silos.values()], f, indent=2)
        
        # Save index
        index_file = self.storage_path / "index.json"
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(self.index, f, indent=2)
        
        print(f"💾 Knowledge base saved")
    
    def _generate_id(self) -> str:
        """Generate a unique ID"""
        return hashlib.sha256(str(time.time()).encode()).hexdigest()[:16]
    
    # ==================== KNOWLEDGE ITEMS ====================
    
    def add_item(
        self,
        title: str,
        content: str,
        source: str = "",
        source_type: str = "text",
        tags: Optional[List[str]] = None,
        category: str = "general",
        silo_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> KnowledgeItem:
        """
        Add a knowledge item to the knowledge base.
        
        Args:
            title: Title of the knowledge item
            content: Content of the knowledge item
            source: Source of the knowledge
            source_type: Type of source
            tags: List of tags
            category: Category
            silo_id: Silo to add to
            metadata: Additional metadata
            
        Returns:
            The created KnowledgeItem
        """
        item_id = self._generate_id()
        
        item = KnowledgeItem(
            id=item_id,
            title=title,
            content=content,
            source=source,
            source_type=source_type,
            tags=tags or [],
            category=category,
            metadata=metadata or {}
        )
        
        self.items[item_id] = item
        self.stats['total_items'] += 1
        self.stats['total_size'] += len(content.encode('utf-8'))
        
        # Add to silo if specified
        if silo_id and silo_id in self.silos:
            self.silos[silo_id].item_count += 1
            self.silos[silo_id].size_bytes += len(content.encode('utf-8'))
            self.silos[silo_id].updated_at = time.time()
        
        # Index the item
        self._index_item(item)
        
        # Generate embedding
        if self.vector_store:
            embedding = self.vector_store.generate_embedding(content)
            item.embedding = embedding.tolist() if hasattr(embedding, 'tolist') else embedding
        
        self.stats['last_updated'] = time.time()
        
        print(f"🆕 Added knowledge item: {title}")
        return item
    
    def update_item(self, item_id: str, **kwargs) -> Optional[KnowledgeItem]:
        """Update a knowledge item"""
        if item_id not in self.items:
            return None
        
        item = self.items[item_id]
        
        for key, value in kwargs.items():
            if hasattr(item, key):
                setattr(item, key, value)
        
        item.updated_at = time.time()
        
        # Re-index if content changed
        if 'content' in kwargs:
            self._remove_from_index(item)
            self._index_item(item)
        
        self.stats['last_updated'] = time.time()
        
        print(f"🔄 Updated knowledge item: {item.title}")
        return item
    
    def delete_item(self, item_id: str) -> bool:
        """Delete a knowledge item"""
        if item_id not in self.items:
            return False
        
        item = self.items[item_id]
        
        # Remove from index
        self._remove_from_index(item)
        
        # Remove from silo
        for silo in self.silos.values():
            # In a real implementation, would track which silo the item belongs to
            pass
        
        del self.items[item_id]
        self.stats['total_items'] -= 1
        self.stats['total_size'] -= len(item.content.encode('utf-8'))
        self.stats['last_updated'] = time.time()
        
        print(f"🗑️  Deleted knowledge item: {item.title}")
        return True
    
    def get_item(self, item_id: str) -> Optional[KnowledgeItem]:
        """Get a knowledge item by ID"""
        return self.items.get(item_id)
    
    def search_items(self, query: str, limit: int = 10) -> List[KnowledgeItem]:
        """
        Search knowledge items by query.
        
        Args:
            query: Search query
            limit: Maximum results
            
        Returns:
            List of matching KnowledgeItems
        """
        results = []
        
        # Tokenize query
        query_tokens = self._tokenize(query)
        
        # Find items matching all tokens
        matching_ids = None
        for token in query_tokens:
            if token not in self.index:
                return []
            
            if matching_ids is None:
                matching_ids = set(self.index[token])
            else:
                matching_ids &= set(self.index[token])
        
        if not matching_ids:
            return []
        
        # Get items and sort by relevance
        for item_id in matching_ids:
            if item_id in self.items:
                item = self.items[item_id]
                score = self._calculate_score(item, query_tokens)
                results.append((score, item))
        
        # Sort by score
        results.sort(key=lambda x: x[0], reverse=True)
        
        return [r[1] for r in results[:limit]]
    
    def semantic_search(self, query: str, limit: int = 10) -> List[KnowledgeItem]:
        """
        Perform semantic search using embeddings.
        
        Args:
            query: Search query
            limit: Maximum results
            
        Returns:
            List of matching KnowledgeItems
        """
        if not self.vector_store:
            return self.search_items(query, limit)
        
        # Generate query embedding
        query_embedding = self.vector_store.generate_embedding(query)
        
        # Find similar items
        results = []
        for item in self.items.values():
            if item.embedding:
                similarity = self.vector_store.calculate_similarity(
                    query_embedding, item.embedding
                )
                results.append((similarity, item))
        
        # Sort by similarity
        results.sort(key=lambda x: x[0], reverse=True)
        
        return [r[1] for r in results[:limit]]
    
    # ==================== KNOWLEDGE SILOS ====================
    
    def create_silo(
        self,
        name: str,
        description: str = "",
        color: str = "#2196F3",
        icon: str = "folder"
    ) -> KnowledgeSilo:
        """
        Create a new knowledge silo.
        
        Args:
            name: Name of the silo
            description: Description
            color: Color for the silo
            icon: Icon for the silo
            
        Returns:
            The created KnowledgeSilo
        """
        silo_id = self._generate_id()
        
        silo = KnowledgeSilo(
            id=silo_id,
            name=name,
            description=description,
            color=color,
            icon=icon
        )
        
        self.silos[silo_id] = silo
        self.stats['total_silos'] += 1
        self.stats['last_updated'] = time.time()
        
        print(f"📁 Created silo: {name}")
        return silo
    
    def delete_silo(self, silo_id: str) -> bool:
        """Delete a knowledge silo"""
        if silo_id not in self.silos:
            return False
        
        silo = self.silos[silo_id]
        
        # Delete all items in the silo
        # In a real implementation, would track which items belong to which silo
        
        del self.silos[silo_id]
        self.stats['total_silos'] -= 1
        self.stats['last_updated'] = time.time()
        
        print(f"🗑️  Deleted silo: {silo.name}")
        return True
    
    def get_silo(self, silo_id: str) -> Optional[KnowledgeSilo]:
        """Get a knowledge silo by ID"""
        return self.silos.get(silo_id)
    
    def get_items_in_silo(self, silo_id: str) -> List[KnowledgeItem]:
        """Get all items in a silo"""
        # In a real implementation, would track which items belong to which silo
        # For now, return all items
        return list(self.items.values())
    
    # ==================== INDEXING ====================
    
    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text into words"""
        import re
        return re.findall(r'[\w\-]+', text.lower())
    
    def _index_item(self, item: KnowledgeItem):
        """Index a knowledge item"""
        tokens = self._tokenize(item.title) + self._tokenize(item.content)
        
        for token in set(tokens):
            if token not in self.index:
                self.index[token] = []
            if item.id not in self.index[token]:
                self.index[token].append(item.id)
    
    def _remove_from_index(self, item: KnowledgeItem):
        """Remove an item from the index"""
        tokens = self._tokenize(item.title) + self._tokenize(item.content)
        
        for token in tokens:
            if token in self.index and item.id in self.index[token]:
                self.index[token].remove(item.id)
                if not self.index[token]:
                    del self.index[token]
    
    def _calculate_score(self, item: KnowledgeItem, query_tokens: List[str]) -> float:
        """Calculate relevance score for an item"""
        score = 0.0
        
        # Title match bonus
        title_tokens = self._tokenize(item.title)
        for token in query_tokens:
            if token in title_tokens:
                score += 2.0
        
        # Content match
        content_tokens = self._tokenize(item.content)
        for token in query_tokens:
            if token in content_tokens:
                score += 1.0
        
        # Tag match bonus
        for token in query_tokens:
            if token in [t.lower() for t in item.tags]:
                score += 1.5
        
        return score
    
    # ==================== FILE IMPORT ====================
    
    def import_file(self, file_path: str, silo_id: Optional[str] = None) -> Optional[KnowledgeItem]:
        """
        Import a file into the knowledge base.
        
        Args:
            file_path: Path to the file
            silo_id: Silo to add to
            
        Returns:
            The created KnowledgeItem
        """
        from documents.document_processor import DocumentProcessor
        
        processor = DocumentProcessor()
        processed = processor.process(file_path)
        
        if not processed:
            return None
        
        # Create knowledge item
        item = self.add_item(
            title=processed.metadata.file_name,
            content=processed.content,
            source=file_path,
            source_type='file',
            tags=[processed.metadata.file_type.value],
            category='document',
            silo_id=silo_id,
            metadata={
                'file_type': processed.metadata.file_type.value,
                'file_size': processed.metadata.file_size,
                'page_count': processed.metadata.page_count,
                'word_count': processed.metadata.word_count
            }
        )
        
        return item
    
    def import_text(self, text: str, title: str = "Untitled", silo_id: Optional[str] = None) -> KnowledgeItem:
        """
        Import text into the knowledge base.
        
        Args:
            text: Text to import
            title: Title for the knowledge item
            silo_id: Silo to add to
            
        Returns:
            The created KnowledgeItem
        """
        return self.add_item(
            title=title,
            content=text,
            source_type='text',
            silo_id=silo_id
        )
    
    # ==================== STATS & INFO ====================
    
    def get_stats(self) -> Dict[str, Any]:
        """Get knowledge base statistics"""
        return {
            **self.stats,
            'silo_stats': {
                silo_id: {
                    'name': silo.name,
                    'item_count': silo.item_count,
                    'size_mb': silo.size_bytes / (1024 * 1024)
                }
                for silo_id, silo in self.silos.items()
            }
        }
    
    def get_all_items(self) -> List[KnowledgeItem]:
        """Get all knowledge items"""
        return list(self.items.values())
    
    def get_all_silos(self) -> List[KnowledgeSilo]:
        """Get all knowledge silos"""
        return list(self.silos.values())
    
    def clear(self):
        """Clear the entire knowledge base"""
        self.items.clear()
        self.silos.clear()
        self.index.clear()
        self.stats = {
            'total_items': 0,
            'total_silos': 0,
            'total_size': 0,
            'indexed_items': 0,
            'last_updated': 0
        }
        
        # Clear vector store
        if self.vector_store:
            self.vector_store.clear()
        
        print("🧹 Knowledge base cleared")
    
    def backup(self, backup_path: str) -> bool:
        """Create a backup of the knowledge base"""
        import shutil
        
        try:
            backup_dir = Path(backup_path)
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy storage directory
            shutil.copytree(self.storage_path, backup_dir / "knowledge_base")
            
            print(f"💾 Backup created at {backup_path}")
            return True
        except Exception as e:
            print(f"❌ Backup failed: {e}")
            return False
    
    def restore(self, backup_path: str) -> bool:
        """Restore knowledge base from backup"""
        import shutil
        
        try:
            backup_dir = Path(backup_path) / "knowledge_base"
            if backup_dir.exists():
                # Clear current data
                self.clear()
                
                # Remove current storage
                if self.storage_path.exists():
                    shutil.rmtree(self.storage_path)
                
                # Copy backup
                shutil.copytree(backup_dir, self.storage_path)
                
                # Reload data
                self._load_data()
                
                print(f"🔄 Knowledge base restored from {backup_path}")
                return True
        except Exception as e:
            print(f"❌ Restore failed: {e}")
            return False
