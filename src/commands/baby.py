
from core import Message, command, logger, get_lang

lang = get_lang()


def help():
    return {
        "name": "baby",
        "version": "0.0.1",
        "description": "Chat with AI baby using SimSimi API",
        "author": "Komihub",
        "usage": "/baby - Start chatting with baby AI",
    }


API_URL = "http://2.56.246.81:30170/api/simsimi?text="


# /baby command handler
@command("baby")
async def baby(message: Message):
    logger.info(
        lang.log_command_executed.format(command="baby", user_id=message.from_user.id)
    )

    greeting = """👶 Hii~ I'm your baby chat bot! 💬

I'm here to chat with you using cute baby language!
Reply to this message to talk with me!

Just say anything and I'll respond like a cute baby! 🥰"""
    await message.answer(greeting)