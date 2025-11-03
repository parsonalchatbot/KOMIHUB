from core import Message, command, logger, get_lang
from core.config import config
from core.database import db

lang = get_lang()


def help():
    return {
        "name": "add_admin",
        "version": "0.0.1",
        "description": "Add a user as admin",
        "author": "Komihub",
        "usage": "/add_admin [user_id or reply] [admin_type]",
    }


@command("add_admin")
async def add_admin(message: Message):
    # Check if user is owner
    if message.from_user.id != config.ADMIN_ID:
        await message.answer("❌ This command is only available to the owner.")
        return

    logger.info(
        lang.log_command_executed.format(
            command="add_admin", user_id=message.from_user.id
        )
    )

    args = message.text.split()
    admin_types = ["admins", "elders", "gc_admins", "ch_admins"]

    # Get target user
    if message.reply_to_message:
        target_user = message.reply_to_message.from_user
        admin_type = args[1] if len(args) > 1 else "admins"
    else:
        if len(args) < 2:
            await message.answer(
                "Usage: /add_admin [user_id/username or reply] [admin_type]\nAdmin types: admins, elders, gc_admins, ch_admins\n\nDefault admin type: admins (if owner), gc_admins (if gc_admin)"
            )
            return
        try:
            target_input = args[1]
            # Set default admin type based on executor's role
            if len(args) > 2:
                admin_type = args[2]
            elif message.from_user.id == config.ADMIN_ID:
                admin_type = "admins"  # Owner defaults to bot admin
            elif db.is_admin(message.from_user.id, "gc_admins"):
                admin_type = "gc_admins"  # GC admin defaults to gc_admin
            else:
                admin_type = "admins"  # Fallback

            # Try to get user by username or ID
            if target_input.startswith("@"):
                # Username lookup
                username = target_input[1:]  # Remove @
                try:
                    chat_member = await message.bot.get_chat_member(
                        message.chat.id, target_input
                    )
                    target_user = chat_member.user
                    target_user_id = target_user.id
                except Exception:
                    await message.answer(f"User @{username} not found in this chat.")
                    return
            else:
                # Assume it's a user ID
                target_user_id = int(target_input)
                # Create a minimal user object since we don't need full info for adding admin
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

    if admin_type not in admin_types:
        await message.answer(f"Invalid admin type. Available: {', '.join(admin_types)}")
        return

    # Add admin
    if db.add_admin(target_user.id, admin_type):
        role_names = {
            "admins": "Admin",
            "elders": "Elder",
            "gc_admins": "Group Chat Admin",
            "ch_admins": "Channel Admin",
        }

        await message.answer(
            f"✅ <b>Admin Added Successfully!</b>\n\n"
            f"👤 User: {target_user.first_name} {target_user.last_name or ''}\n"
            f"🆔 ID: <code>{target_user.id}</code>\n"
            f"👑 Role: {role_names.get(admin_type, admin_type)}\n\n"
            f"User now has admin privileges!",
            parse_mode="HTML",
        )
        logger.info(f"Added {admin_type} admin: {target_user.id}")
    else:
        await message.answer("❌ User is already an admin of this type.")


@command("remove_admin")
async def remove_admin(message: Message):
    # Check if user is owner
    if message.from_user.id != config.ADMIN_ID:
        await message.answer("❌ This command is only available to the owner.")
        return

    logger.info(
        lang.log_command_executed.format(
            command="remove_admin", user_id=message.from_user.id
        )
    )

    args = message.text.split()
    admin_types = ["admins", "elders", "gc_admins", "ch_admins"]

    # Get target user
    if message.reply_to_message:
        target_user = message.reply_to_message.from_user
        admin_type = args[1] if len(args) > 1 else "admins"
    else:
        if len(args) < 2:
            await message.answer(
                "Usage: /remove_admin [user_id or reply] [admin_type]\nAdmin types: admins, elders, gc_admins, ch_admins"
            )
            return
        try:
            target_input = args[1]
            # Set default admin type based on executor's role
            if len(args) > 2:
                admin_type = args[2]
            elif message.from_user.id == config.ADMIN_ID:
                admin_type = "admins"  # Owner defaults to bot admin
            elif db.is_admin(message.from_user.id, "gc_admins"):
                admin_type = "gc_admins"  # GC admin defaults to gc_admin
            else:
                admin_type = "admins"  # Fallback

            # Try to get user by username or ID
            if target_input.startswith("@"):
                # Username lookup
                username = target_input[1:]  # Remove @
                try:
                    chat_member = await message.bot.get_chat_member(
                        message.chat.id, target_input
                    )
                    target_user = chat_member.user
                    target_user_id = target_user.id
                except Exception:
                    await message.answer(f"User @{username} not found in this chat.")
                    return
            else:
                # Assume it's a user ID
                target_user_id = int(target_input)
                # Create a minimal user object since we don't need full info for removing admin
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

    if admin_type not in admin_types:
        await message.answer(f"Invalid admin type. Available: {', '.join(admin_types)}")
        return

    # Remove admin
    if db.remove_admin(target_user.id, admin_type):
        await message.answer(
            f"✅ <b>Admin Removed Successfully!</b>\n\n"
            f"👤 User: {target_user.first_name} {target_user.last_name or ''}\n"
            f"🆔 ID: <code>{target_user.id}</code>\n\n"
            f"Admin privileges revoked!",
            parse_mode="HTML",
        )
        logger.info(f"Removed {admin_type} admin: {target_user.id}")
    else:
        await message.answer("❌ User is not an admin of this type.")


@command("list_admins")
async def list_admins(message: Message):
    # Check if user is admin
    if not db.is_admin(message.from_user.id):
        await message.answer("❌ This command is only available to administrators.")
        return

    logger.info(
        lang.log_command_executed.format(
            command="list_admins", user_id=message.from_user.id
        )
    )

    admins = db.load_data("admins")

    admin_text = "<b>👑 Bot Administrators</b>\n\n"

    role_names = {
        "owner": "👑 Owner",
        "admins": "⚡ Admins",
        "elders": "🧙 Elders",
        "gc_admins": "👥 Group Chat Admins",
        "ch_admins": "📢 Channel Admins",
    }

    for role_type, user_ids in admins.items():
        if user_ids:
            admin_text += f"<b>{role_names.get(role_type, role_type)}:</b>\n"
            for user_id in user_ids:
                try:
                    user = await message.bot.get_chat_member(message.chat.id, user_id)
                    user = user.user
                    name = f"{user.first_name} {user.last_name or ''}".strip()
                    admin_text += f"• {name} (<code>{user_id}</code>)\n"
                except Exception:
                    # If user not in chat, just show ID
                    admin_text += f"• User {user_id} (<code>{user_id}</code>)\n"
            admin_text += "\n"

    await message.answer(admin_text, parse_mode="HTML")


@command("add_admin_gc")
async def add_admin_gc(message: Message):
    """Add group chat admin - only owner and existing gc_admins can use this"""
    # Check if user is owner or gc_admin
    if message.from_user.id != config.ADMIN_ID and not db.is_admin(
        message.from_user.id, "gc_admins"
    ):
        await message.answer(
            "❌ This command is only available to the owner or group chat admins."
        )
        return

    # Check if this is a group chat
    if message.chat.type not in ["group", "supergroup"]:
        await message.answer("❌ This command can only be used in group chats.")
        return

    logger.info(
        lang.log_command_executed.format(
            command="add_admin_gc", user_id=message.from_user.id
        )
    )

    args = message.text.split()

    # Get target user
    if message.reply_to_message:
        target_user = message.reply_to_message.from_user
    else:
        if len(args) < 2:
            await message.answer(
                "Usage: /add_admin_gc [user_id/username or reply]\nThis command adds group chat admin privileges for this specific group."
            )
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
                    await message.answer("User not found in this group chat.")
                    return
        except ValueError:
            await message.answer("Invalid user ID or username format.")
            return

    # Add as gc_admin
    if db.add_admin(target_user.id, "gc_admins"):
        await message.answer(
            f"✅ <b>Group Chat Admin Added Successfully!</b>\n\n"
            f"👤 User: {target_user.first_name} {target_user.last_name or ''}\n"
            f"🆔 ID: <code>{target_user.id}</code>\n"
            f"👑 Role: Group Chat Admin\n\n"
            f"User now has group chat admin privileges!",
            parse_mode="HTML",
        )
        logger.info(f"Added gc_admin: {target_user.id} in chat {message.chat.id}")
    else:
        await message.answer("❌ User is already a group chat admin.")


@command("remove_admin_gc")
async def remove_admin_gc(message: Message):
    """Remove group chat admin - only owner and existing gc_admins can use this"""
    # Check if user is owner or gc_admin
    if message.from_user.id != config.ADMIN_ID and not db.is_admin(
        message.from_user.id, "gc_admins"
    ):
        await message.answer(
            "❌ This command is only available to the owner or group chat admins."
        )
        return

    # Check if this is a group chat
    if message.chat.type not in ["group", "supergroup"]:
        await message.answer("❌ This command can only be used in group chats.")
        return

    logger.info(
        lang.log_command_executed.format(
            command="remove_admin_gc", user_id=message.from_user.id
        )
    )

    args = message.text.split()

    # Get target user
    if message.reply_to_message:
        target_user = message.reply_to_message.from_user
    else:
        if len(args) < 2:
            await message.answer(
                "Usage: /remove_admin_gc [user_id/username or reply]\nThis command removes group chat admin privileges."
            )
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
                    await message.answer("User not found in this group chat.")
                    return
        except ValueError:
            await message.answer("Invalid user ID or username format.")
            return

    # Remove as gc_admin
    if db.remove_admin(target_user.id, "gc_admins"):
        await message.answer(
            f"✅ <b>Group Chat Admin Removed Successfully!</b>\n\n"
            f"👤 User: {target_user.first_name} {target_user.last_name or ''}\n"
            f"🆔 ID: <code>{target_user.id}</code>\n\n"
            f"Group chat admin privileges revoked!",
            parse_mode="HTML",
        )
        logger.info(f"Removed gc_admin: {target_user.id} from chat {message.chat.id}")
    else:
        await message.answer("❌ User is not a group chat admin.")
