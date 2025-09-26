#!/usr/bin/env python3
"""
Configuration management for Skynet Core
Handles environment variables and default settings
"""

import os
from typing import Optional


class Config:
    """Configuration class for Skynet Core"""
    
    def __init__(self):
        """Initialize configuration with environment variables and defaults"""
        # Ollama Configuration
        self.ollama_base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
        self.ollama_model = os.environ.get("OLLAMA_MODEL", "mistral")
        
        # Search Configuration
        self.search_provider = os.environ.get("SEARCH_PROVIDER", "duckduckgo")
        
        # Web Search API Keys (optional)
        self.azure_search_key = os.environ.get("AZURE_SEARCH_KEY")
        self.azure_search_endpoint = os.environ.get("AZURE_SEARCH_ENDPOINT")
        self.google_api_key = os.environ.get("GOOGLE_API_KEY")
        self.google_cx = os.environ.get("GOOGLE_CX")
        
        # AI Provider API Keys (optional cloud fallbacks)
        self.openai_api_key = os.environ.get("OPENAI_API_KEY")
        self.openai_model = os.environ.get("OPENAI_MODEL", "gpt-3.5-turbo")
        
        self.anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY")
        self.anthropic_model = os.environ.get("ANTHROPIC_MODEL", "claude-3-sonnet-20240229")
        
        self.gemini_api_key = os.environ.get("GOOGLE_API_KEY")  # Same as google_api_key for Gemini
        self.gemini_model = os.environ.get("GEMINI_MODEL", "gemini-pro")
        
        # GitHub Copilot Configuration
        self.github_copilot_token = os.environ.get("GITHUB_COPILOT_TOKEN")
        self.copilot_api_url = os.environ.get("COPILOT_API_URL")
        
        # Microsoft Copilot Configuration
        self.microsoft_copilot_api_key = os.environ.get("MICROSOFT_COPILOT_API_KEY")
        self.microsoft_copilot_endpoint = os.environ.get("MICROSOFT_COPILOT_ENDPOINT")
        
        # Storage Configuration
        self.storage_type = os.environ.get("SKYNET_STORAGE_TYPE", "sqlite")
        
        # SQLite Configuration (default)
        self.sqlite_database = os.environ.get("SQLITE_DATABASE", "data/skynet.db")
        
        # MSSQL Configuration (optional)
        self.mssql_server = os.environ.get("MSSQL_SERVER", "localhost")
        self.mssql_database = os.environ.get("MSSQL_DATABASE", "skynet_core")
        self.mssql_username = os.environ.get("MSSQL_USERNAME")
        self.mssql_password = os.environ.get("MSSQL_PASSWORD")
        self.mssql_driver = os.environ.get("MSSQL_DRIVER", "ODBC Driver 17 for SQL Server")
        self.mssql_trusted_connection = os.environ.get("MSSQL_TRUSTED_CONNECTION", "false").lower() == "true"
        self.mssql_encrypt = os.environ.get("MSSQL_ENCRYPT", "true").lower() == "true"
        self.mssql_trust_server_certificate = os.environ.get("MSSQL_TRUST_SERVER_CERTIFICATE", "false").lower() == "true"
        self.mssql_connection_timeout = int(os.environ.get("MSSQL_CONNECTION_TIMEOUT", "30"))
        
        # Memory Configuration
        self.max_turns = int(os.environ.get("MEMORY_MAX_TURNS", "10"))
        
        # Web Interface Configuration
        self.web_host = os.environ.get("WEB_HOST", "0.0.0.0")
        self.web_port = int(os.environ.get("WEB_PORT", "5005"))
        self.secret_key = os.environ.get("SECRET_KEY")
        
        # Debug Configuration
        self.debug = os.environ.get("DEBUG", "false").lower() == "true"
        self.log_level = os.environ.get("LOG_LEVEL", "INFO").upper()
    
    def get(self, key: str, default=None):
        """Get configuration value by key with optional default"""
        return getattr(self, key, default)
    
    def get_storage_config(self) -> dict:
        """Get storage-specific configuration as a dictionary"""
        if self.storage_type == "mssql":
            return {
                "server": self.mssql_server,
                "database": self.mssql_database,
                "username": self.mssql_username,
                "password": self.mssql_password,
                "driver": self.mssql_driver,
                "trusted_connection": self.mssql_trusted_connection,
                "encrypt": self.mssql_encrypt,
                "trust_server_certificate": self.mssql_trust_server_certificate,
                "connection_timeout": self.mssql_connection_timeout,
            }
        elif self.storage_type == "sqlite":
            return {
                "database": self.sqlite_database,
            }
        else:
            return {}
    
    def has_cloud_providers(self) -> bool:
        """Check if any cloud AI provider is configured"""
        return bool(
            self.openai_api_key or 
            self.anthropic_api_key or 
            self.gemini_api_key or 
            self.github_copilot_token or 
            self.microsoft_copilot_api_key
        )
    
    def get_available_providers(self) -> list:
        """Get list of available AI providers based on configuration"""
        providers = ["ollama"]  # Ollama is always available (local)
        
        if self.openai_api_key:
            providers.append("openai")
        if self.anthropic_api_key:
            providers.append("anthropic")
        if self.gemini_api_key:
            providers.append("gemini")
        if self.github_copilot_token:
            providers.append("github_copilot")
        if self.microsoft_copilot_api_key:
            providers.append("microsoft_copilot")
            
        return providers
    
    def __repr__(self):
        """String representation showing key configuration values"""
        return (
            f"Config("
            f"ollama_model='{self.ollama_model}', "
            f"search_provider='{self.search_provider}', "
            f"storage_type='{self.storage_type}', "
            f"providers={len(self.get_available_providers())}"
            f")"
        )
