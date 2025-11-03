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
