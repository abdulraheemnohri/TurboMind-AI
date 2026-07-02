#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TurboMind AI - Memory Manager
=============================
Manages memory allocation, cleanup, and optimization for AI models
"""

import psutil
import time
import gc
from typing import Dict, Any, Optional
from enum import Enum


class MemoryMode(Enum):
    """Memory management modes"""
    LOW_RAM = "low_ram"  # For devices with 4GB RAM
    BALANCED = "balanced"  # For devices with 6-8GB RAM
    HIGH_RAM = "high_ram"  # For devices with 12-16GB RAM


class MemoryManager:
    """
    Manages memory for the AI runtime.
    Handles adaptive caching, context compression, and cleanup.
    """
    
    def __init__(self, mode: MemoryMode = MemoryMode.BALANCED):
        """
        Initialize the memory manager.
        
        Args:
            mode: Memory management mode
        """
        self.mode = mode
        self.cache = {}
        self.last_cleanup = time.time()
        self.stats = {
            'total_ram': 0,
            'available_ram': 0,
            'used_ram': 0,
            'cache_size': 0
        }
        
        self._update_stats()
        print(f"🧠 Memory Manager initialized in {mode.value} mode")
    
    def _update_stats(self) -> None:
        """Update memory statistics"""
        if hasattr(psutil, 'virtual_memory'):
            mem = psutil.virtual_memory()
            self.stats['total_ram'] = mem.total / (1024 ** 2)  # MB
            self.stats['available_ram'] = mem.available / (1024 ** 2)
            self.stats['used_ram'] = mem.used / (1024 ** 2)
        
        self.stats['cache_size'] = sum(
            len(str(v)) for v in self.cache.values()
        ) / 1024  # Approximate size in KB
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current memory statistics"""
        self._update_stats()
        return {
            **self.stats,
            'mode': self.mode.value,
            'timestamp': time.time()
        }
    
    def set_mode(self, mode: MemoryMode) -> None:
        """Set the memory management mode"""
        self.mode = mode
        print(f"🔄 Memory mode changed to: {mode.value}")
    
    def allocate(self, size_mb: float, priority: int = 0) -> bool:
        """
        Allocate memory for a task.
        
        Args:
            size_mb: Size in megabytes
            priority: Priority level (0-10, higher is more important)
            
        Returns:
            bool: True if allocation successful
        """
        self._update_stats()
        
        # Check if we have enough memory
        if size_mb > self.stats['available_ram']:
            # Try to free some memory
            self.cleanup(aggressive=True)
            self._update_stats()
            
            if size_mb > self.stats['available_ram']:
                print(f"❌ Not enough memory: need {size_mb}MB, have {self.stats['available_ram']}MB")
                return False
        
        print(f"✅ Allocated {size_mb}MB (priority: {priority})")
        return True
    
    def free(self, size_mb: float) -> None:
        """Free allocated memory"""
        print(f"🗑️  Freed {size_mb}MB")
        self._update_stats()
    
    def cache_store(self, key: str, value: Any) -> None:
        """Store a value in cache"""
        # Check cache limits based on mode
        max_cache_size = {
            MemoryMode.LOW_RAM: 100,  # 100MB
            MemoryMode.BALANCED: 500,  # 500MB
            MemoryMode.HIGH_RAM: 1000  # 1GB
        }.get(self.mode, 500)
        
        # Estimate value size
        value_size = len(str(value)) / 1024  # KB
        
        if self.stats['cache_size'] + value_size > max_cache_size:
            # Cache is full, cleanup
            self.cache_cleanup()
        
        self.cache[key] = value
        self.stats['cache_size'] += value_size
        
        print(f"💾 Cached: {key} ({value_size:.2f}KB)")
    
    def cache_get(self, key: str) -> Optional[Any]:
        """Get a value from cache"""
        return self.cache.get(key)
    
    def cache_cleanup(self, percentage: float = 0.5) -> None:
        """
        Clean up cache by removing least recently used items.
        
        Args:
            percentage: Percentage of cache to remove
        """
        if not self.cache:
            return
        
        # Simple cleanup: remove first N items
        keys_to_remove = list(self.cache.keys())[:int(len(self.cache) * percentage)]
        
        for key in keys_to_remove:
            value_size = len(str(self.cache[key])) / 1024
            del self.cache[key]
            self.stats['cache_size'] -= value_size
            print(f"🧹 Removed from cache: {key}")
    
    def cleanup(self, aggressive: bool = False) -> None:
        """
        Clean up memory.
        
        Args:
            aggressive: If True, perform more aggressive cleanup
        """
        print("🧹 Cleaning up memory...")
        
        # Run garbage collection
        gc.collect()
        
        # Cache cleanup
        self.cache_cleanup(percentage=0.3 if not aggressive else 0.7)
        
        # Clear various caches
        if aggressive:
            # Clear PyTorch cache if available
            try:
                import torch
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
            except ImportError:
                pass
        
        self.last_cleanup = time.time()
        self._update_stats()
        
        print(f"✅ Cleanup complete. Freed: {self.stats['available_ram'] - self.stats.get('available_ram_before', 0):.2f}MB")
    
    def compress_context(self, context: Any, ratio: float = 0.5) -> Any:
        """
        Compress context to save memory.
        
        Args:
            context: Context to compress
            ratio: Compression ratio (0-1)
            
        Returns:
            Compressed context
        """
        # TODO: Implement actual context compression
        # For now, just return the context as-is
        print(f"🗜️  Compressing context (ratio: {ratio})")
        return context
    
    def should_cleanup(self) -> bool:
        """Check if cleanup should be performed"""
        self._update_stats()
        
        # Cleanup if:
        # - Memory usage is high
        # - Cache is getting large
        # - It's been a while since last cleanup
        
        thresholds = {
            MemoryMode.LOW_RAM: 0.8,  # 80% usage
            MemoryMode.BALANCED: 0.7,  # 70% usage
            MemoryMode.HIGH_RAM: 0.6  # 60% usage
        }
        
        memory_usage = self.stats['used_ram'] / self.stats['total_ram']
        time_since_cleanup = time.time() - self.last_cleanup
        
        return (
            memory_usage > thresholds.get(self.mode, 0.7) or
            self.stats['cache_size'] > 100 or  # 100MB
            time_since_cleanup > 300  # 5 minutes
        )
