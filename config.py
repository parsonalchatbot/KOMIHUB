"""
Configuration management for KOMIHUB Bot
Supports environment variables and config files
"""
import os
import json
from pathlib import Path
from typing import Optional, Dict, Any

def load_config() -> Dict[str, Any]:
    """Load configuration from environment variables or config file"""
    
    # Default configuration
    config = {
        "bot": {
            "token": os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE"),
            "name": os.getenv("BOT_NAME", "KOMIHUB BOT"),
            "admin_id": int(os.getenv("ADMIN_ID", "6122160777")),
            "admin_name": os.getenv("ADMIN_NAME", "EJ")
        },
        "features": {
            "auto_update": os.getenv("AUTO_UPDATE", "true").lower() == "true",
            "update_check_interval": int(os.getenv("UPDATE_CHECK_INTERVAL", "3600")),
            "maintenance_mode": os.getenv("MAINTENANCE_MODE", "false").lower() == "true",
            "user_tracking": os.getenv("USER_TRACKING", "true").lower() == "true",
            "broadcast_system": os.getenv("BROADCAST_SYSTEM", "true").lower() == "true",
            "admin_management": os.getenv("ADMIN_MANAGEMENT", "true").lower() == "true",
            "hot_reload": os.getenv("HOT_RELOAD", "true").lower() == "true"
        },
        "apis": {
            "version_url": os.getenv("VERSION_URL", "YOUR_VERSION_URL_HERE"),
            "github_repo": os.getenv("GITHUB_REPO", "GrandpaEJ/KOMIHUB"),
            "yt_api_key": os.getenv("YOUTUBE_API_KEY", "YOUR_YOUTUBE_API_KEY_HERE")
        },
        "database": {
            "data_dir": os.getenv("DATA_DIR", "data"),
            "backup_enabled": os.getenv("BACKUP_ENABLED", "true").lower() == "true",
            "backup_interval": int(os.getenv("BACKUP_INTERVAL", "86400")),
            "url": os.getenv("DATABASE_URL", "sqlite:///./data/komihub.db")
        },
        "logging": {
            "level": os.getenv("LOG_LEVEL", "INFO"),
            "file_logging": os.getenv("LOG_TO_FILE", "true").lower() == "true",
            "console_logging": os.getenv("LOG_TO_CONSOLE", "true").lower() == "true"
        },
        "performance": {
            "max_workers": int(os.getenv("MAX_WORKERS", "4")),
            "timeout": int(os.getenv("TIMEOUT", "30")),
            "rate_limit": {
                "enabled": os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true",
                "max_requests": int(os.getenv("RATE_LIMIT_MAX_REQUESTS", "100")),
                "window_seconds": int(os.getenv("RATE_LIMIT_WINDOW", "60"))
            }
        }
    }
    
    # Also load from config.json if it exists (overrides defaults)
    config_file = Path("config.json")
    if config_file.exists():
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                file_config = json.load(f)
            
            # Deep merge file config with environment config
            config = deep_merge(config, file_config)
        except Exception as e:
            print(f"Warning: Could not load config.json: {e}")
    
    return config

def deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """Deep merge two dictionaries"""
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result

# Global config instance
config = load_config()

# Export commonly used values
BOT_TOKEN = config["bot"]["token"]
BOT_NAME = config["bot"]["name"]
ADMIN_ID = config["bot"]["admin_id"]
ADMIN_NAME = config["bot"]["admin_name"]

DATABASE_URL = config["database"]["url"]
DATA_DIR = config["database"]["data_dir"]

LOG_LEVEL = config["logging"]["level"]
LOG_TO_FILE = config["logging"]["file_logging"]
LOG_TO_CONSOLE = config["logging"]["console_logging"]

MAX_WORKERS = config["performance"]["max_workers"]
TIMEOUT = config["performance"]["timeout"]

# Rate limiting config
RATE_LIMIT_ENABLED = config["performance"]["rate_limit"]["enabled"]
RATE_LIMIT_MAX_REQUESTS = config["performance"]["rate_limit"]["max_requests"]
RATE_LIMIT_WINDOW = config["performance"]["rate_limit"]["window_seconds"]

# Feature toggles
AUTO_UPDATE = config["features"]["auto_update"]
UPDATE_CHECK_INTERVAL = config["features"]["update_check_interval"]
MAINTENANCE_MODE = config["features"]["maintenance_mode"]
USER_TRACKING = config["features"]["user_tracking"]
BROADCAST_SYSTEM = config["features"]["broadcast_system"]
ADMIN_MANAGEMENT = config["features"]["admin_management"]
HOT_RELOAD = config["features"]["hot_reload"]

# API keys
YOUTUBE_API_KEY = config["apis"]["yt_api_key"]
VERSION_URL = config["apis"]["version_url"]
GITHUB_REPO = config["apis"]["github_repo"]

def get_config() -> Dict[str, Any]:
    """Get the full configuration dictionary"""
    return config

def reload_config():
    """Reload configuration from files and environment"""
    global config, BOT_TOKEN, BOT_NAME, ADMIN_ID, ADMIN_NAME, DATABASE_URL, DATA_DIR
    global LOG_LEVEL, LOG_TO_FILE, LOG_TO_CONSOLE, MAX_WORKERS, TIMEOUT
    global RATE_LIMIT_ENABLED, RATE_LIMIT_MAX_REQUESTS, RATE_LIMIT_WINDOW
    global AUTO_UPDATE, UPDATE_CHECK_INTERVAL, MAINTENANCE_MODE, USER_TRACKING
    global BROADCAST_SYSTEM, ADMIN_MANAGEMENT, HOT_RELOAD, YOUTUBE_API_KEY
    global VERSION_URL, GITHUB_REPO
    
    config = load_config()
    
    # Update exported values
    BOT_TOKEN = config["bot"]["token"]
    BOT_NAME = config["bot"]["name"]
    ADMIN_ID = config["bot"]["admin_id"]
    ADMIN_NAME = config["bot"]["admin_name"]
    
    DATABASE_URL = config["database"]["url"]
    DATA_DIR = config["database"]["data_dir"]
    
    LOG_LEVEL = config["logging"]["level"]
    LOG_TO_FILE = config["logging"]["file_logging"]
    LOG_TO_CONSOLE = config["logging"]["console_logging"]
    
    MAX_WORKERS = config["performance"]["max_workers"]
    TIMEOUT = config["performance"]["timeout"]
    
    RATE_LIMIT_ENABLED = config["performance"]["rate_limit"]["enabled"]
    RATE_LIMIT_MAX_REQUESTS = config["performance"]["rate_limit"]["max_requests"]
    RATE_LIMIT_WINDOW = config["performance"]["rate_limit"]["window_seconds"]
    
    AUTO_UPDATE = config["features"]["auto_update"]
    UPDATE_CHECK_INTERVAL = config["features"]["update_check_interval"]
    MAINTENANCE_MODE = config["features"]["maintenance_mode"]
    USER_TRACKING = config["features"]["user_tracking"]
    BROADCAST_SYSTEM = config["features"]["broadcast_system"]
    ADMIN_MANAGEMENT = config["features"]["admin_management"]
    HOT_RELOAD = config["features"]["hot_reload"]
    
    YOUTUBE_API_KEY = config["apis"]["yt_api_key"]
    VERSION_URL = config["apis"]["version_url"]
    GITHUB_REPO = config["apis"]["github_repo"]
