import aiohttp
import urllib.parse
from core import Message, command, logger, get_lang, FSInputFile, config
import config

lang = get_lang()

base_url = config.API_ULLASH_BASE
API_URL = f"{base_url}/api/dalle4"


def help():
    return {
        "name": "dalle",
        "version": "0.0.1",
        "description": "Generate AI images using DALL-E",
        "author": "Komihub",
        "usage": "/dalle [prompt] - Generate AI images from text prompt",
        "examples": [
            "/dalle komi san",
            "/dalle sunset over mountains",
            "/dalle cute robot in space"
        ]
    }


@command("dalle")
async def dalle_command(message: Message):
    """Generate AI images from text prompt using DALL-E"""
    logger.info(
        lang.log_command_executed.format(command="dalle", user_id=message.from_user.id)
    )

    # Get prompt from command arguments
    args = message.text.split()[1:]  # Remove /dalle
    
    if len(args) == 0:
        usage_text = """🎨 <b>DALL-E Image Generator</b>

Generate AI images from text descriptions!

<b>Usage:</b>
/dalle [prompt]

<b>Examples:</b>
/dalle komi san
/dalle sunset over mountains
/dalle cute robot in space

<b>Note:</b> Be specific for better results! 🌟"""
        await message.answer(usage_text, parse_mode="HTML")
        return

    # Join all arguments to form the prompt
    prompt = " ".join(args)

    if not prompt.strip():
        await message.answer("❌ Please provide a valid prompt!")
        return

    logger.info(f"DALLE: User {message.from_user.id} generating images for: '{prompt}'")

    # Send waiting message
    waiting_msg = await message.answer("⏳ Generating images... Please wait!")

    try:
        # Make API request
        async with aiohttp.ClientSession() as session:
            # Encode prompt for URL
            prompt_encoded = urllib.parse.quote(prompt)
            api_url = f"{API_URL}?prompt={prompt_encoded}"
            
            async with session.get(api_url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    
                    if data.get("status") and data.get("images"):
                        # Delete waiting message
                        await waiting_msg.delete()
                        
                        # Send all images as a batch (media group)
                        images = data["images"]
                        caption_text = f"🎨 Generated images for: <b>{prompt}</b>\n📸 {len(images)} images created"
                        
                        # Download all images and send as media group
                        import tempfile
                        import os
                        from aiogram.types import InputMediaPhoto
                        
                        media_group = []
                        temp_files = []  # Keep track of temp files to clean up
                        
                        # Use SFW spoiler setting for AI generated images
                        spoiler = config.image_spoiler.sfw_enabled if hasattr(config.image_spoiler, 'sfw_enabled') else True
                        
                        try:
                            for i, img_url in enumerate(images, 1):
                                # Download image
                                async with session.get(img_url) as img_resp:
                                    if img_resp.status == 200:
                                        img_data = await img_resp.read()
                                        
                                        # Save temporary file
                                        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
                                        temp_file.write(img_data)
                                        temp_file.close()
                                        temp_files.append(temp_file.name)
                                        
                                        # Create InputMediaPhoto
                                        if i == 1:
                                            # First image gets the main caption
                                            media_group.append(InputMediaPhoto(
                                                media=FSInputFile(temp_file.name),
                                                caption=caption_text,
                                                parse_mode="HTML",
                                                has_spoiler=spoiler
                                            ))
                                        else:
                                            # Other images get simple captions
                                            media_group.append(InputMediaPhoto(
                                                media=FSInputFile(temp_file.name),
                                                caption=f"🖼️ Image {i}/{len(images)}",
                                                has_spoiler=spoiler
                                            ))
                                    
                        except Exception as e:
                            logger.error(f"DALLE: Error processing images: {e}")
                            await message.answer("❌ Error processing images. Please try again!")
                            return
                        
                        # Send all images as a media group
                        if media_group:
                            await message.answer_media_group(media_group)
                            logger.info(f"DALLE: Successfully sent media group with {len(media_group)} images")
                            
                            # Clean up all temporary files
                            for temp_file in temp_files:
                                try:
                                    os.unlink(temp_file)
                                except:
                                    pass
                        
                        logger.info(f"DALLE: Successfully generated {len(images)} images for '{prompt}'")
                    else:
                        # Delete waiting message and send error
                        await waiting_msg.delete()
                        await message.answer("❌ No images generated. Please try a different prompt!")
                        
                else:
                    logger.warning(f"DALLE API returned status {resp.status}")
                    await waiting_msg.edit_text("❌ Something went wrong generating images. Please try again!")
                    
    except Exception as e:
        logger.error(f"DALLE API error: {e}")
        try:
            await waiting_msg.edit_text("❌ Something went wrong. Please try again!")
        except:
            pass