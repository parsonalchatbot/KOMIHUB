from core import Message, command, logger, get_lang
from core.database import db
from aiogram.exceptions import TelegramBadRequest

lang = get_lang()


def help():
    return {
        "name": "ban",
        "version": "0.0.1",
        "description": "Ban a user from the chat",
        "author": "Komihub",
        "usage": "/ban [user_id or reply to message] [reason]",
    }


@command("ban")
async def ban(message: Message):
    logger.info(
        lang.log_command_executed.format(command="ban", user_id=message.from_user.id)
    )

    # Check if user is admin (using database or telegram permissions)
    if not db.is_admin(message.from_user.id):
        try:
            user_member = await message.bot.get_chat_member(
                message.chat.id, message.from_user.id
            )
            if user_member.status not in ["administrator", "creator"]:
                await message.answer(lang.no_rights_to_ban_user)
                return
        except Exception:
            await message.answer(lang.unknown_error)
            return

    # Get target user
    if message.reply_to_message:
        target_user = message.reply_to_message.from_user
        reason = (
            message.text.split(" ", 1)[1]
            if len(message.text.split(" ", 1)) > 1
            else "No reason provided"
        )
    else:
        args = message.text.split()
        if len(args) < 2:
            await message.answer("Usage: /ban [user_id/username or reply] [reason]")
            return
        try:
            target_input = args[1]

            # Try to get user by username or ID
            if target_input.startswith("@"):
                # Username lookup
                username = target_input[1:]  # Remove @
                try:
                    chat_member = await message.bot.get_chat_member(
                        message.chat.id, target_input
                    )
                    target_user = chat_member.user
                except Exception:
                    await message.answer(f"User @{username} not found in this chat.")
                    return
            else:
                # Assume it's a user ID
                target_user_id = int(target_input)
                try:
                    chat_member = await message.bot.get_chat_member(
                        message.chat.id, target_user_id
                    )
                    target_user = chat_member.user
                except Exception:
                    await message.answer("User not found in this chat.")
                    return

            reason = " ".join(args[2:]) if len(args) > 2 else "No reason provided"
        except ValueError:
            await message.answer("Invalid user ID or username format.")
            return

    # Ban the user and update database
    try:
        await message.bot.ban_chat_member(message.chat.id, target_user.id)
        # Add to database ban list
        db.ban_user(target_user.id, reason, message.from_user.id)
        await message.answer(
            f"✅ <b>User Banned Successfully!</b>\n\n"
            f"👤 User: {target_user.first_name} {target_user.last_name or ''}\n"
            f"🆔 ID: <code>{target_user.id}</code>\n"
            f"📝 Reason: {reason}\n\n"
            f"User has been banned from this chat!",
            parse_mode="HTML",
        )
        logger.info(
            f"Banned user {target_user.id} from chat {message.chat.id} for: {reason}"
        )
    except TelegramBadRequest as e:
        await message.answer(f"Failed to ban user: {e}")
    except Exception as e:
        await message.answer(lang.unknown_error)
        logger.error(f"Ban error: {e}")


@command("unban")
async def unban(message: Message):
    logger.info(
        lang.log_command_executed.format(command="unban", user_id=message.from_user.id)
    )

    # Check if user is admin (using database or telegram permissions)
    if not db.is_admin(message.from_user.id):
        try:
            user_member = await message.bot.get_chat_member(
                message.chat.id, message.from_user.id
            )
            if user_member.status not in ["administrator", "creator"]:
                await message.answer("❌ You don't have rights to unban users.")
                return
        except Exception:
            await message.answer(lang.unknown_error)
            return

    # Get target user
    if message.reply_to_message:
        target_user = message.reply_to_message.from_user
    else:
        args = message.text.split()
        if len(args) < 2:
            await message.answer("Usage: /unban [user_id/username or reply]")
            return
        try:
            target_input = args[1]

            # Try to get user by username or ID
            if target_input.startswith("@"):
                # Username lookup
                username = target_input[1:]  # Remove @
                try:
                    chat_member = await message.bot.get_chat_member(
                        message.chat.id, target_input
                    )
                    target_user = chat_member.user
                except Exception:
                    await message.answer(f"User @{username} not found in this chat.")
                    return
            else:
                # Assume it's a user ID
                target_user_id = int(target_input)
                # Create a minimal user object since we don't need full info for unbanning
                target_user = type(
                    "User",
                    (),
                    {
                        "id": target_user_id,
                        "first_name": f"User {target_user_id}",
                        "last_name": "",
                    },
                )()
        except ValueError:
            await message.answer("Invalid user ID or username format.")
            return

    # Unban the user and update database
    try:
        await message.bot.unban_chat_member(message.chat.id, target_user.id)
        # Remove from database ban list
        if db.unban_user(target_user.id):
            await message.answer(
                f"✅ <b>User Unbanned Successfully!</b>\n\n"
                f"👤 User: {target_user.first_name} {target_user.last_name or ''}\n"
                f"🆔 ID: <code>{target_user.id}</code>\n\n"
                f"User has been unbanned from this chat!",
                parse_mode="HTML",
            )
            logger.info(f"Unbanned user {target_user.id} from chat {message.chat.id}")
        else:
            await message.answer(
                f"✅ <b>User Unbanned from Chat!</b>\n\n"
                f"👤 User: {target_user.first_name} {target_user.last_name or ''}\n"
                f"🆔 ID: <code>{target_user.id}</code>\n\n"
                f"Note: User was not in the bot's ban database.",
                parse_mode="HTML",
            )
    except TelegramBadRequest as e:
        await message.answer(f"Failed to unban user: {e}")
    except Exception as e:
        await message.answer(lang.unknown_error)
        logger.error(f"Unban error: {e}")


@command("ban_info")
async def ban_info(message: Message):
    """Get ban information for a user"""
    # Check if user is admin
    if not db.is_admin(message.from_user.id):
        try:
            user_member = await message.bot.get_chat_member(
                message.chat.id, message.from_user.id
            )
            if user_member.status not in ["administrator", "creator"]:
                await message.answer(
                    "❌ You don't have rights to view ban information."
                )
                return
        except Exception:
            await message.answer(lang.unknown_error)
            return

    args = message.text.split()
    if len(args) < 2:
        await message.answer("Usage: /ban_info [user_id]")
        return

    try:
        target_user_id = int(args[1])
        ban_data = db.get_ban_info(target_user_id)

        if ban_data:
            banned_at = ban_data.get("banned_at", 0)
            reason = ban_data.get("reason", "No reason provided")
            banned_by = ban_data.get("banned_by", "Unknown")

            await message.answer(
                f"🚫 <b>Ban Information</b>\n\n"
                f"🆔 User ID: <code>{target_user_id}</code>\n"
                f"📅 Banned At: {banned_at}\n"
                f"👤 Banned By: <code>{banned_by}</code>\n"
                f"📝 Reason: {reason}",
                parse_mode="HTML",
            )
        else:
            await message.answer("❌ User is not banned in the database.")
    except ValueError:
        await message.answer("Invalid user ID.")
    except Exception as e:
        await message.answer(lang.unknown_error)
        logger.error(f"Ban info error: {e}")
