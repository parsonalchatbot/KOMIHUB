"""
Configuration management for KOMIHUB Bot
Supports environment variables and config files
"""
import os
import json
from pathlib import Path
from typing import Optional, Dict, Any

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()  # Load .env file if it exists
except ImportError:
    # Fallback if python-dotenv is not available
    pass

def load_config() -> Dict[str, Any]:
    """Load configuration - config.json as main, .env as fallback"""
    
    # Priority 1: Load from config.json (main source)
    config = {}
    config_file = Path("config.json")
    if config_file.exists():
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except Exception as e:
            print(f"Warning: Could not load config.json: {e}")
    
    # Priority 2: Environment variables as fallback for missing values
    env_config = {
        "bot": {
            "token": os.getenv("BOT_TOKEN"),
            "name": os.getenv("BOT_NAME"),
            "admin_id": int(os.getenv("ADMIN_ID", "6122160777")) if os.getenv("ADMIN_ID") else None,
            "admin_name": os.getenv("ADMIN_NAME")
        },
        "features": {
            "auto_update": os.getenv("AUTO_UPDATE"),
            "update_check_interval": int(os.getenv("UPDATE_CHECK_INTERVAL")) if os.getenv("UPDATE_CHECK_INTERVAL") else None,
            "maintenance_mode": os.getenv("MAINTENANCE_MODE"),
            "user_tracking": os.getenv("USER_TRACKING"),
            "broadcast_system": os.getenv("BROADCAST_SYSTEM"),
            "admin_management": os.getenv("ADMIN_MANAGEMENT"),
            "hot_reload": os.getenv("HOT_RELOAD")
        },
        "apis": {
            "version_url": os.getenv("VERSION_URL"),
            "github_repo": os.getenv("GITHUB_REPO"),
            "yt_api_key": os.getenv("YOUTUBE_API_KEY")
        },
        "image_spoiler": {
            "sfw_enabled": os.getenv("SFW_IMG_SPOILER"),
            "nsfw_enabled": os.getenv("NSFW_IMG_SPOILER")
        },
        "database": {
            "data_dir": os.getenv("DATA_DIR"),
            "backup_enabled": os.getenv("BACKUP_ENABLED"),
            "backup_interval": int(os.getenv("BACKUP_INTERVAL")) if os.getenv("BACKUP_INTERVAL") else None,
            "url": os.getenv("DATABASE_URL")
        },
        "logging": {
            "level": os.getenv("LOG_LEVEL"),
            "file_logging": os.getenv("LOG_TO_FILE"),
            "console_logging": os.getenv("LOG_TO_CONSOLE")
        },
        "performance": {
            "max_workers": int(os.getenv("MAX_WORKERS")) if os.getenv("MAX_WORKERS") else None,
            "timeout": int(os.getenv("TIMEOUT")) if os.getenv("TIMEOUT") else None,
            "rate_limit": {
                "enabled": os.getenv("RATE_LIMIT_ENABLED"),
                "max_requests": int(os.getenv("RATE_LIMIT_MAX_REQUESTS")) if os.getenv("RATE_LIMIT_MAX_REQUESTS") else None,
                "window_seconds": int(os.getenv("RATE_LIMIT_WINDOW")) if os.getenv("RATE_LIMIT_WINDOW") else None
            }
        }
    }
    
    # Merge environment config as fallback for None values
    config = deep_merge_with_env_fallback(config, env_config)
    
    # Apply defaults for any remaining None values
    config = apply_defaults(config)
    
    return config

def deep_merge_with_env_fallback(base: Dict[str, Any], fallback: Dict[str, Any]) -> Dict[str, Any]:
    """Merge configs with environment variables as fallback for None values"""
    result = base.copy()
    
    for key, fallback_value in fallback.items():
        if key in result:
            if isinstance(result[key], dict) and isinstance(fallback_value, dict):
                result[key] = deep_merge_with_env_fallback(result[key], fallback_value)
            elif fallback_value is not None and (result[key] is None or result[key] == "YOUR_BOT_TOKEN_HERE"):
                result[key] = fallback_value
        else:
            result[key] = fallback_value
    
    return result

def apply_defaults(config: Dict[str, Any]) -> Dict[str, Any]:
    """Apply default values for any remaining None values"""
    defaults = {
        "bot": {
            "name": "KOMIHUB BOT",
            "admin_id": 6122160777,
            "admin_name": "EJ"
        },
        "features": {
            "auto_update": True,
            "update_check_interval": 3600,
            "maintenance_mode": False,
            "user_tracking": True,
            "broadcast_system": True,
            "admin_management": True,
            "hot_reload": True
        },
        "apis": {
            "github_repo": "GrandpaEJ/KOMIHUB"
        },
        "image_spoiler": {
            "sfw_enabled": True,
            "nsfw_enabled": True
        },
        "database": {
            "data_dir": "data",
            "backup_enabled": True,
            "backup_interval": 86400,
            "url": "sqlite:///./data/komihub.db"
        },
        "logging": {
            "level": "INFO",
            "file_logging": True,
            "console_logging": True
        },
        "performance": {
            "max_workers": 4,
            "timeout": 30,
            "rate_limit": {
                "enabled": True,
                "max_requests": 100,
                "window_seconds": 60
            }
        }
    }
    
    return deep_merge_with_env_fallback(defaults, config)

def deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """Deep merge two dictionaries"""
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result

# Load configuration
config_data = load_config()

# Create config object that's compatible with old import style
class Config:
    """Configuration object that allows both attribute access and dict-like access"""
    
    def __init__(self, data: Dict[str, Any]):
        self._data = data
        # Set all configuration values as attributes
        for section_name, section_data in data.items():
            setattr(self, section_name, section_data)
    
    def __getitem__(self, key):
        """Allow dict-like access"""
        return self._data[key]
    
    def __contains__(self, key):
        """Allow 'in' operator"""
        return key in self._data
    
    def get(self, key, default=None):
        """Allow get method like dict"""
        if key in self._data:
            return self._data[key]
        return default

# Create the config object (compatible with both old and new styles)
config = Config(config_data)

# Also export individual variables for new code
BOT_TOKEN = config_data["bot"]["token"]
BOT_NAME = config_data["bot"]["name"]
ADMIN_ID = config_data["bot"]["admin_id"]
ADMIN_NAME = config_data["bot"]["admin_name"]

DATABASE_URL = config_data["database"]["url"]
DATA_DIR = config_data["database"]["data_dir"]

LOG_LEVEL = config_data["logging"]["level"]
LOG_TO_FILE = config_data["logging"]["file_logging"]
LOG_TO_CONSOLE = config_data["logging"]["console_logging"]

MAX_WORKERS = config_data["performance"]["max_workers"]
TIMEOUT = config_data["performance"]["timeout"]

# Rate limiting config
RATE_LIMIT_ENABLED = config_data["performance"]["rate_limit"]["enabled"]
RATE_LIMIT_MAX_REQUESTS = config_data["performance"]["rate_limit"]["max_requests"]
RATE_LIMIT_WINDOW = config_data["performance"]["rate_limit"]["window_seconds"]

# Feature toggles
AUTO_UPDATE = config_data["features"]["auto_update"]
UPDATE_CHECK_INTERVAL = config_data["features"]["update_check_interval"]
MAINTENANCE_MODE = config_data["features"]["maintenance_mode"]
USER_TRACKING = config_data["features"]["user_tracking"]
BROADCAST_SYSTEM = config_data["features"]["broadcast_system"]
ADMIN_MANAGEMENT = config_data["features"]["admin_management"]
HOT_RELOAD = config_data["features"]["hot_reload"]

# API keys
YOUTUBE_API_KEY = config_data["apis"]["yt_api_key"]
VERSION_URL = config_data["apis"]["version_url"]
GITHUB_REPO = config_data["apis"]["github_repo"]

# Image spoiler settings
SFW_IMG_SPOILER = config_data["image_spoiler"]["sfw_enabled"]
NSFW_IMG_SPOILER = config_data["image_spoiler"]["nsfw_enabled"]

def get_config() -> Dict[str, Any]:
    """Get the full configuration dictionary"""
    return config_data

def reload_config():
    """Reload configuration from files and environment"""
    global config, config_data, BOT_TOKEN, BOT_NAME, ADMIN_ID, ADMIN_NAME, DATABASE_URL, DATA_DIR
    global LOG_LEVEL, LOG_TO_FILE, LOG_TO_CONSOLE, MAX_WORKERS, TIMEOUT
    global RATE_LIMIT_ENABLED, RATE_LIMIT_MAX_REQUESTS, RATE_LIMIT_WINDOW
    global AUTO_UPDATE, UPDATE_CHECK_INTERVAL, MAINTENANCE_MODE, USER_TRACKING
    global BROADCAST_SYSTEM, ADMIN_MANAGEMENT, HOT_RELOAD, YOUTUBE_API_KEY
    global VERSION_URL, GITHUB_REPO, SFW_IMG_SPOILER, NSFW_IMG_SPOILER
    
    config_data = load_config()
    config = Config(config_data)
    
    # Update exported values
    BOT_TOKEN = config_data["bot"]["token"]
    BOT_NAME = config_data["bot"]["name"]
    ADMIN_ID = config_data["bot"]["admin_id"]
    ADMIN_NAME = config_data["bot"]["admin_name"]
    
    DATABASE_URL = config_data["database"]["url"]
    DATA_DIR = config_data["database"]["data_dir"]
    
    LOG_LEVEL = config_data["logging"]["level"]
    LOG_TO_FILE = config_data["logging"]["file_logging"]
    LOG_TO_CONSOLE = config_data["logging"]["console_logging"]
    
    MAX_WORKERS = config_data["performance"]["max_workers"]
    TIMEOUT = config_data["performance"]["timeout"]
    
    RATE_LIMIT_ENABLED = config_data["performance"]["rate_limit"]["enabled"]
    RATE_LIMIT_MAX_REQUESTS = config_data["performance"]["rate_limit"]["max_requests"]
    RATE_LIMIT_WINDOW = config_data["performance"]["rate_limit"]["window_seconds"]
    
    AUTO_UPDATE = config_data["features"]["auto_update"]
    UPDATE_CHECK_INTERVAL = config_data["features"]["update_check_interval"]
    MAINTENANCE_MODE = config_data["features"]["maintenance_mode"]
    USER_TRACKING = config_data["features"]["user_tracking"]
    BROADCAST_SYSTEM = config_data["features"]["broadcast_system"]
    ADMIN_MANAGEMENT = config_data["features"]["admin_management"]
    HOT_RELOAD = config_data["features"]["hot_reload"]
    
    YOUTUBE_API_KEY = config_data["apis"]["yt_api_key"]
    VERSION_URL = config_data["apis"]["version_url"]
    GITHUB_REPO = config_data["apis"]["github_repo"]
    
    SFW_IMG_SPOILER = config_data["image_spoiler"]["sfw_enabled"]
    NSFW_IMG_SPOILER = config_data["image_spoiler"]["nsfw_enabled"]
