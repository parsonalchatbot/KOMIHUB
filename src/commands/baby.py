from core import Message, command, logger, get_lang
import aiohttp
import json

lang = get_lang()


def help():
    return {
        "name": "baby",
        "version": "0.0.1",
        "description": "Chat with AI baby using SimSimi API",
        "author": "Komihub",
        "usage": "/baby [message] or reply to bot's baby message",
    }


async def get_simsimi_response(text: str) -> str:
    """Get response from SimSimi API"""
    url = "http://2.56.246.81:30170/api/simsimi"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params={"text": text}) as response:
                if response.status == 200:
                    data = await response.json()
                    if "message" in data:
                        return data["message"]
                    else:
                        return "Sorry, I couldn't understand that. 💕"
                else:
                    return "Baby is sleeping right now. 😴"
    except Exception as e:
        logger.error(f"SimSimi API error: {e}")
        return "Baby is having trouble talking. 😢"


@command("baby")
async def baby(message: Message):
    logger.info(
        lang.log_command_executed.format(command="baby", user_id=message.from_user.id)
    )

    # Get text from command arguments
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        # Send initial greeting message that users can reply to
        greeting_msg = await message.answer(
            "👶 <b>Hi! I'm Baby!</b> 💕\n\n"
            "Reply to this message to start chatting with me!"
        )
        return

    user_text = args[1].strip()
    if not user_text:
        await message.answer("Please tell baby something! 💕")
        return

    # Get response from SimSimi API
    response = await get_simsimi_response(user_text)

    await message.answer(f"👶 {response}")