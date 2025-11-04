import aiohttp
from core import Message, command, logger, get_lang, FSInputFile, config

lang = get_lang()

# API endpoints
BASE_URL = "https://api.waifu.pics"

# Available categories
SFW_CATEGORIES = [
    "waifu", "neko", "shinobu", "megumin", "bully", "cuddle", "cry", "hug",
    "awoo", "kiss", "lick", "pat", "smug", "bonk", "yeet", "blush", "smile",
    "wave", "highfive", "handhold", "nom", "bite", "glomp", "slap", "kill",
    "kick", "happy", "wink", "poke", "dance", "cringe"
]

NSFW_CATEGORIES = ["waifu", "neko", "trap", "blowjob"]


def help():
    return {
        "name": "anime_img",
        "version": "0.0.1",
        "description": "Get anime images from Waifu.pics API",
        "author": "Komihub",
        "usage": "/anime_img [category] [-5] [-sfw/nsfw] - Get anime images",
        "examples": [
            "/anime_img list",
            "/anime_img waifu -3",
            "/anime_img kiss -sfw -10",
            "/anime_img cuddle"
        ]
    }


@command("anime_img")
async def anime_img_command(message: Message):
    """Get anime images from Waifu.pics API"""
    logger.info(
        lang.log_command_executed.format(command="anime_img", user_id=message.from_user.id)
    )

    # Get arguments from command
    args = message.text.split()[1:]  # Remove /anime_img
    
    if len(args) == 0:
        usage_text = create_usage_text()
        await message.answer(usage_text)
        return

    # Check if user wants the list
    if args[0].lower() == "list":
        list_text = create_category_list()
        await message.answer(list_text)
        return

    # Parse arguments
    category = None
    content_type = "sfw"  # Default
    limit = 5  # Default
    
    for arg in args:
        if arg.startswith("-"):
            if arg.lower().startswith("-limit:") or arg[1:].isdigit():
                try:
                    if arg.lower().startswith("-limit:"):
                        limit = int(arg.split(":")[1])
                    else:
                        limit = int(arg[1:])  # Remove the - and parse number
                    
                    if limit < 1:
                        limit = 1
                    elif limit > 30:
                        limit = 30  # API max is 30
                except (ValueError, IndexError):
                    await message.answer("❌ Invalid limit format. Use -3 or -limit:number (1-30)")
                    return
            elif arg.lower() in ["-nsfw", "-nsfw:", "-sfw", "-sfw:"]:
                if "nsfw" in arg.lower():
                    content_type = "nsfw"
                else:
                    content_type = "sfw"
            else:
                await message.answer(f"❌ Unknown parameter: {arg}")
                return
        else:
            category = arg.lower()

    # Validate inputs
    if not category:
        await message.answer("❌ Please specify a category!")
        return

    # Check if category exists for the specified content type
    if content_type == "sfw":
        if category not in SFW_CATEGORIES:
            await message.answer(f"❌ Category '{category}' not found in SFW categories!\nUse /anime_img list to see available categories.")
            return
    else:  # nsfw
        if category not in NSFW_CATEGORIES:
            await message.answer(f"❌ Category '{category}' not found in NSFW categories!\nUse /anime_img list to see available categories.")
            return

    logger.info(f"ANIME_IMG: User {message.from_user.id} getting {limit} {content_type} images of category '{category}'")

    # Send waiting message
    waiting_msg = await message.answer(f"🎌 Fetching {limit} {content_type.upper()} {category} images... Please wait!")

    try:
        async with aiohttp.ClientSession() as session:
            if limit == 1:
                # Get single image
                api_url = f"{BASE_URL}/{content_type}/{category}"
                async with session.get(api_url) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if data.get("url"):
                            # Delete waiting message
                            await waiting_msg.delete()
                            
                            # Download and send image
                            await download_and_send_image(session, data["url"], message, f"🎌 {category.title()}", content_type, limit)
                            logger.info(f"ANIME_IMG: Successfully sent 1 image from category {category}")
                        else:
                            await waiting_msg.edit_text("❌ No image returned. Please try again!")
                    else:
                        logger.warning(f"ANIME_IMG API returned status {resp.status}")
                        await waiting_msg.edit_text("❌ Something went wrong. Please try again!")
                        
            else:
                # Get many images
                api_url = f"{BASE_URL}/many/{content_type}/{category}"
                payload = {}
                
                async with session.post(api_url, json=payload) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if data.get("files"):
                            # Delete waiting message
                            await waiting_msg.delete()
                            
                            # Download and send images
                            image_urls = data["files"][:limit]  # Limit to requested amount
                            
                            if len(image_urls) == 1:
                                await download_and_send_image(session, image_urls[0], message, f"🎌 {category.title()}", content_type, len(image_urls))
                            else:
                                # Send as media group if multiple images
                                await send_as_media_group(session, image_urls, message, f"🎌 {category.title()} Images ({len(image_urls)} total)", content_type)
                            
                            logger.info(f"ANIME_IMG: Successfully sent {len(image_urls)} images from category {category}")
                        else:
                            await waiting_msg.edit_text("❌ No images returned. Please try again!")
                    else:
                        logger.warning(f"ANIME_IMG API returned status {resp.status}")
                        await waiting_msg.edit_text("❌ Something went wrong. Please try again!")
                        
    except Exception as e:
        logger.error(f"ANIME_IMG API error: {e}")
        try:
            await waiting_msg.edit_text("❌ Something went wrong. Please try again!")
        except:
            pass


async def download_and_send_image(session, image_url, message, title, content_type="sfw", count=1):
    """Download and send a single image"""
    try:
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
                caption = f"📷 **{title}**\n🎌 Anime Image" if count == 1 else f"📷 **{title}**\n🎌 Anime Image {count}"
                
                # Determine if spoiler should be used
                spoiler = False
                if content_type.lower() == "sfw":
                    spoiler = config.image_spoiler.sfw_enabled if hasattr(config.image_spoiler, 'sfw_enabled') else True
                elif content_type.lower() == "nsfw":
                    spoiler = config.image_spoiler.nsfw_enabled if hasattr(config.image_spoiler, 'nsfw_enabled') else True
                
                with open(temp_file.name, 'rb') as f:
                    await message.answer_photo(
                        photo=FSInputFile(temp_file.name),
                        caption=caption,
                        has_spoiler=spoiler
                    )
                
                # Clean up temporary file
                os.unlink(temp_file.name)
            else:
                await message.answer("❌ Failed to download image.")
                
    except Exception as e:
        logger.error(f"ANIME_IMG: Error downloading/sending image: {e}")
        await message.answer("❌ Error sending image.")


async def send_as_media_group(session, image_urls, message, title, content_type="sfw"):
    """Send multiple images as a media group"""
    import tempfile
    import os
    from aiogram.types import InputMediaPhoto
    
    media_group = []
    temp_files = []
    
    # Determine if spoiler should be used
    spoiler = False
    if content_type.lower() == "sfw":
        spoiler = config.image_spoiler.sfw_enabled if hasattr(config.image_spoiler, 'sfw_enabled') else True
    elif content_type.lower() == "nsfw":
        spoiler = config.image_spoiler.nsfw_enabled if hasattr(config.image_spoiler, 'nsfw_enabled') else True
    
    try:
        for i, img_url in enumerate(image_urls, 1):
            # Download image
            async with session.get(img_url) as img_resp:
                if img_resp.status == 200:
                    image_data = await img_resp.read()
                    
                    # Save temporary file
                    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
                    temp_file.write(image_data)
                    temp_file.close()
                    temp_files.append(temp_file.name)
                    
                    # Create InputMediaPhoto
                    if i == 1:
                        # First image gets the main caption
                        media_group.append(InputMediaPhoto(
                            media=FSInputFile(temp_file.name),
                            caption=f"📷 **{title}**\n🎌 Anime Images",
                            has_spoiler=spoiler
                        ))
                    else:
                        # Other images get simple captions
                        media_group.append(InputMediaPhoto(
                            media=FSInputFile(temp_file.name),
                            caption=f"🎌 Image {i}/{len(image_urls)}",
                            has_spoiler=spoiler
                        ))
                
    except Exception as e:
        logger.error(f"ANIME_IMG: Error processing images: {e}")
        await message.answer("❌ Error processing images. Please try again!")
        return
    
    # Send all images as a media group
    if media_group:
        await message.answer_media_group(media_group)
        
        # Clean up all temporary files
        for temp_file in temp_files:
            try:
                os.unlink(temp_file)
            except:
                pass


def create_usage_text():
    """Create usage instructions text"""
    return """🎌 **Anime Image Generator**

Get anime images from Waifu.pics API!

**Usage:**
/anime_img [category] [-number] [-sfw/nsfw]

**Examples:**
/anime_img list
/anime_img waifu -3
/anime_img kiss -nfw -10
/anime_img cuddle -sfw -1

**Parameters:**
• **Category**: Choose from available categories
• **-number**: Number of images (1-30, default: 5)
• **-sfw/-nsfw**: Content type (default: SFW)

**Note:** Use /anime_img list to see all available categories! 🌟"""


def create_category_list():
    """Create category list text"""
    sfw_list = ", ".join(SFW_CATEGORIES)
    nsfw_list = ", ".join(NSFW_CATEGORIES)
    
    return f"""🎌 **Available Categories**

**SFW Categories:** `{len(SFW_CATEGORIES)} available`
{sfw_list}

**NSFW Categories:** `{len(NSFW_CATEGORIES)} available`
{nsfw_list}

**Usage Examples:**
• /anime_img waifu -3
• /anime_img kiss -sfw -10
• /anime_img cuddle -sfw -1

**Note:** NSFW content requires special permissions! ⚠️"""