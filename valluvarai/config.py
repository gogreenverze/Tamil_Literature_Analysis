"""
Configuration module for ValluvarAI.
Handles API keys, service settings, and fallback mechanisms.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, List

# Default configuration
DEFAULT_CONFIG = {
    "api_keys": {
        "openai": "",
        "stability_ai": "",
        "leonardo_ai": "",
        "elevenlabs": ""
    },
    "services": {
        "image_generation": {
            "provider": "openai",  # openai, stability_ai, leonardo_ai
            "model": "dall-e-3",
            "image_size": "1024x1024",
            "quality": "standard",
            "fallback_to_placeholder": True
        },
        "text_generation": {
            "provider": "openai",  # openai, local
            "model": "gpt-4",
            "temperature": 0.7,
            "max_tokens": 1000,
            "fallback_to_template": True
        },
        "text_to_speech": {
            "provider": "gtts",  # gtts, elevenlabs
            "voice_tamil": "default",
            "voice_english": "default",
            "fallback_to_gtts": True
        },
        "video_generation": {
            "enable_ffmpeg": True,
            "default_fps": 24,
            "default_duration": 45,
            "add_music": True,
            "music_path": ""
        }
    },
    "cache": {
        "enable_caching": True,
        "cache_dir": "",
        "max_cache_size_mb": 1000,
        "cache_expiry_days": 30
    },
    "language": {
        "default": "both",  # tamil, english, both
        "supported_languages": ["tamil", "english"]
    }
}

class Config:
    """Configuration manager for ValluvarAI."""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the configuration manager.
        
        Args:
            config_path: Path to the configuration file. If None, uses the default path.
        """
        self.config = DEFAULT_CONFIG.copy()
        
        # Set default cache directory
        if not self.config["cache"]["cache_dir"]:
            self.config["cache"]["cache_dir"] = str(Path.home() / ".valluvarai" / "cache")
        
        # Load configuration from file if available
        if config_path:
            self.config_path = Path(config_path)
        else:
            self.config_path = Path.home() / ".valluvarai" / "config.json"
        
        self._load_config()
        
        # Load API keys from environment variables
        self._load_api_keys_from_env()
    
    def _load_config(self):
        """Load configuration from file."""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    file_config = json.load(f)
                    # Update config with file values, preserving default values for missing keys
                    self._update_nested_dict(self.config, file_config)
            except Exception as e:
                print(f"Error loading configuration: {e}")
    
    def _update_nested_dict(self, d: Dict, u: Dict):
        """
        Update a nested dictionary with values from another dictionary.
        
        Args:
            d: The dictionary to update.
            u: The dictionary with update values.
        """
        for k, v in u.items():
            if isinstance(v, dict) and k in d and isinstance(d[k], dict):
                self._update_nested_dict(d[k], v)
            else:
                d[k] = v
    
    def _load_api_keys_from_env(self):
        """Load API keys from environment variables."""
        # Map of config keys to environment variable names
        env_vars = {
            "openai": "OPENAI_API_KEY",
            "stability_ai": "STABILITY_API_KEY",
            "leonardo_ai": "LEONARDO_API_KEY",
            "elevenlabs": "ELEVENLABS_API_KEY"
        }
        
        for key, env_var in env_vars.items():
            if env_var in os.environ:
                self.config["api_keys"][key] = os.environ[env_var]
    
    def save(self):
        """Save the configuration to file."""
        try:
            # Create directory if it doesn't exist
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving configuration: {e}")
    
    def get_api_key(self, service: str) -> str:
        """
        Get the API key for a service.
        
        Args:
            service: The service name (openai, stability_ai, etc.).
            
        Returns:
            The API key for the service.
        """
        return self.config["api_keys"].get(service, "")
    
    def set_api_key(self, service: str, api_key: str):
        """
        Set the API key for a service.
        
        Args:
            service: The service name (openai, stability_ai, etc.).
            api_key: The API key.
        """
        self.config["api_keys"][service] = api_key
        self.save()
    
    def get_service_config(self, service: str) -> Dict[str, Any]:
        """
        Get the configuration for a service.
        
        Args:
            service: The service name (image_generation, text_generation, etc.).
            
        Returns:
            The configuration for the service.
        """
        return self.config["services"].get(service, {})
    
    def set_service_config(self, service: str, config: Dict[str, Any]):
        """
        Set the configuration for a service.
        
        Args:
            service: The service name (image_generation, text_generation, etc.).
            config: The configuration for the service.
        """
        self.config["services"][service] = config
        self.save()
    
    def get_cache_config(self) -> Dict[str, Any]:
        """
        Get the cache configuration.
        
        Returns:
            The cache configuration.
        """
        return self.config["cache"]
    
    def set_cache_config(self, config: Dict[str, Any]):
        """
        Set the cache configuration.
        
        Args:
            config: The cache configuration.
        """
        self.config["cache"] = config
        self.save()
    
    def get_language_config(self) -> Dict[str, Any]:
        """
        Get the language configuration.
        
        Returns:
            The language configuration.
        """
        return self.config["language"]
    
    def set_language_config(self, config: Dict[str, Any]):
        """
        Set the language configuration.
        
        Args:
            config: The language configuration.
        """
        self.config["language"] = config
        self.save()
    
    def is_service_available(self, service: str) -> bool:
        """
        Check if a service is available.
        
        Args:
            service: The service name (openai, stability_ai, etc.).
            
        Returns:
            True if the service is available, False otherwise.
        """
        # Check if the API key is available
        api_key = self.get_api_key(service)
        if not api_key:
            return False
        
        # Additional checks could be added here, such as testing the API connection
        
        return True
    
    def get_fallback_provider(self, service_type: str) -> str:
        """
        Get the fallback provider for a service type.
        
        Args:
            service_type: The service type (image_generation, text_generation, etc.).
            
        Returns:
            The fallback provider for the service type.
        """
        service_config = self.get_service_config(service_type)
        
        if service_type == "image_generation":
            # Check if the primary provider is available
            primary_provider = service_config.get("provider", "openai")
            if self.is_service_available(primary_provider):
                return primary_provider
            
            # Try alternative providers
            for provider in ["openai", "stability_ai", "leonardo_ai"]:
                if provider != primary_provider and self.is_service_available(provider):
                    return provider
            
            # If no provider is available, use placeholder
            if service_config.get("fallback_to_placeholder", True):
                return "placeholder"
            
            return ""
        
        elif service_type == "text_generation":
            # Check if the primary provider is available
            primary_provider = service_config.get("provider", "openai")
            if self.is_service_available(primary_provider):
                return primary_provider
            
            # If no provider is available, use template
            if service_config.get("fallback_to_template", True):
                return "template"
            
            return ""
        
        elif service_type == "text_to_speech":
            # Check if the primary provider is available
            primary_provider = service_config.get("provider", "gtts")
            if primary_provider == "gtts" or self.is_service_available(primary_provider):
                return primary_provider
            
            # If the primary provider is not available, use gtts as fallback
            if service_config.get("fallback_to_gtts", True):
                return "gtts"
            
            return ""
        
        return ""

# Global configuration instance
config = Config()
