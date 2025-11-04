from aiogram import Bot, Dispatcher
from aiogram.types import FSInputFile
from aiogram.types import Message
import asyncio
import aiohttp
from aiogram import types
from aiogram.filters import Command as CommandFilter

from .logging import logger
from .lang import get_lang
from .handler import commands as cmd_handler
from .handler import message as msg_handler

# Import config and expose it for backward compatibility
try:
    # Import config module to make it available
    import sys
    import os
    
    # Add current directory to path if not already there
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if current_dir not in sys.path:
        sys.path.append(current_dir)
    
    import config as config_module
    
    # Export config for backward compatibility with image commands
    config = config_module.config
    
except ImportError as e:
    # Fallback if config import fails
    logger.warning(f"Could not import config module: {e}")
    config = None

# Global dispatcher instance
dp = Dispatcher()

# Command decorator
commands = {}


def command(cmd_name=None):
    def decorator(func):
        name = cmd_name or func.__name__
        commands[name] = func
        # Store command name for later registration
        func._command_name = name
        return func

    return decorator


# Export commonly used items
__all__ = [
    "Bot",
    "Dispatcher",
    "Message",
    "command",
    "logger",
    "get_lang",
    "config",
    "FSInputFile",
    "types",
    "CommandFilter",
    "aiohttp"
]
