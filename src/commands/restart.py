from core import Message, command, logger, get_lang, config
import os
import sys
import subprocess
import signal
import time
from pathlib import Path

lang = get_lang()


def help():
    return {
        "name": "restart",
        "version": "1.0.0",
        "description": "Restart the entire bot application (supports both web and polling modes)",
        "author": "Komihub",
        "usage": "/restart",
    }


def shutdown_web_server():
    """Gracefully shutdown web server if running"""
    try:
        # Check if port 8000 is in use (web server port)
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', 8000))
        sock.close()
        
        if result == 0:
            logger.info("Web server detected on port 8000, sending graceful shutdown signal...")
            
            # Try to send SIGTERM to web server process
            try:
                import psutil
                for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                    if 'app.py' in proc.info['cmdline'] or 'uvicorn' in proc.info['name']:
                        logger.info(f"Terminating web server process {proc.info['pid']}")
                        proc.terminate()
                        proc.wait(timeout=5)
                        break
            except Exception as e:
                logger.warning(f"Could not terminate web server gracefully: {e}")
    except Exception as e:
        logger.warning(f"Error checking for web server: {e}")


def restart_bot_process():
    """Start a new bot process with appropriate mode"""
    python_exe = sys.executable
    script_path = os.path.abspath(sys.argv[0])
    cwd = os.getcwd()
    
    # Determine restart command based on hosting mode
    restart_cmd = [python_exe, script_path]
    
    # Check hosting mode to determine restart strategy
    hosting_mode = config.config_data.get("hosting", {}).get("mode", "auto")
    
    if hosting_mode == "webhook" or hosting_mode == "auto":
        # For web hosting, just restart the app
        logger.info(f"Starting new bot process (web mode): {restart_cmd}")
        return subprocess.Popen(restart_cmd, cwd=cwd)
    else:
        # For polling mode, same as before
        logger.info(f"Starting new bot process (polling mode): {restart_cmd}")
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
            "🔄 <b>Restarting Bot Application...</b>\n\n⏳ Initializing restart process...",
            parse_mode="HTML",
        )

        # Check if this might be a web server
        hosting_mode = config.config_data.get("hosting", {}).get("mode", "auto")
        
        if hosting_mode in ["webhook", "auto"]:
            restart_msg = await restart_msg.edit_text(
                "🔄 <b>Restarting Bot Application...</b>\n\n🌐 Detected web hosting mode\n⏳ Shutting down web server...",
                parse_mode="HTML",
            )
            
            # Gracefully shutdown web server
            shutdown_web_server()
            
            # Wait for web server to shut down
            time.sleep(3)

        # Start new process in background
        logger.info("Starting new bot process...")
        try:
            new_process = restart_bot_process()
            logger.info(f"New process started with PID: {new_process.pid}")

            # Save the new PID
            from core.pid_manager import pid_manager
            pid_manager.save_pid(new_process.pid)

        except Exception as e:
            await restart_msg.edit_text(
                f"❌ <b>Failed to start new process!</b>\n\nError: {e}",
                parse_mode="HTML",
            )
            return

        # Wait for the new process to initialize
        time.sleep(5)

        # Check if new process is still running
        if new_process.poll() is None:
            # Process is running, wait a bit more for it to fully start
            time.sleep(2)

            await restart_msg.edit_text(
                f"✅ <b>Bot Restarted Successfully!</b>\n\n🔄 New instance is now running.\n🌐 Hosting Mode: {hosting_mode.upper()}\n⏹️ Shutting down old instance...",
                parse_mode="HTML",
            )

            # Give a moment for the message to be seen
            time.sleep(1)

            # Stop the bot polling before exiting
            from core.bot import bot_instance

            # Check if bot instance exists and has dp attribute
            if hasattr(bot_instance, 'dp'):
                await bot_instance.dp.stop_polling()

            # If this is a web server, also stop it gracefully
            if hosting_mode in ["webhook", "auto"]:
                try:
                    # Try to shut down web server gracefully
                    shutdown_web_server()
                except Exception as e:
                    logger.warning(f"Error during web server shutdown: {e}")

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
