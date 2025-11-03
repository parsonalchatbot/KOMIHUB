from aiogram.types import ChatMemberUpdated
from core import logger, get_lang
from core.database import db

lang = get_lang()


async def on_user_join(chat_member: ChatMemberUpdated):
    """Handle user joining a group chat"""
    # Only handle group chats
    if chat_member.chat.type not in ["group", "supergroup"]:
        return

    # Check if this is actually a join event (old_chat_member should be None or different status)
    if chat_member.old_chat_member and chat_member.old_chat_member.status in [
        "member",
        "administrator",
        "creator",
    ]:
        return  # This is not a join event

    if chat_member.new_chat_member.status in ["member", "administrator", "creator"]:
        user = chat_member.new_chat_member.user
        user_id = user.id
        chat_id = chat_member.chat.id

        # Add user to database
        user_data = {
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
        }
        db.add_user(user_id, user_data)

        # Log the join event
        logger.info(f"User {user_id} joined chat {chat_id}")

        # Send welcome message to chat (optional - can be disabled in config)
        try:
            welcome_msg = f"👋 <b>{user.first_name or 'User'}</b> joined the group"
            if user.username:
                welcome_msg += f" (@{user.username})"
            await chat_member.bot.send_message(
                chat_id=chat_id, text=welcome_msg, parse_mode="HTML"
            )
        except Exception as e:
            logger.error(f"Failed to send welcome message: {e}")

        # Also use the lang format if available
        try:
            logger.info(lang.log_user_joined.format(user_id=user_id, chat_id=chat_id))
        except:
            pass

        # Check if user is banned
        if db.is_banned(user_id):
            try:
                await chat_member.bot.ban_chat_member(chat_id, user_id)
                logger.info(
                    f"Auto-banned previously banned user {user_id} in chat {chat_id}"
                )
            except Exception as e:
                logger.error(f"Failed to auto-ban user {user_id}: {e}")


# Register events
from core.bot import bot_instance

bot_instance.register_event("chat_member", on_user_join)
