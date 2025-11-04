import aiohttp
import urllib.parse
from core import Message, command, logger, get_lang, FSInputFile, config

lang = get_lang()

API_URL = "http://2.56.246.81:30170/api/animagine"


def help():
    return {
        "name": "img_ai2",
        "version": "0.0.1",
        "description": "Generate AI images using Animagine API with ratio support",
        "author": "Komihub",
        "usage": "/img_ai2 [prompt] - Generate AI image from text prompt",
        "examples": [
            "/img_ai2 komi san",
            "/img_ai2 cute anime girl 16:9",
            "/img_ai2 futuristic city"
        ]
    }


@command("img_ai2")
async def img_ai2_command(message: Message):
    """Generate AI image from text prompt using Animagine API with ratio support"""
    logger.info(
        lang.log_command_executed.format(command="img_ai2", user_id=message.from_user.id)
    )

    # Get arguments from command
    args = message.text.split()[1:]  # Remove /img_ai2
    
    if len(args) == 0:
        usage_text = """🎨 <b>Animagine AI Image Generator</b>

Generate high-quality AI images using Animagine API!

<b>Usage:</b>
/img_ai2 [prompt] [ratio]

<b>Examples:</b>
/img_ai2 komi san
/img_ai2 cute anime girl 16:9
/img_ai2 futuristic city 1:1

<b>Available Ratios:</b>
• 16:9 (widescreen)
• 9:16 (portrait)
• 1:1 (square)
• 4:3 (classic)

<b>Note:</b> Ratio is optional, defaults to 1:1! 🌟"""
        await message.answer(usage_text, parse_mode="HTML")
        return

    # Extract prompt and optional ratio
    prompt_parts = []
    ratio = "1:1"  # Default ratio
    
    for arg in args:
        # Check if this looks like a ratio (contains ":" and numbers)
        if ":" in arg and any(c.isdigit() for c in arg) and not any(c.isalpha() for c in arg.replace(":", "")):
            ratio = arg
        else:
            prompt_parts.append(arg)
    
    # Join prompt parts
    prompt = " ".join(prompt_parts).strip()

    if not prompt:
        await message.answer("❌ Please provide a valid prompt!")
        return

    logger.info(f"IMG_AI2: User {message.from_user.id} generating image for: '{prompt}' (ratio: {ratio})")

    # Send waiting message
    waiting_msg = await message.answer("🎨 Generating Animagine image... Please wait!")

    try:
        # Make API request
        async with aiohttp.ClientSession() as session:
            # Encode parameters for URL
            prompt_encoded = urllib.parse.quote(prompt)
            ratio_encoded = urllib.parse.quote(ratio)
            api_url = f"{API_URL}?prompt={prompt_encoded}&ratio={ratio_encoded}"
            
            logger.info(f"IMG_AI2: API URL: {api_url}")
            
            async with session.get(api_url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    
                    if data.get("image"):
                        # Delete waiting message
                        await waiting_msg.delete()
                        
                        # Get image URL
                        image_url = data["image"]
                        
                        # Download the image
                        async with session.get(image_url) as img_resp:
                            if img_resp.status == 200:
                                image_data = await img_resp.read()
                                
                                # Save temporary file
                                import tempfile
                                import os
                                
                                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
                                temp_file.write(image_data)
                                temp_file.close()
                                
                                # Send the image
                                caption_text = f"🎨 <b>Animagine Generated</b>\n\n🎯 <b>Prompt:</b> {prompt}\n📐 <b>Ratio:</b> {ratio}"

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
                                
                                logger.info(f"IMG_AI2: Successfully generated image for '{prompt}' (ratio: {ratio})")
                            else:
                                logger.error(f"IMG_AI2: Failed to download image from {image_url}")
                                await waiting_msg.edit_text("❌ Failed to download generated image. Please try again!")
                                
                    else:
                        logger.warning(f"IMG_AI2: No image in API response: {data}")
                        await waiting_msg.edit_text("❌ No image generated. Please try a different prompt!")
                        
                else:
                    logger.warning(f"IMG_AI2 API returned status {resp.status}")
                    text = await resp.text()
                    logger.warning(f"IMG_AI2 API response: {text}")
                    await waiting_msg.edit_text("❌ Something went wrong generating image. Please try again!")
                    
    except Exception as e:
        logger.error(f"IMG_AI2 API error: {e}")
        try:
            await waiting_msg.edit_text("❌ Something went wrong. Please try again!")
        except:
            pass