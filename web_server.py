"""
FastAPI web server for hosting the bot on web services like Render
"""
import os
import json
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global bot instance
bot_instance = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    global bot_instance
    
    # Startup
    logger.info("Starting Telegram Bot Web Server...")
    
    # Import and initialize bot
    try:
        from core.bot import bot_instance as main_bot
        bot_instance = main_bot
        
        # Load commands and events
        from core.handler.commands import load_commands, register_commands
        from core.handler.events import load_events, register_events
        
        loaded, failed = load_commands()
        logger.info(f"Commands loaded: {loaded}, failed: {failed}")
        
        register_commands()
        logger.info("Commands registered")
        
        loaded, failed = load_events()
        logger.info(f"Events loaded: {loaded}, failed: {failed}")
        
        register_events()
        logger.info("Events registered")
        
        logger.info("Bot initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize bot: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down bot server...")

# Create FastAPI app
app = FastAPI(
    title="KOMIHUB Bot",
    description="Telegram Bot Framework",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "KOMIHUB Bot",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "webhook": "/webhook",
            "health": "/health",
            "info": "/info"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for web services"""
    try:
        # Check if bot is initialized
        if bot_instance and hasattr(bot_instance, 'bot'):
            return {
                "status": "healthy",
                "bot_status": "initialized",
                "service": "KOMIHUB Bot"
            }
        else:
            return JSONResponse(
                status_code=503,
                content={
                    "status": "unhealthy",
                    "bot_status": "not_initialized",
                    "service": "KOMIHUB Bot"
                }
            )
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "error",
                "error": str(e),
                "service": "KOMIHUB Bot"
            }
        )

@app.get("/info")
async def bot_info():
    """Bot information endpoint"""
    try:
        if bot_instance and hasattr(bot_instance, 'bot'):
            bot_info = await bot_instance.bot.get_me()
            return {
                "bot_name": bot_info.first_name,
                "bot_username": bot_info.username,
                "bot_id": bot_info.id,
                "supports_inline_queries": bot_info.supports_inline_queries,
                "service": "KOMIHUB Bot"
            }
        else:
            return JSONResponse(
                status_code=503,
                content={"error": "Bot not initialized"}
            )
    except Exception as e:
        logger.error(f"Bot info error: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to get bot info"}
        )

@app.post("/webhook")
async def telegram_webhook(request: Request):
    """Telegram webhook endpoint"""
    try:
        if not bot_instance:
            raise HTTPException(status_code=503, detail="Bot not initialized")
        
        # Get the update data
        update_data = await request.json()
        
        # Process the update
        # Note: This is a simplified webhook handler
        # In a real implementation, you would process the update through the bot's dispatcher
        logger.info(f"Received webhook update: {update_data.get('update_id', 'unknown')}")
        
        return {"status": "ok", "processed": True}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/set_webhook")
async def set_webhook(request: Request):
    """Set webhook endpoint"""
    try:
        if not bot_instance:
            raise HTTPException(status_code=503, detail="Bot not initialized")
        
        data = await request.json()
        webhook_url = data.get("webhook_url")
        
        if not webhook_url:
            raise HTTPException(status_code=400, detail="Webhook URL required")
        
        # Set webhook
        result = await bot_instance.bot.set_webhook(webhook_url)
        
        return {
            "status": "ok",
            "webhook_set": result,
            "url": webhook_url
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Set webhook error: {e}")
        raise HTTPException(status_code=500, detail="Failed to set webhook")

@app.delete("/webhook")
async def delete_webhook(request: Request):
    """Delete webhook endpoint"""
    try:
        if not bot_instance:
            raise HTTPException(status_code=503, detail="Bot not initialized")
        
        result = await bot_instance.bot.delete_webhook()
        
        return {
            "status": "ok",
            "webhook_deleted": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete webhook error: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete webhook")

def main():
    """Main function to run the web server"""
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    uvicorn.run(
        "web_server:app",
        host=host,
        port=port,
        reload=os.getenv("ENVIRONMENT") == "development"
    )

if __name__ == "__main__":
    main()