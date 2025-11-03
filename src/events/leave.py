from aiogram.types import ChatMemberUpdated
from core import logger, get_lang
from core.database import db

lang = get_lang()


async def on_user_left(chat_member: ChatMemberUpdated):
    """Handle user leaving a group chat"""
    # Only handle group chats
    if chat_member.chat.type not in ["group", "supergroup"]:
        return

    if chat_member.new_chat_member.status == "left":
        user = chat_member.new_chat_member.user
        user_id = user.id
        chat_id = chat_member.chat.id

        # Update user data in database
        db.update_user(user_id, last_seen=None)  # Mark as left

        # Log the leave event
        logger.info(lang.log_user_left.format(user_id=user_id, chat_id=chat_id))


# Register events
from core.bot import bot_instance

bot_instance.register_event("chat_member", on_user_left)
