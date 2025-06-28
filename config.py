"""
Configuration management for Skynet Lite
"""

import os
import yaml
from typing import Optional


class Config:
    def __init__(self, config_file: str = "config.yaml"):
        self.config_file = config_file
        self._load_config()
    
    def _load_config(self):
        """Load configuration from file and environment variables"""
        # Default configuration
        self.default_config = {
            "ollama": {
                "base_url": "http://localhost:11434",
                "model": "mistral",
                "timeout": 30
            },
            "bing": {
                "api_key": None,
                "endpoint": "https://api.bing.microsoft.com/v7.0/search",
                "market": "en-US",
                "count": 5
            },
            "chat": {
                "max_history": 10,
                "temperature": 0.7,
                "max_tokens": 1000
            }
        }
        
        # Load from config file if it exists
        config_data = self.default_config.copy()
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    file_config = yaml.safe_load(f) or {}
                self._merge_config(config_data, file_config)
            except Exception as e:
                print(f"Warning: Could not load config file {self.config_file}: {e}")
        
        # Override with environment variables
        self._load_env_vars(config_data)
        
        # Set attributes
        self.ollama_base_url = config_data["ollama"]["base_url"]
        self.ollama_model = config_data["ollama"]["model"]
        self.ollama_timeout = config_data["ollama"]["timeout"]
        
        self.bing_api_key = config_data["bing"]["api_key"]
        self.bing_endpoint = config_data["bing"]["endpoint"]
        self.bing_market = config_data["bing"]["market"]
        self.bing_count = config_data["bing"]["count"]
        
        self.max_history = config_data["chat"]["max_history"]
        self.temperature = config_data["chat"]["temperature"]
        self.max_tokens = config_data["chat"]["max_tokens"]
    
    def _merge_config(self, base: dict, override: dict):
        """Recursively merge configuration dictionaries"""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_config(base[key], value)
            else:
                base[key] = value
    
    def _load_env_vars(self, config: dict):
        """Load configuration from environment variables"""
        env_mappings = {
            "BING_API_KEY": ["bing", "api_key"],
            "OLLAMA_BASE_URL": ["ollama", "base_url"],
            "OLLAMA_MODEL": ["ollama", "model"],
        }
        
        for env_var, config_path in env_mappings.items():
            value = os.getenv(env_var)
            if value:
                current = config
                for key in config_path[:-1]:
                    current = current[key]
                current[config_path[-1]] = value
    
    def create_default_config_file(self):
        """Create a default config.yaml file"""
        try:
            with open(self.config_file, 'w') as f:
                yaml.dump(self.default_config, f, default_flow_style=False, indent=2)
            print(f"✅ Created default config file: {self.config_file}")
        except Exception as e:
            print(f"❌ Could not create config file: {e}")
    
    def validate(self) -> bool:
        """Validate the configuration"""
        if not self.bing_api_key:
            print("⚠️  Warning: No Bing API key configured. Web search will be disabled.")
            print("   Set BING_API_KEY environment variable or add it to config.yaml")
        
        return True
