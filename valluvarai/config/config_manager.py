"""
Configuration manager for ValluvarAI.
"""

import os
import json
import dotenv
from pathlib import Path
from typing import Dict, Any, Optional

# Load environment variables from .env file
dotenv.load_dotenv()


class ConfigManager:
    """Configuration manager for ValluvarAI."""

    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize the configuration manager.

        Args:
            config_file: Path to the configuration file. If None, uses the default path.
        """
        # Set up configuration file
        if config_file:
            self.config_file = Path(config_file)
        else:
            # Try to find the configuration file in various locations
            # 1. Check if there's a config file in the current directory
            if os.path.exists("valluvar_config.json"):
                self.config_file = Path("valluvar_config.json")
            # 2. Check if there's a config file in the user's home directory
            elif os.path.exists(os.path.expanduser("~/.valluvarai/config.json")):
                self.config_file = Path(os.path.expanduser("~/.valluvarai/config.json"))
            # 3. Use the default config file in the package
            else:
                self.config_file = Path(__file__).parent / "default_config.json"

        # Load configuration
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """
        Load configuration from file.

        Returns:
            Configuration dictionary.
        """
        try:
            if self.config_file.exists():
                with open(self.config_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            else:
                # If the config file doesn't exist, use the default config
                default_config_path = Path(__file__).parent / "default_config.json"
                if default_config_path.exists():
                    with open(default_config_path, "r", encoding="utf-8") as f:
                        return json.load(f)
                else:
                    print(f"Warning: Default config file not found at {default_config_path}")
                    return {}
        except Exception as e:
            print(f"Error loading configuration: {e}")
            return {}

    def save_config(self):
        """Save configuration to file."""
        try:
            # Create the directory if it doesn't exist
            self.config_file.parent.mkdir(parents=True, exist_ok=True)

            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving configuration: {e}")

    def get_api_key(self, provider: str) -> Optional[str]:
        """
        Get API key for a provider.

        Args:
            provider: Provider name.

        Returns:
            API key if found, None otherwise.
        """
        # Check if the API key is in the configuration
        api_key = self.config.get("api_keys", {}).get(provider)

        # If not, check if it's in the environment variables
        if not api_key:
            env_var_name = f"{provider.upper()}_API_KEY"
            api_key = os.environ.get(env_var_name)

        return api_key

    def set_api_key(self, provider: str, api_key: str):
        """
        Set API key for a provider.

        Args:
            provider: Provider name.
            api_key: API key.
        """
        if "api_keys" not in self.config:
            self.config["api_keys"] = {}

        self.config["api_keys"][provider] = api_key
        self.save_config()

    def get_service_config(self, service: str) -> Dict[str, Any]:
        """
        Get configuration for a service.

        Args:
            service: Service name.

        Returns:
            Service configuration dictionary.
        """
        return self.config.get("services", {}).get(service, {})

    def set_service_config(self, service: str, config: Dict[str, Any]):
        """
        Set configuration for a service.

        Args:
            service: Service name.
            config: Service configuration dictionary.
        """
        if "services" not in self.config:
            self.config["services"] = {}

        self.config["services"][service] = config
        self.save_config()

    def get_ui_config(self) -> Dict[str, Any]:
        """
        Get UI configuration.

        Returns:
            UI configuration dictionary.
        """
        return self.config.get("ui", {})

    def set_ui_config(self, config: Dict[str, Any]):
        """
        Set UI configuration.

        Args:
            config: UI configuration dictionary.
        """
        self.config["ui"] = config
        self.save_config()
