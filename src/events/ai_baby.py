import aiohttp
from core import Message, logger
from core.bot import bot_instance

API_URL = "http://2.56.246.81:30170/api/simsimi?text="


async def handle_ai_baby(message: Message):
    """AI Baby chat handler"""
    logger.info(f"AI_BABY HANDLER CALLED: {message.from_user.id} - '{message.text}'")
    
    # Only respond if the user is replying to one of the bot's messages
    if not message.reply_to_message:
        return
    
    # Check if the message being replied to is from the bot
    if message.reply_to_message.from_user.id != message.bot.id:
        return

    user_text = message.text.strip()
    if not user_text:
        return

    logger.info(f"AI_BABY: Processing chat request from user {message.from_user.id}: '{user_text}'")
    
    # Fetch AI reply from SimSimi API
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(API_URL + user_text) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    baby_msg = data.get("message", "👶 Goo goo gaa gaa~")
                else:
                    baby_msg = "🥺 Oops! I can't talk right now."
                    logger.warning(f"SimSimi API returned status {resp.status}")
    except Exception as e:
        logger.error(f"Error calling SimSimi API: {e}")
        baby_msg = "🥺 Oops! I can't talk right now."

    await message.answer(baby_msg)
    return


# Register the event handler
try:
    logger.info("AI_BABY: Registering event handler...")
    bot_instance.register_event("message", handle_ai_baby)
    logger.info("AI_BABY: Event handler registered successfully!")
except Exception as e:
    logger.error(f"AI_BABY: Error registering event handler: {e}")