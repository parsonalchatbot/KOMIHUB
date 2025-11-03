from aiogram.types import ChatMemberUpdated
from core import logger, get_lang
from core.database import db

lang = get_lang()


async def on_user_left(chat_member: ChatMemberUpdated):
    """Handle user leaving a group chat"""
    # Only handle group chats
    if chat_member.chat.type not in ["group", "supergroup"]:
        return

    # Check if this is actually a leave event (new status should be 'left' and old status was member/admin)
    if chat_member.new_chat_member.status != "left":
        return  # This is not a leave event

    if chat_member.old_chat_member and chat_member.old_chat_member.status in [
        "member",
        "administrator",
        "creator",
    ]:
        user = chat_member.new_chat_member.user
        user_id = user.id
        chat_id = chat_member.chat.id

        # Update user data in database
        db.update_user(user_id, last_seen=None)  # Mark as left

        # Log the leave event
        logger.info(f"User {user_id} left chat {chat_id}")

        # Send leave message to chat (optional - can be disabled in config)
        try:
            leave_msg = f"👋 <b>{user.first_name or 'User'}</b> left the group"
            if user.username:
                leave_msg += f" (@{user.username})"
            await chat_member.bot.send_message(
                chat_id=chat_id, text=leave_msg, parse_mode="HTML"
            )
        except Exception as e:
            logger.error(f"Failed to send leave message: {e}")

        # Also use the lang format if available
        try:
            logger.info(lang.log_user_left.format(user_id=user_id, chat_id=chat_id))
        except:
            pass


# Register events
from core.bot import bot_instance

bot_instance.register_event("chat_member", on_user_left)
