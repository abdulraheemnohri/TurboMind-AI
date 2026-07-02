#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TurboMind AI - Privacy Settings
================================
Manages privacy-related settings and data protection
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
import json


@dataclass
class PrivacyConfig:
    collect_usage_stats: bool = False
    collect_error_reports: bool = False
    collect_analytics: bool = False
    share_data_with_developers: bool = False
    share_anonymous_data: bool = False
    encrypt_local_data: bool = True
    auto_delete_old_data: bool = True
    data_retention_days: int = 30
    camera_access: bool = False
    microphone_access: bool = True
    storage_access: bool = True
    location_access: bool = False
    contacts_access: bool = False
    use_biometric_auth: bool = False
    auto_lock_timeout: int = 0
    require_auth_for_sensitive: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'collect_usage_stats': self.collect_usage_stats,
            'collect_error_reports': self.collect_error_reports,
            'collect_analytics': self.collect_analytics,
            'share_data_with_developers': self.share_data_with_developers,
            'share_anonymous_data': self.share_anonymous_data,
            'encrypt_local_data': self.encrypt_local_data,
            'auto_delete_old_data': self.auto_delete_old_data,
            'data_retention_days': self.data_retention_days,
            'camera_access': self.camera_access,
            'microphone_access': self.microphone_access,
            'storage_access': self.storage_access,
            'location_access': self.location_access,
            'contacts_access': self.contacts_access,
            'use_biometric_auth': self.use_biometric_auth,
            'auto_lock_timeout': self.auto_lock_timeout,
            'require_auth_for_sensitive': self.require_auth_for_sensitive
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PrivacyConfig':
        return cls(
            collect_usage_stats=data.get('collect_usage_stats', False),
            collect_error_reports=data.get('collect_error_reports', False),
            collect_analytics=data.get('collect_analytics', False),
            share_data_with_developers=data.get('share_data_with_developers', False),
            share_anonymous_data=data.get('share_anonymous_data', False),
            encrypt_local_data=data.get('encrypt_local_data', True),
            auto_delete_old_data=data.get('auto_delete_old_data', True),
            data_retention_days=data.get('data_retention_days', 30),
            camera_access=data.get('camera_access', False),
            microphone_access=data.get('microphone_access', True),
            storage_access=data.get('storage_access', True),
            location_access=data.get('location_access', False),
            contacts_access=data.get('contacts_access', False),
            use_biometric_auth=data.get('use_biometric_auth', False),
            auto_lock_timeout=data.get('auto_lock_timeout', 0),
            require_auth_for_sensitive=data.get('require_auth_for_sensitive', False)
        )


class PrivacySettings:
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = Path(config_path) if config_path else Path("config/privacy.json")
        self.config = PrivacyConfig()
        self._load_settings()
        print(" Privacy Settings initialized")
    
    def _load_settings(self) -> bool:
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.config = PrivacyConfig.from_dict(data)
                return True
            else:
                self._save_settings()
                return True
        except Exception as e:
            print(f" Error loading privacy settings: {e}")
            self.config = PrivacyConfig()
            return False
    
    def _save_settings(self) -> bool:
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config.to_dict(), f, indent=4)
            return True
        except Exception as e:
            print(f" Error saving privacy settings: {e}")
            return False
    
    def get_permission(self, permission_name: str) -> bool:
        permission_map = {
            'camera': 'camera_access', 'microphone': 'microphone_access',
            'storage': 'storage_access', 'location': 'location_access',
            'contacts': 'contacts_access'
        }
        attr_name = permission_map.get(permission_name.lower())
        if attr_name:
            return getattr(self.config, attr_name, False)
        return False
    
    def set_permission(self, permission_name: str, granted: bool) -> bool:
        permission_map = {
            'camera': 'camera_access', 'microphone': 'microphone_access',
            'storage': 'storage_access', 'location': 'location_access',
            'contacts': 'contacts_access'
        }
        attr_name = permission_map.get(permission_name.lower())
        if attr_name:
            setattr(self.config, attr_name, granted)
            self._save_settings()
            return True
        return False
    
    def get_all_permissions(self) -> Dict[str, bool]:
        return {
            'camera': self.config.camera_access,
            'microphone': self.config.microphone_access,
            'storage': self.config.storage_access,
            'location': self.config.location_access,
            'contacts': self.config.contacts_access
        }
    
    def set_data_collection(self, collect_usage: bool = False, collect_errors: bool = False, collect_analytics: bool = False) -> bool:
        try:
            self.config.collect_usage_stats = collect_usage
            self.config.collect_error_reports = collect_errors
            self.config.collect_analytics = collect_analytics
            self._save_settings()
            return True
        except Exception as e:
            print(f" Error updating data collection: {e}")
            return False
    
    def set_encryption(self, enabled: bool = True) -> bool:
        try:
            self.config.encrypt_local_data = enabled
            self._save_settings()
            return True
        except Exception as e:
            print(f" Error updating encryption: {e}")
            return False
    
    def get_privacy_summary(self) -> Dict[str, Any]:
        return {
            'data_collection': {
                'usage_stats': self.config.collect_usage_stats,
                'error_reports': self.config.collect_error_reports,
                'analytics': self.config.collect_analytics
            },
            'data_sharing': {
                'with_developers': self.config.share_data_with_developers,
                'anonymous': self.config.share_anonymous_data
            },
            'storage': {
                'encryption': self.config.encrypt_local_data,
                'auto_cleanup': self.config.auto_delete_old_data
            },
            'permissions': self.get_all_permissions()
        }
    
    def reset_to_defaults(self) -> bool:
        try:
            self.config = PrivacyConfig()
            self._save_settings()
            return True
        except Exception as e:
            print(f" Error resetting privacy: {e}")
            return False
    
    def is_data_collection_enabled(self) -> bool:
        return (self.config.collect_usage_stats or self.config.collect_error_reports or self.config.collect_analytics)
    
    def is_data_sharing_enabled(self) -> bool:
        return (self.config.share_data_with_developers or self.config.share_anonymous_data)