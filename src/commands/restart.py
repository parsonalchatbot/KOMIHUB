from core import Message, command, logger, get_lang, config
import os
import sys
import subprocess
import time
from core.pid_manager import pid_manager

lang = get_lang()


def help():
    return {
        "name": "restart",
        "version": "2.0.0",
        "description": "Restart the entire bot application (enhanced with proper process management)",
        "author": "Komihub",
        "usage": "/restart",
    }


def start_bot_process():
    """Start a new bot process"""
    python_exe = sys.executable
    script_path = os.path.abspath(sys.argv[0])
    cwd = os.getcwd()
    
    restart_cmd = [python_exe, script_path]
    logger.info(f"Starting new bot process: {restart_cmd}")
    
    return subprocess.Popen(restart_cmd, cwd=cwd)


@command("restart")
async def restart(message: Message):
    # Check if user is admin
    if message.from_user.id != config.ADMIN_ID:
        await message.answer("❌ This command is only available to administrators.")
        return

    logger.info(
        lang.log_command_executed.format(
            command="restart", user_id=message.from_user.id
        )
    )

    try:
        # Notify user that restart is starting
        restart_msg = await message.answer(
            "🔄 <b>Restarting Bot Application...</b>\n\n⏳ Shutting down existing processes...",
            parse_mode="HTML",
        )

        # Get hosting mode
        hosting_mode = config.config_data.get("hosting", {}).get("mode", "polling")
        
        restart_msg = await restart_msg.edit_text(
            "🔄 <b>Restarting Bot Application...</b>\n\n🧹 Killing old bot processes...",
            parse_mode="HTML",
        )

        # Kill all existing bot and server processes
        killed_count = pid_manager.kill_all_bot_processes()
        logger.info(f"Killed {killed_count} old processes")

        # Start new process in background
        restart_msg = await restart_msg.edit_text(
            "🔄 <b>Restarting Bot Application...</b>\n\n🚀 Starting new bot instance...",
            parse_mode="HTML",
        )

        try:
            new_process = start_bot_process()
            logger.info(f"New process started with PID: {new_process.pid}")

            # Save the new bot PID
            pid_manager.save_bot_pid(new_process.pid)

        except Exception as e:
            await restart_msg.edit_text(
                f"❌ <b>Failed to start new process!</b>\n\nError: {e}",
                parse_mode="HTML",
            )
            return

        # Wait for the new process to initialize
        restart_msg = await restart_msg.edit_text(
            "🔄 <b>Restarting Bot Application...</b>\n\n⏳ Waiting for new instance to start...",
            parse_mode="HTML",
        )
        time.sleep(5)

        # Check if new process is still running
        if new_process.poll() is None:
            # Process is running
            time.sleep(2)

            await restart_msg.edit_text(
                f"✅ <b>Bot Restarted Successfully!</b>\n\n🔄 New instance is now running.\n📊 PID: {new_process.pid}\n🌐 Mode: {hosting_mode.upper()}\n⏹️ Shutting down old instance...",
                parse_mode="HTML",
            )

            # Give a moment for the message to be seen
            time.sleep(1)

            # Stop the bot polling before exiting
            try:
                from core.bot import bot_instance
                if hasattr(bot_instance, 'dp'):
                    await bot_instance.dp.stop_polling()
            except Exception as e:
                logger.warning(f"Error stopping bot polling: {e}")

            # Exit current process gracefully
            logger.info("Shutting down current bot process for restart")
            os._exit(0)
        else:
            # Process has exited
            exit_code = new_process.returncode
            await restart_msg.edit_text(
                f"❌ <b>Restart Failed!</b>\n\nNew process exited with code: {exit_code}",
                parse_mode="HTML",
            )
            logger.error(f"Restart failed: New process exited with code {exit_code}")

    except Exception as e:
        logger.error(f"Restart error: {e}")
        await message.answer(
            "❌ Failed to restart the application. Check logs for details."
        )
