#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TurboMind AI - Scheduler
========================
Automatically detects and chooses the best execution path
"""

import time
import platform
import psutil
from typing import Dict, Any, Optional
from enum import Enum


class HardwareType(Enum):
    """Available hardware types"""
    CPU = "cpu"
    GPU = "gpu"
    NPU = "npu"


class Scheduler:
    """
    Schedules tasks and chooses the best execution path
    based on available hardware and system resources.
    """
    
    def __init__(self):
        """Initialize the scheduler"""
        self.hardware = self._detect_hardware()
        self.system_info = self._get_system_info()
        self.last_check = time.time()
        
        print(f"⚙️  Scheduler initialized")
        print(f"   Detected hardware: {self.hardware}")
    
    def _detect_hardware(self) -> Dict[HardwareType, bool]:
        """Detect available hardware"""
        hardware = {
            HardwareType.CPU: True,  # CPU is always available
            HardwareType.GPU: False,
            HardwareType.NPU: False
        }
        
        # Check for GPU (CUDA)
        try:
            import torch
            if torch.cuda.is_available():
                hardware[HardwareType.GPU] = True
                print("🎮 GPU (CUDA) detected")
        except ImportError:
            pass
        
        # Check for NPU (Neural Processing Unit)
        # This is platform-specific
        system = platform.system()
        
        if system == 'Android':
            # Check for Qualcomm Hexagon NPU
            try:
                # This is a placeholder - actual detection would use Android APIs
                hardware[HardwareType.NPU] = True
                print("🧠 NPU detected (Android)")
            except:
                pass
        elif system == 'Windows':
            # Check for Intel NPU or AMD NPU
            try:
                import torch
                if hasattr(torch, 'xpu') and torch.xpu.is_available():
                    hardware[HardwareType.NPU] = True
                    print("🧠 NPU detected (Windows)")
            except:
                pass
        
        return hardware
    
    def _get_system_info(self) -> Dict[str, Any]:
        """Get system information"""
        info = {
            'system': platform.system(),
            'node': platform.node(),
            'cpu_cores': psutil.cpu_count(logical=False),
            'total_ram_gb': psutil.virtual_memory().total / (1024 ** 3),
            'battery_percent': None,
            'temperature_c': None
        }
        
        # Get battery info (if available)
        try:
            battery = psutil.sensors_battery()
            if battery:
                info['battery_percent'] = battery.percent
        except:
            pass
        
        # Get temperature (if available)
        try:
            temps = psutil.sensors_temperatures()
            if temps:
                # Get CPU temperature
                cpu_temp = temps.get('coretemp', []) or temps.get('cpu_thermal', [])
                if cpu_temp:
                    info['temperature_c'] = cpu_temp[0].current
        except:
            pass
        
        return info
    
    def choose_execution_path(self, task_type: str = "inference") -> Dict[str, Any]:
        """
        Choose the best execution path for a task.
        
        Args:
            task_type: Type of task (inference, training, etc.)
            
        Returns:
            dict: Execution configuration
        """
        self._update_system_info()
        
        config = {
            'hardware': HardwareType.CPU.value,
            'threads': 1,
            'priority': 'normal'
        }
        
        # Choose hardware
        if self.hardware.get(HardwareType.NPU, False):
            config['hardware'] = HardwareType.NPU.value
            config['threads'] = 1  # NPUs typically use single thread
        elif self.hardware.get(HardwareType.GPU, False):
            config['hardware'] = HardwareType.GPU.value
            config['threads'] = 2  # GPUs can handle multiple threads
        else:
            # Use CPU
            config['hardware'] = HardwareType.CPU.value
            
            # Adjust threads based on CPU cores
            if self.system_info['cpu_cores'] >= 8:
                config['threads'] = 8
            elif self.system_info['cpu_cores'] >= 4:
                config['threads'] = 4
            else:
                config['threads'] = 2
        
        # Adjust for battery and temperature
        if self.system_info.get('battery_percent', 100) < 20:
            # Low battery - reduce performance
            config['priority'] = 'battery_saver'
            config['threads'] = max(1, config['threads'] // 2)
        
        if self.system_info.get('temperature_c', 0) > 70:
            # High temperature - reduce performance
            config['priority'] = 'thermal_protection'
            config['threads'] = max(1, config['threads'] // 2)
        
        # Task-specific optimizations
        if task_type == "inference":
            config['batch_size'] = 1
        elif task_type == "training":
            config['batch_size'] = min(4, self.system_info['cpu_cores'])
        
        return config
    
    def _update_system_info(self) -> None:
        """Update system information"""
        if time.time() - self.last_check > 60:  # Update every 60 seconds
            self.system_info = self._get_system_info()
            self.last_check = time.time()
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status"""
        self._update_system_info()
        return {
            **self.system_info,
            'hardware': {k.value: v for k, v in self.hardware.items()},
            'last_check': self.last_check
        }
    
    def schedule_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Schedule a task with optimal configuration.
        
        Args:
            task: Task configuration
            
        Returns:
            dict: Scheduled task with execution path
        """
        execution_path = self.choose_execution_path(
            task.get('type', 'inference')
        )
        
        scheduled_task = {
            **task,
            **execution_path,
            'scheduled_at': time.time(),
            'status': 'queued'
        }
        
        print(f"⏰ Task scheduled: {task.get('name', 'unknown')}")
        print(f"   Hardware: {execution_path['hardware']}")
        print(f"   Threads: {execution_path['threads']}")
        
        return scheduled_task
