"""
Caching module for ValluvarAI.
Provides caching functionality for API responses, generated content, etc.
"""

import os
import json
import hashlib
import time
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, List, Union, Tuple
import pickle

from valluvarai.config import config

class Cache:
    """Cache manager for ValluvarAI."""

    def __init__(self, cache_dir: Optional[str] = None):
        """
        Initialize the cache manager.

        Args:
            cache_dir: Directory to store cache files. If None, uses the default from config.
        """
        # Try to get cache config from the new config system
        try:
            cache_config = config.get_service_config("cache")
        except (AttributeError, KeyError):
            # Fallback to default values if config is not available
            cache_config = {}

        if cache_dir:
            self.cache_dir = Path(cache_dir)
        else:
            cache_dir_from_config = cache_config.get("cache_dir", "")
            if cache_dir_from_config:
                self.cache_dir = Path(cache_dir_from_config)
            else:
                # Default to a directory in the user's home directory
                self.cache_dir = Path.home() / ".valluvarai" / "cache"

        self.enable_caching = cache_config.get("enable_caching", True)
        self.max_cache_size_mb = cache_config.get("max_cache_size_mb", 1000)
        self.cache_expiry_days = cache_config.get("cache_expiry_days", 30)

        # Create cache directory if it doesn't exist
        if self.enable_caching:
            self.cache_dir.mkdir(parents=True, exist_ok=True)

            # Create subdirectories for different types of cached content
            (self.cache_dir / "kural").mkdir(exist_ok=True)
            (self.cache_dir / "stories").mkdir(exist_ok=True)
            (self.cache_dir / "images").mkdir(exist_ok=True)
            (self.cache_dir / "audio").mkdir(exist_ok=True)
            (self.cache_dir / "analysis").mkdir(exist_ok=True)

    def _get_cache_key(self, key_data: Any) -> str:
        """
        Generate a cache key from the input data.

        Args:
            key_data: Data to generate the key from.

        Returns:
            Cache key as a string.
        """
        # Convert the input data to a string
        if isinstance(key_data, dict):
            key_str = json.dumps(key_data, sort_keys=True)
        elif isinstance(key_data, (list, tuple)):
            key_str = json.dumps(key_data, sort_keys=True)
        else:
            key_str = str(key_data)

        # Generate a hash of the string
        return hashlib.md5(key_str.encode()).hexdigest()

    def _get_cache_path(self, cache_type: str, cache_key: str) -> Path:
        """
        Get the path to a cache file.

        Args:
            cache_type: Type of cached content (kural, stories, images, etc.).
            cache_key: Cache key.

        Returns:
            Path to the cache file.
        """
        return self.cache_dir / cache_type / f"{cache_key}.pkl"

    def get(self, cache_type: str, key_data: Any) -> Optional[Any]:
        """
        Get cached data.

        Args:
            cache_type: Type of cached content (kural, stories, images, etc.).
            key_data: Data to generate the cache key from.

        Returns:
            Cached data if available and not expired, None otherwise.
        """
        if not self.enable_caching:
            return None

        cache_key = self._get_cache_key(key_data)
        cache_path = self._get_cache_path(cache_type, cache_key)

        if not cache_path.exists():
            return None

        # Check if the cache is expired
        cache_age_days = (time.time() - cache_path.stat().st_mtime) / (60 * 60 * 24)
        if cache_age_days > self.cache_expiry_days:
            # Remove expired cache
            cache_path.unlink()
            return None

        # Load the cached data
        try:
            with open(cache_path, 'rb') as f:
                return pickle.load(f)
        except Exception as e:
            print(f"Error loading cache: {e}")
            return None

    def set(self, cache_type: str, key_data: Any, data: Any) -> bool:
        """
        Cache data.

        Args:
            cache_type: Type of cached content (kural, stories, images, etc.).
            key_data: Data to generate the cache key from.
            data: Data to cache.

        Returns:
            True if the data was cached successfully, False otherwise.
        """
        if not self.enable_caching:
            return False

        # Check if we need to clean up the cache
        self._cleanup_cache_if_needed()

        cache_key = self._get_cache_key(key_data)
        cache_path = self._get_cache_path(cache_type, cache_key)

        # Save the data to cache
        try:
            with open(cache_path, 'wb') as f:
                pickle.dump(data, f)
            return True
        except Exception as e:
            print(f"Error caching data: {e}")
            return False

    def invalidate(self, cache_type: str, key_data: Any) -> bool:
        """
        Invalidate cached data.

        Args:
            cache_type: Type of cached content (kural, stories, images, etc.).
            key_data: Data to generate the cache key from.

        Returns:
            True if the cache was invalidated successfully, False otherwise.
        """
        if not self.enable_caching:
            return False

        cache_key = self._get_cache_key(key_data)
        cache_path = self._get_cache_path(cache_type, cache_key)

        if not cache_path.exists():
            return False

        try:
            cache_path.unlink()
            return True
        except Exception as e:
            print(f"Error invalidating cache: {e}")
            return False

    def clear(self, cache_type: Optional[str] = None) -> bool:
        """
        Clear the cache.

        Args:
            cache_type: Type of cached content to clear. If None, clears all cache.

        Returns:
            True if the cache was cleared successfully, False otherwise.
        """
        if not self.enable_caching:
            return False

        try:
            if cache_type:
                # Clear specific cache type
                cache_dir = self.cache_dir / cache_type
                if cache_dir.exists():
                    for file in cache_dir.glob("*.pkl"):
                        file.unlink()
            else:
                # Clear all cache
                for cache_dir in ["kural", "stories", "images", "audio", "analysis"]:
                    cache_path = self.cache_dir / cache_dir
                    if cache_path.exists():
                        for file in cache_path.glob("*.pkl"):
                            file.unlink()

            return True
        except Exception as e:
            print(f"Error clearing cache: {e}")
            return False

    def _get_cache_size(self) -> int:
        """
        Get the total size of the cache in bytes.

        Returns:
            Total size of the cache in bytes.
        """
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(self.cache_dir):
            for filename in filenames:
                file_path = Path(dirpath) / filename
                total_size += file_path.stat().st_size

        return total_size

    def _cleanup_cache_if_needed(self):
        """Clean up the cache if it exceeds the maximum size."""
        # Check if the cache size exceeds the maximum
        cache_size_mb = self._get_cache_size() / (1024 * 1024)
        if cache_size_mb <= self.max_cache_size_mb:
            return

        # Get all cache files with their modification times
        cache_files = []
        for dirpath, dirnames, filenames in os.walk(self.cache_dir):
            for filename in filenames:
                file_path = Path(dirpath) / filename
                cache_files.append((file_path, file_path.stat().st_mtime))

        # Sort by modification time (oldest first)
        cache_files.sort(key=lambda x: x[1])

        # Remove files until the cache size is below the maximum
        for file_path, _ in cache_files:
            file_path.unlink()

            # Check if we've freed up enough space
            cache_size_mb = self._get_cache_size() / (1024 * 1024)
            if cache_size_mb <= self.max_cache_size_mb * 0.8:  # Aim for 80% of max size
                break

# Global cache instance
cache = Cache()
