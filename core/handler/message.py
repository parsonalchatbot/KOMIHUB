from ..logging import logger
from ..bot import bot_instance


def load_message_handlers():
    """Load all message handler modules"""
    import os
    import importlib

    handlers_dir = "src/events"
    loaded_count = 0
    failed_count = 0

    for filename in os.listdir(handlers_dir):
        if filename.endswith(".py") and filename != "__init__.py":
            module_name = f"src.events.{filename[:-3]}"
            try:
                importlib.import_module(module_name)
                logger.info(f"Loaded message handler module: {module_name}")
                loaded_count += 1
            except ImportError as e:
                logger.error(f"Failed to load message handler module {module_name}: {e}")
                failed_count += 1
            except Exception as e:
                logger.error(f"Unexpected error loading {module_name}: {e}")
                failed_count += 1

    logger.info(
        f"Message handler loading complete: {loaded_count} loaded, {failed_count} failed"
    )
    return loaded_count, failed_count


def register_message_handlers():
    """Register all message handlers with the bot"""
    # Message handlers are registered automatically when their modules are imported
    # via the bot_instance.register_event() calls in each handler file
    logger.info("Message handlers registered via individual module imports")


def reload_message_handlers():
    """Reload all message handler modules"""
    import os
    import importlib
    import sys

    handlers_dir = "src/events"
    reloaded_count = 0

    for filename in os.listdir(handlers_dir):
        if filename.endswith(".py") and filename != "__init__.py":
            module_name = f"src.events.{filename[:-3]}"
            try:
                if module_name in sys.modules:
                    importlib.reload(sys.modules[module_name])
                else:
                    importlib.import_module(module_name)
                reloaded_count += 1
                logger.debug(f"Reloaded message handler module: {module_name}")
            except Exception as e:
                logger.error(f"Failed to reload message handler module {module_name}: {e}")

    logger.info(f"Reloaded {reloaded_count} message handler modules")
    return reloaded_count