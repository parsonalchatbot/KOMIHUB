import asyncio
import os
from aiogram import Bot, Dispatcher
from aiogram.types import Message, Update
from aiogram.filters import Command
from .logging import logger
from .lang import get_lang
from .database import db
from .middleware import UserMiddleware
import config


class KomihubBot:
    def __init__(self):
        self.bot = Bot(token=config.BOT_TOKEN)
        self.dp = Dispatcher()
        self.lang = get_lang()
        self.webhook_url = os.getenv("WEBHOOK_URL")
        self.hosting_mode = os.getenv("HOSTING_MODE", "auto")
        self.webhook_setup_done = False

        # Register middleware
        self.dp.message.middleware.register(UserMiddleware())

    async def start_polling(self):
        # Register unknown command handler
        self.dp.message.register(self.handle_unknown_command)

        # Update bot stats
        db.update_bot_stats(
            bot_name=config.BOT_NAME, online_since=asyncio.get_event_loop().time()
        )

        logger.info(self.lang.log_bot_started)
        await self.dp.start_polling(self.bot)

    async def process_update(self, update: Update):
        """Process a single update (for webhook mode)"""
        try:
            await self.dp.feed_update(self.bot, update)
        except Exception as e:
            logger.error(f"Error processing update {getattr(update, 'update_id', 'unknown')}: {e}")

    async def setup_webhook(self):
        """Setup webhook if configured"""
        if not self.webhook_url:
            logger.info("No webhook URL configured, skipping webhook setup")
            return False

        try:
            webhook_info = await self.bot.get_webhook_info()
            if webhook_info.url != self.webhook_url:
                await self.bot.set_webhook(self.webhook_url)
                logger.info(f"Webhook set to: {self.webhook_url}")
            else:
                logger.info("Webhook already configured correctly")
            return True
        except Exception as e:
            logger.error(f"Failed to setup webhook: {e}")
            return False

    async def remove_webhook(self):
        """Remove webhook"""
        try:
            await self.bot.delete_webhook()
            logger.info("Webhook deleted")
            return True
        except Exception as e:
            logger.error(f"Failed to delete webhook: {e}")
            return False

    async def get_bot_info(self):
        """Get bot information"""
        try:
            return await self.bot.get_me()
        except Exception as e:
            logger.error(f"Failed to get bot info: {e}")
            return None

    def register_command(self, command_name, handler):
        try:
            self.dp.message.register(handler, Command(command_name))
            logger.debug(f"Successfully registered command: {command_name}")
        except Exception as e:
            logger.error(f"Failed to register command {command_name}: {e}")
            raise

    def register_event(self, event_type, handler):
        if event_type == "chat_member":
            self.dp.chat_member.register(handler)
        elif event_type == "message":
            # Register message handler without command filter to catch all messages
            self.dp.message.register(handler)
        # Add more event types as needed

    async def handle_unknown_command(self, message: Message):
        """Handle unknown commands"""
        try:
            from src.commands.unknown import handle_unknown_command

            await handle_unknown_command(message)
        except Exception as e:
            logger.error(f"Error in unknown command handler: {e}")
            # Fallback response
            await message.answer(
                "❓ Unknown command. Use /help to see available commands."
            )


bot_instance = KomihubBot()
