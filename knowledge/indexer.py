#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TurboMind AI - File Indexer
============================
Indexes files for knowledge base
"""

from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
import time
import json
import os


@dataclass
class IndexedFile:
    """Represents an indexed file"""
    file_path: str
    file_name: str
    file_type: str
    file_size: int
    chunks: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    indexed_at: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'file_path': self.file_path,
            'file_name': self.file_name,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'chunks': self.chunks,
            'metadata': self.metadata,
            'indexed_at': self.indexed_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'IndexedFile':
        """Create from dictionary"""
        return cls(
            file_path=data.get('file_path', ''),
            file_name=data.get('file_name', ''),
            file_type=data.get('file_type', ''),
            file_size=data.get('file_size', 0),
            chunks=data.get('chunks', []),
            metadata=data.get('metadata', {}),
            indexed_at=data.get('indexed_at', time.time())
        )


@dataclass
class IndexingProgress:
    """Represents indexing progress"""
    total_files: int
    processed_files: int
    current_file: str
    status: str
    start_time: float
    estimated_time_remaining: float = 0
    
    @property
    def progress_percent(self) -> float:
        """Calculate progress percentage"""
        return (self.processed_files / self.total_files * 100) if self.total_files > 0 else 0
    
    @property
    def elapsed_time(self) -> float:
        """Calculate elapsed time"""
        return time.time() - self.start_time


class FileIndexer:
    """
    Indexes files for the knowledge base.
    Handles chunking, embedding, and storing file content.
    """
    
    def __init__(self, knowledge_base=None):
        """
        Initialize the file indexer.
        
        Args:
            knowledge_base: Optional KnowledgeBase instance
        """
        self.knowledge_base = knowledge_base
        self.indexed_files: Dict[str, IndexedFile] = {}
        self.supported_extensions = ['.pdf', '.docx', '.txt', '.md', '.html', '.csv', '.xlsx', '.pptx']
        
        print("📁 File Indexer initialized")
    
    def index_file(self, file_path: str, silo_id: Optional[str] = None) -> Optional[IndexedFile]:
        """
        Index a single file.
        
        Args:
            file_path: Path to the file
            silo_id: Silo to add to
            
        Returns:
            IndexedFile or None if failed
        """
        file_path_obj = Path(file_path)
        
        if not file_path_obj.exists():
            print(f"❌ File not found: {file_path}")
            return None
        
        # Check if already indexed
        file_key = str(file_path_obj.resolve())
        if file_key in self.indexed_files:
            print(f"ℹ️  File already indexed: {file_path}")
            return self.indexed_files[file_key]
        
        # Process file
        from documents.document_processor import DocumentProcessor
        
        processor = DocumentProcessor()
        processed = processor.process(file_path)
        
        if not processed:
            print(f"❌ Failed to process file: {file_path}")
            return None
        
        # Create indexed file
        indexed_file = IndexedFile(
            file_path=file_key,
            file_name=file_path_obj.name,
            file_type=processed.metadata.file_type.value,
            file_size=processed.metadata.file_size,
            chunks=[
                {
                    'chunk_id': chunk.chunk_id,
                    'text': chunk.text,
                    'metadata': chunk.metadata
                }
                for chunk in processed.chunks
            ],
            metadata={
                'page_count': processed.metadata.page_count,
                'word_count': processed.metadata.word_count,
                'char_count': processed.metadata.char_count,
                'created_at': processed.metadata.created_at,
                'modified_at': processed.metadata.modified_at
            }
        )
        
        # Add to knowledge base
        if self.knowledge_base:
            for chunk in processed.chunks:
                self.knowledge_base.add_item(
                    title=f"{processed.metadata.file_name} - Chunk {chunk.chunk_id}",
                    content=chunk.text,
                    source=file_path,
                    source_type='file_chunk',
                    tags=[processed.metadata.file_type.value, f"chunk_{chunk.chunk_id}"],
                    category='document_chunk',
                    silo_id=silo_id,
                    metadata={
                        'file_id': file_key,
                        'file_name': processed.metadata.file_name,
                        'chunk_id': chunk.chunk_id,
                        'page': chunk.metadata.get('start_page', 0)
                    }
                )
        
        # Store indexed file
        self.indexed_files[file_key] = indexed_file
        
        print(f"✅ Indexed file: {file_path}")
        return indexed_file
    
    def index_directory(self, directory_path: str, silo_id: Optional[str] = None) -> IndexingProgress:
        """
        Index all files in a directory.
        
        Args:
            directory_path: Path to the directory
            silo_id: Silo to add to
            
        Returns:
            IndexingProgress object
        """
        directory_path_obj = Path(directory_path)
        
        if not directory_path_obj.exists():
            raise FileNotFoundError(f"Directory not found: {directory_path}")
        
        # Find all supported files
        files = []
        for ext in self.supported_extensions:
            files.extend(directory_path_obj.glob(f"**/*{ext}"))
        
        files = [f for f in files if f.is_file()]
        
        progress = IndexingProgress(
            total_files=len(files),
            processed_files=0,
            current_file="",
            status="starting",
            start_time=time.time()
        )
        
        for i, file_path in enumerate(files):
            progress.current_file = str(file_path)
            progress.processed_files = i
            progress.status = f"Processing {file_path.name}"
            
            # Estimate time remaining
            if i > 0:
                avg_time = progress.elapsed_time / i
                progress.estimated_time_remaining = avg_time * (len(files) - i)
            
            try:
                self.index_file(str(file_path), silo_id)
            except Exception as e:
                print(f"⚠️  Error indexing {file_path}: {e}")
            
            # Yield progress (for streaming)
            yield progress
        
        progress.processed_files = len(files)
        progress.status = "complete"
        yield progress
    
    def reindex_file(self, file_path: str) -> Optional[IndexedFile]:
        """
        Re-index a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            IndexedFile or None if failed
        """
        # Remove from index
        file_key = str(Path(file_path).resolve())
        if file_key in self.indexed_files:
            del self.indexed_files[file_key]
        
        # Re-index
        return self.index_file(file_path)
    
    def delete_from_index(self, file_path: str) -> bool:
        """
        Delete a file from the index.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if deleted
        """
        file_key = str(Path(file_path).resolve())
        
        if file_key in self.indexed_files:
            del self.indexed_files[file_key]
            print(f"🗑️  Deleted from index: {file_path}")
            return True
        
        return False
    
    def get_indexed_file(self, file_path: str) -> Optional[IndexedFile]:
        """Get an indexed file by path"""
        file_key = str(Path(file_path).resolve())
        return self.indexed_files.get(file_key)
    
    def get_all_indexed_files(self) -> List[IndexedFile]:
        """Get all indexed files"""
        return list(self.indexed_files.values())
    
    def is_indexed(self, file_path: str) -> bool:
        """Check if a file is already indexed"""
        file_key = str(Path(file_path).resolve())
        return file_key in self.indexed_files
    
    def get_index_stats(self) -> Dict[str, Any]:
        """Get indexing statistics"""
        return {
            'total_files': len(self.indexed_files),
            'total_chunks': sum(len(f.chunks) for f in self.indexed_files.values()),
            'total_size': sum(f.file_size for f in self.indexed_files.values()),
            'supported_extensions': self.supported_extensions
        }
    
    def clear_index(self):
        """Clear all indexed files"""
        self.indexed_files.clear()
        print("🧹 File index cleared")
    
    def save_index(self, output_path: str) -> bool:
        """Save index to a file"""
        try:
            output_file = Path(output_path)
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(
                    [f.to_dict() for f in self.indexed_files.values()],
                    f,
                    indent=2
                )
            
            print(f"💾 Index saved to {output_path}")
            return True
        except Exception as e:
            print(f"❌ Save failed: {e}")
            return False
    
    def load_index(self, input_path: str) -> bool:
        """Load index from a file"""
        try:
            input_file = Path(input_path)
            with open(input_file, 'r', encoding='utf-8') as f:
                files_data = json.load(f)
            
            for file_data in files_data:
                indexed_file = IndexedFile.from_dict(file_data)
                self.indexed_files[indexed_file.file_path] = indexed_file
            
            print(f"📥 Index loaded from {input_path}")
            return True
        except Exception as e:
            print(f"❌ Load failed: {e}")
            return False
    
    def search_index(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search the index for files matching the query.
        
        Args:
            query: Search query
            limit: Maximum results
            
        Returns:
            List of matching files
        """
        if not self.knowledge_base:
            return []
        
        # Search knowledge base
        results = self.knowledge_base.search_items(query, limit)
        
        # Group by file
        file_results = {}
        for item in results:
            file_path = item.metadata.get('file_path', '')
            if file_path and file_path not in file_results:
                file_results[file_path] = {
                    'file_path': file_path,
                    'file_name': item.metadata.get('file_name', ''),
                    'match_count': 0,
                    'items': []
                }
            if file_path:
                file_results[file_path]['match_count'] += 1
                file_results[file_path]['items'].append(item)
        
        # Sort by match count
        sorted_results = sorted(
            file_results.values(),
            key=lambda x: x['match_count'],
            reverse=True
        )
        
        return sorted_results[:limit]
    
    def get_supported_extensions(self) -> List[str]:
        """Get list of supported file extensions"""
        return self.supported_extensions.copy()
    
    def add_supported_extension(self, extension: str) -> None:
        """Add a supported file extension"""
        if extension not in self.supported_extensions:
            self.supported_extensions.append(extension)
