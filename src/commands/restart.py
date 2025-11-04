from core import Message, command, logger, get_lang, config
import os
import sys
import subprocess
import time
import threading
from core.pid_manager import pid_manager

lang = get_lang()


# def help():
#     return {
#         "name": "restart",
#         "version": "2.0.0",
#         "description": "Restart the entire bot application (enhanced with proper process management)",
#         "author": "Komihub",
#         "usage": "/restart",
#     }


def start_bot_process():
    """Start a new bot process with proper environment"""
    python_exe = sys.executable
    script_path = os.path.abspath(sys.argv[0])
    cwd = os.getcwd()
    
    # Create a new environment with all current env vars plus explicit path
    new_env = dict(os.environ)
    
    # Ensure proper Python path
    if 'PYTHONPATH' in new_env:
        new_env['PYTHONPATH'] = f"{cwd}:{new_env['PYTHONPATH']}"
    else:
        new_env['PYTHONPATH'] = cwd
    
    # Add restart environment variable to distinguish new instances
    new_env['BOT_RESTART_INSTANCE'] = str(os.getpid())
    
    restart_cmd = [python_exe, script_path]
    logger.info(f"Starting new bot process: {restart_cmd}")
    logger.info(f"Working directory: {cwd}")
    logger.info(f"Python executable: {python_exe}")
    logger.info(f"Script path: {script_path}")
    
    try:
        return subprocess.Popen(
            restart_cmd,
            cwd=cwd,
            env=new_env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except Exception as e:
        logger.error(f"Failed to start process: {e}")
        raise


def monitor_process_health(process, timeout=10):
    """Monitor if a process starts successfully"""
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        if process.poll() is not None:
            # Process exited
            return False, f"Process exited with code {process.returncode}"
        
        # Check if process is still running
        try:
            if process.returncode is not None:
                return False, f"Process failed with return code {process.returncode}"
        except:
            pass
        
        time.sleep(0.5)
    
    return process.poll() is None, "Process still running"


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
        
        logger.info("🚀 Two-phase restart: Starting new process FIRST...")
        
        # PHASE 1: Start new process BEFORE killing old one
        restart_msg = await restart_msg.edit_text(
            "🔄 <b>Restarting Bot Application...</b>\n\n🚀 Starting new bot instance...",
            parse_mode="HTML",
        )

        try:
            logger.info("🔍 About to call start_bot_process()...")
            new_process = start_bot_process()
            logger.info(f"✅ New process started successfully with PID: {new_process.pid}")
            
            # Monitor process health
            restart_msg = await restart_msg.edit_text(
                "🔄 <b>Restarting Bot Application...</b>\n\n✅ New instance started\n🔍 Checking health...",
                parse_mode="HTML",
            )
            
            is_healthy, status_msg = monitor_process_health(new_process, timeout=15)
            
            if not is_healthy:
                await restart_msg.edit_text(
                    f"❌ <b>New process failed to start!</b>\n\n{status_msg}",
                    parse_mode="HTML",
                )
                logger.error(f"New process health check failed: {status_msg}")
                return

            logger.info("✅ New process passed health check")
            logger.info(f"🔍 Process poll result: {new_process.poll()}")

        except Exception as e:
            await restart_msg.edit_text(
                f"❌ <b>Failed to start new process!</b>\n\nError: {e}",
                parse_mode="HTML",
            )
            logger.error(f"❌ Failed to start new process: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return

        # PHASE 2: Now kill old processes (but only others, not ourselves)
        logger.info("🧹 Now killing old processes (excluding ourselves)...")
        restart_msg = await restart_msg.edit_text(
            "🔄 <b>Restarting Bot Application...</b>\n\n🚀 New instance healthy\n🧹 Stopping old instance...",
            parse_mode="HTML",
        )

        try:
            # Kill all existing bot and server processes EXCEPT ourselves
            killed_count = pid_manager.cleanup_old_instances()  # This doesn't kill current process
            logger.info(f"✅ Killed {killed_count} old processes")
        except Exception as e:
            logger.error(f"❌ Failed to kill processes: {e}")
            await restart_msg.edit_text(
                f"⚠️ <b>Warning:</b> Failed to kill some processes\n\nError: {e}",
                parse_mode="HTML",
            )
            # Don't return - new process is already running

        # Save the new bot PID
        pid_manager.save_bot_pid(new_process.pid)
        logger.info(f"✅ Saved new bot PID: {new_process.pid}")
        
        # Final verification
        if new_process.poll() is None:
            await restart_msg.edit_text(
                f"✅ <b>Bot Restarted Successfully!</b>\n\n🔄 New instance is now running.\n📊 PID: {new_process.pid}\n🌐 Mode: {hosting_mode.upper()}",
                parse_mode="HTML",
            )

            # Give a moment for the message to be seen
            time.sleep(2)

            # Exit current process gracefully
            logger.info("Shutting down current bot process for restart")
            os._exit(0)
        else:
            # New process has exited
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
