from core import Message, logger, get_lang
from src.commands.baby import get_simsimi_response

lang = get_lang()


async def on_baby_reply(message: Message):
    """Handle replies to bot's baby messages for continuous chat"""
    # Only handle if this is a reply to the bot
    if not message.reply_to_message or message.reply_to_message.from_user.id != message.bot.id:
        return

    # Check if the replied message is from baby command (contains baby emoji or specific format)
    replied_text = message.reply_to_message.text or ""
    if not (replied_text.startswith("👶") or "baby" in replied_text.lower() or "Baby" in replied_text):
        return

    # Get user's message
    user_text = message.text.strip()
    if not user_text:
        return  # Don't respond to empty messages

    logger.info(f"Baby reply from user {message.from_user.id}: {user_text}")

    # Get response from SimSimi API
    response = await get_simsimi_response(user_text)

    await message.answer(f"👶 {response}")


# Register events
from core.bot import bot_instance

bot_instance.register_event("message", on_baby_reply)