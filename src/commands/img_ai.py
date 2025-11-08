import aiohttp
import urllib.parse
from core import Message, command, logger, get_lang, FSInputFile, config
import config

lang = get_lang()

base_url = config.API_ULLASH_BASE
API_URL = f"{base_url}/api/magic"


def help():
    return {
        "name": "img_ai",
        "version": "0.0.1",
        "description": "Generate AI images using Magic API",
        "author": "Komihub",
        "usage": "/img_ai [prompt] - Generate AI image from text prompt",
        "examples": [
            "/img_ai cute anime girl",
            "/img_ai sunset landscape",
            "/img_ai futuristic city"
        ]
    }


@command("img_ai")
async def img_ai_command(message: Message):
    """Generate AI image from text prompt using Magic API"""
    logger.info(
        lang.log_command_executed.format(command="img_ai", user_id=message.from_user.id)
    )

    # Get prompt from command arguments
    args = message.text.split()[1:]  # Remove /img_ai
    
    if len(args) == 0:
        usage_text = """🪄 <b>Magic AI Image Generator</b>

Generate AI images using advanced Magic API!

<b>Usage:</b>
/img_ai [prompt]

<b>Examples:</b>
/img_ai cute anime girl
/img_ai sunset landscape
/img_ai futuristic city

<b>Note:</b> Be detailed for the best results! 🌟"""
        await message.answer(usage_text, parse_mode="HTML")
        return

    # Join all arguments to form the prompt
    prompt = " ".join(args)

    if not prompt.strip():
        await message.answer("❌ Please provide a valid prompt!")
        return

    logger.info(f"IMG_AI: User {message.from_user.id} generating image for: '{prompt}'")

    # Send waiting message
    waiting_msg = await message.answer("🪄 Generating magical image... Please wait!")

    try:
        # Make API request
        async with aiohttp.ClientSession() as session:
            # Encode prompt for URL
            prompt_encoded = urllib.parse.quote(prompt)
            api_url = f"{API_URL}?prompt={prompt_encoded}"
            
            async with session.get(api_url) as resp:
                if resp.status == 200:
                    # Get the image data
                    image_data = await resp.read()
                    
                    # Delete waiting message
                    await waiting_msg.delete()
                    
                    # Save temporary file
                    import tempfile
                    import os
                    
                    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
                    temp_file.write(image_data)
                    temp_file.close()
                    
                    # Send the image
                    caption_text = f"🪄 <b>Magic AI Generated</b>\n\n🎨 <b>Prompt:</b> {prompt}"

                    # Use SFW spoiler setting for AI generated images
                    spoiler = config.image_spoiler.sfw_enabled if hasattr(config.image_spoiler, 'sfw_enabled') else True

                    with open(temp_file.name, 'rb') as f:
                        await message.answer_photo(
                            photo=FSInputFile(temp_file.name),
                            caption=caption_text,
                            parse_mode="HTML",
                            has_spoiler=spoiler
                        )
                    
                    # Clean up temporary file
                    os.unlink(temp_file.name)
                    
                    logger.info(f"IMG_AI: Successfully generated image for '{prompt}'")
                else:
                    logger.warning(f"IMG_AI API returned status {resp.status}")
                    await waiting_msg.edit_text("❌ Something went wrong generating image. Please try again!")
                    
    except Exception as e:
        logger.error(f"IMG_AI API error: {e}")
        try:
            await waiting_msg.edit_text("❌ Something went wrong. Please try again!")
        except:
            pass