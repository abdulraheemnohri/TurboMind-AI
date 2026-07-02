#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TurboMind AI - KV Cache Manager
===============================
Manages Key-Value cache for efficient inference
"""

from typing import Dict, Any, List, Optional, Tuple
import numpy as np
from dataclasses import dataclass, field
from collections import OrderedDict


@dataclass
class CacheEntry:
    """Represents a cache entry"""
    key: Tuple[int, ...]  # Token sequence as key
    value: Any  # Cached value (e.g., attention outputs)
    timestamp: float  # When it was cached
    size: int = 0  # Size in bytes (approximate)
    access_count: int = 0  # How many times accessed


class KVCacheManager:
    """
    Manages Key-Value cache for AI model inference.
    Caches attention keys and values to speed up decoding.
    """
    
    def __init__(self, max_size: int = 1024, max_entries: int = 1000):
        """
        Initialize the KV cache manager.
        
        Args:
            max_size: Maximum cache size in MB
            max_entries: Maximum number of cache entries
        """
        self.max_size = max_size * 1024 * 1024  # Convert to bytes
        self.max_entries = max_entries
        self.cache: Dict[Tuple[int, ...], CacheEntry] = {}
        self.current_size = 0
        self.hits = 0
        self.misses = 0
        self.access_order = OrderedDict()  # For LRU eviction
        
        print(f"💾 KV Cache Manager initialized (max: {max_size}MB, {max_entries} entries)")
    
    def get(self, key: Tuple[int, ...]) -> Optional[Any]:
        """
        Get a value from cache.
        
        Args:
            key: Token sequence key
            
        Returns:
            Cached value or None if not found
        """
        if key in self.cache:
            entry = self.cache[key]
            entry.access_count += 1
            
            # Update access order for LRU
            self.access_order.move_to_end(key)
            
            self.hits += 1
            return entry.value
        
        self.misses += 1
        return None
    
    def set(self, key: Tuple[int, ...], value: Any, size: Optional[int] = None) -> bool:
        """
        Set a value in cache.
        
        Args:
            key: Token sequence key
            value: Value to cache
            size: Size of the value in bytes (optional)
            
        Returns:
            True if cached successfully
        """
        # Calculate size if not provided
        if size is None:
            size = self._estimate_size(value)
        
        # Check if we need to evict entries
        while (self.current_size + size > self.max_size or 
               len(self.cache) >= self.max_entries) and self.cache:
            self._evict()
        
        # Add new entry
        entry = CacheEntry(
            key=key,
            value=value,
            timestamp=__import__('time').time(),
            size=size,
            access_count=1
        )
        
        self.cache[key] = entry
        self.access_order[key] = entry
        self.current_size += size
        
        return True
    
    def _evict(self) -> bool:
        """
        Evict the least recently used entry.
        
        Returns:
            True if an entry was evicted
        """
        if not self.cache:
            return False
        
        # Get LRU key
        lru_key, _ = self.access_order.popitem(last=False)
        
        # Remove from cache
        if lru_key in self.cache:
            entry = self.cache[lru_key]
            self.current_size -= entry.size
            del self.cache[lru_key]
            return True
        
        return False
    
    def _estimate_size(self, value: Any) -> int:
        """Estimate the size of a value in bytes"""
        if isinstance(value, np.ndarray):
            return value.nbytes
        elif isinstance(value, (list, tuple)):
            return sum(self._estimate_size(v) for v in value) + 8  # Overhead
        elif isinstance(value, dict):
            return sum(
                self._estimate_size(k) + self._estimate_size(v)
                for k, v in value.items()
            ) + 8
        elif isinstance(value, str):
            return len(value.encode('utf-8'))
        elif isinstance(value, (int, float)):
            return 8
        elif isinstance(value, bool):
            return 1
        else:
            return 16  # Default overhead
    
    def clear(self) -> None:
        """Clear the entire cache"""
        self.cache.clear()
        self.access_order.clear()
        self.current_size = 0
        self.hits = 0
        self.misses = 0
        print("🧹 KV Cache cleared")
    
    def clear_by_prefix(self, prefix: Tuple[int, ...]) -> int:
        """
        Clear cache entries that start with a specific prefix.
        
        Args:
            prefix: Token sequence prefix
            
        Returns:
            Number of entries cleared
        """
        prefix_len = len(prefix)
        keys_to_remove = [
            key for key in self.cache.keys()
            if len(key) >= prefix_len and key[:prefix_len] == prefix
        ]
        
        for key in keys_to_remove:
            entry = self.cache[key]
            self.current_size -= entry.size
            del self.cache[key]
            if key in self.access_order:
                del self.access_order[key]
        
        return len(keys_to_remove)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_accesses = self.hits + self.misses
        hit_rate = (self.hits / total_accesses * 100) if total_accesses > 0 else 0
        
        return {
            'size_mb': self.current_size / (1024 * 1024),
            'max_size_mb': self.max_size / (1024 * 1024),
            'entries': len(self.cache),
            'max_entries': self.max_entries,
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate_percent': hit_rate,
            'average_entry_size_kb': (self.current_size / len(self.cache) / 1024) if self.cache else 0
        }
    
    def contains(self, key: Tuple[int, ...]) -> bool:
        """Check if a key is in cache"""
        return key in self.cache
    
    def remove(self, key: Tuple[int, ...]) -> bool:
        """Remove a specific key from cache"""
        if key in self.cache:
            entry = self.cache[key]
            self.current_size -= entry.size
            del self.cache[key]
            if key in self.access_order:
                del self.access_order[key]
            return True
        return False
    
    def get_keys(self) -> List[Tuple[int, ...]]:
        """Get all keys in cache"""
        return list(self.cache.keys())
    
    def get_values(self) -> List[Any]:
        """Get all values in cache"""
        return [entry.value for entry in self.cache.values()]
    
    def resize(self, new_max_size: int, new_max_entries: int) -> None:
        """
        Resize the cache.
        
        Args:
            new_max_size: New maximum size in MB
            new_max_entries: New maximum number of entries
        """
        self.max_size = new_max_size * 1024 * 1024
        self.max_entries = new_max_entries
        
        # Evict entries if needed
        while (self.current_size > self.max_size or 
               len(self.cache) > self.max_entries) and self.cache:
            self._evict()
        
        print(f"📐 Cache resized to {new_max_size}MB, {new_max_entries} entries")
    
    def save_state(self) -> Dict[str, Any]:
        """Save cache state for persistence"""
        return {
            'cache': [
                {
                    'key': list(entry.key),
                    'value': entry.value,
                    'timestamp': entry.timestamp,
                    'size': entry.size,
                    'access_count': entry.access_count
                }
                for entry in self.cache.values()
            ],
            'current_size': self.current_size,
            'hits': self.hits,
            'misses': self.misses,
            'access_order': list(self.access_order.keys())
        }
    
    def load_state(self, state: Dict[str, Any]) -> None:
        """Load cache state from persistence"""
        self.cache.clear()
        self.access_order.clear()
        self.current_size = 0
        self.hits = state.get('hits', 0)
        self.misses = state.get('misses', 0)
        
        for entry_data in state.get('cache', []):
            key = tuple(entry_data['key'])
            entry = CacheEntry(
                key=key,
                value=entry_data['value'],
                timestamp=entry_data['timestamp'],
                size=entry_data['size'],
                access_count=entry_data['access_count']
            )
            self.cache[key] = entry
            self.access_order[key] = entry
            self.current_size += entry.size
        
        # Restore access order
        access_order_keys = state.get('access_order', [])
        if access_order_keys:
            # Reorder based on access order
            new_access_order = OrderedDict()
            for key in access_order_keys:
                if key in self.cache:
                    new_access_order[key] = self.cache[key]
            self.access_order = new_access_order
        
        print(f"📥 Cache state loaded ({len(self.cache)} entries)")
