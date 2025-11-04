import aiohttp
import urllib.parse
from core import Message, command, logger, get_lang, FSInputFile

lang = get_lang()

API_URL = "http://2.56.246.81:30170/api/emojimix"


def help():
    return {
        "name": "emojimix",
        "version": "0.0.1",
        "description": "Mix two emojis into a combined image",
        "author": "Komihub", 
        "usage": "/emojimix [emoji1] [emoji2] - Mix two emojis together",
        "examples": [
            "/emojimix 😃🫩",
            "/emojimix 😃 🫩",
            "/emojimix ❤️ 🎉"
        ]
    }


@command("emojimix")
async def emojimix_command(message: Message):
    """Mix two emojis into a combined image"""
    logger.info(
        lang.log_command_executed.format(command="emojimix", user_id=message.from_user.id)
    )

    # Get arguments from command
    args = message.text.split()[1:]  # Remove /emojimix
    
    if len(args) == 0:
        usage_text = """🎨 <b>EmojiMix Command</b>

Mix two emojis into a combined image!

<b>Usage:</b>
/emojimix [emoji1] [emoji2]

<b>Examples:</b>
/emojimix 😃🫩
/emojimix 😃 🫩
/emojimix ❤️ 🎉

<b>Note:</b> You can use emojis with or without spaces between them!"""
        await message.answer(usage_text, parse_mode="HTML")
        return

    # Extract emojis from arguments
    # Handle both "😃🫩" and "😃 🫩" formats
    if len(args) == 1:
        # Single argument: might be "😃🫩" (already combined)
        emoji_text = args[0]
        if len(emoji_text) >= 2:
            emoji1 = emoji_text[0]  # First character
            emoji2 = emoji_text[1]  # Second character
        else:
            await message.answer("❌ Please provide at least 2 emojis!")
            return
    elif len(args) == 2:
        # Two separate arguments
        emoji1 = args[0]
        emoji2 = args[1]
    else:
        # More than 2 emojis - take first two
        emoji1 = args[0]
        emoji2 = args[1]

    # Validate emojis
    if not emoji1 or not emoji2:
        await message.answer("❌ Please provide valid emojis!")
        return

    logger.info(f"EmojiMix: User {message.from_user.id} mixing {emoji1} + {emoji2}")

    # Encode emojis for URL
    emoji1_encoded = urllib.parse.quote(emoji1)
    emoji2_encoded = urllib.parse.quote(emoji2)

    # Build API URL
    api_url = f"{API_URL}?emoji1={emoji1_encoded}&emoji2={emoji2_encoded}"

    try:
        # Make API request
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as resp:
                if resp.status == 200:
                    # Get the image data
                    image_data = await resp.read()
                    
                    # Save temporary file
                    import tempfile
                    import os
                    
                    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
                    temp_file.write(image_data)
                    temp_file.close()
                    
                    # Send the image
                    with open(temp_file.name, 'rb') as f:
                        await message.answer_photo(
                            photo=FSInputFile(temp_file.name),
                            caption=f"🎨 Mixed: {emoji1} + {emoji2}"
                        )
                    
                    # Clean up temporary file
                    os.unlink(temp_file.name)
                    
                    logger.info(f"EmojiMix: Successfully created mix for {emoji1} + {emoji2}")
                else:
                    logger.warning(f"EmojiMix API returned status {resp.status}")
                    await message.answer("❌ Failed to mix emojis. Please try different emojis!")
                    
    except Exception as e:
        logger.error(f"EmojiMix API error: {e}")
        await message.answer("❌ Error mixing emojis. Please try again!")