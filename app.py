"""
Main application entry point for the KOMIHUB Bot
Supports both polling and webhook modes for different hosting environments
"""
import os
import asyncio
import logging
from typing import Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def print_banner():
    """Print application banner"""
    banner = """
╔══════════════════════════════════════╗
║              KOMIHUB BOT             ║
║        Telegram Bot Framework        ║
╚══════════════════════════════════════╝
"""
    print(banner)
    
    # Get configuration from environment or config file
    bot_name = os.getenv("BOT_NAME", "KOMIHUB BOT")
    admin_name = os.getenv("ADMIN_NAME", "Admin")
    
    print(f"🤖 Bot Name: {bot_name}")
    print(f"👤 Admin: {admin_name}")
    print("=" * 40)

async def run_polling_mode():
    """Run bot in polling mode (for VPS, Termux, local development)"""
    logger.info("Starting bot in polling mode...")
    
    try:
        # Import bot components
        from core.bot import bot_instance
        from core.handler.commands import load_commands, register_commands
        from core.handler.events import load_events, register_events
        from core.handler.message import load_message_handlers
        from core.pid_manager import pid_manager
        import config
        
        print_banner()
        
        # PID management (optional for VPS)
        pid_manager.save_pid()
        killed = pid_manager.cleanup_old_instances()
        if killed > 0:
            print(f"🧹 Cleaned up {killed} old bot instances")
        
        # Load and register commands
        try:
            loaded, failed = load_commands()
            logger.info(f"Commands loaded: {loaded}, failed: {failed}")
            if failed > 0:
                logger.warning(f"{failed} commands failed to load but bot will continue")
        except Exception as e:
            logger.error(f"Critical error loading commands: {e}")
            return False
        
        try:
            register_commands()
            logger.info("Commands registered successfully")
        except Exception as e:
            logger.error(f"Critical error registering commands: {e}")
            return False
        
        # Load and register events
        try:
            loaded, failed = load_events()
            logger.info(f"Events loaded: {loaded}, failed: {failed}")
            if failed > 0:
                logger.warning(f"{failed} events failed to load but bot will continue")
        except Exception as e:
            logger.error(f"Critical error loading events: {e}")
            return False
        
        try:
            register_events()
            logger.info("Events registered successfully")
        except Exception as e:
            logger.error(f"Critical error registering events: {e}")
            return False
        
        # Load and register message handlers
        try:
            loaded, failed = load_message_handlers()
            logger.info(f"Message handlers loaded: {loaded}, failed: {failed}")
            if failed > 0:
                logger.warning(f"{failed} message handlers failed to load but bot will continue")
        except Exception as e:
            logger.error(f"Critical error loading message handlers: {e}")
            return False
        
        # Start polling
        logger.info("Starting bot polling...")
        await bot_instance.start_polling()
        return True
        
    except Exception as e:
        logger.error(f"Critical error during bot polling: {e}")
        return False

async def run_webhook_mode():
    """Run bot in webhook mode (for Render, Heroku, and other web services)"""
    logger.info("Starting bot in webhook mode...")
    
    try:
        # Import and start web server
        import uvicorn
        from web_server import app
        
        port = int(os.getenv("PORT", 8000))
        host = os.getenv("HOST", "0.0.0.0")
        
        print_banner()
        print(f"🌐 Starting web server on {host}:{port}")
        
        config = uvicorn.Config(
            app=app,
            host=host,
            port=port,
            log_level="info",
            access_log=True
        )
        server = uvicorn.Server(config)
        
        logger.info(f"Web server starting on {host}:{port}")
        await server.serve()
        return True
        
    except Exception as e:
        logger.error(f"Critical error during web server: {e}")
        return False

def get_hosting_mode() -> str:
    """
    Determine the hosting mode based on environment variables and configuration
    Returns: 'polling', 'webhook', or 'auto'
    """
    # Check for explicit mode setting
    mode = os.getenv("HOSTING_MODE", "auto").lower()
    
    if mode in ["polling", "webhook", "auto"]:
        if mode != "auto":
            return mode
    
    # Auto-detect mode based on environment
    if os.getenv("PORT"):
        # Web service (Render, Heroku, etc.)
        return "webhook"
    elif os.getenv("WEBHOOK_URL"):
        # Explicit webhook configuration
        return "webhook"
    else:
        # Default to polling for VPS, Termux, local development
        return "polling"

async def main():
    """Main application entry point"""
    mode = get_hosting_mode()
    
    logger.info(f"Hosting mode: {mode}")
    
    if mode == "polling":
        success = await run_polling_mode()
        if not success:
            logger.error("Bot polling failed")
            return False
    elif mode == "webhook":
        success = await run_webhook_mode()
        if not success:
            logger.error("Web server failed")
            return False
    else:
        logger.error(f"Unknown hosting mode: {mode}")
        return False
    
    return True

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        exit(0 if result else 1)
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
        exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        exit(1)