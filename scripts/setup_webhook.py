#!/usr/bin/env python3
"""
Webhook setup script for KOMIHUB Bot
This script validates environment variables and sets up webhook URL automatically
"""
import os
import asyncio
import requests
import json
from pathlib import Path

def get_render_url():
    """Get the Render service URL"""
    # Render automatically provides RENDER_EXTERNAL_HOSTNAME
    hostname = os.getenv("RENDER_EXTERNAL_HOSTNAME")
    if not hostname:
        print("❌ RENDER_EXTERNAL_HOSTNAME not found in environment variables")
        print("Make sure your service is deployed on Render")
        return None
    
    # Use HTTPS and the correct webhook endpoint
    webhook_url = f"https://{hostname}/webhook"
    return webhook_url

def validate_env_vars():
    """Validate required environment variables"""
    required_vars = [
        "BOT_TOKEN",
        "WEBHOOK_URL"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        return False
    
    print("✅ All required environment variables are set")
    return True

def print_webhook_info(webhook_url):
    """Print webhook configuration info"""
    print("\n🔗 Webhook Configuration:")
    print(f"   Webhook URL: {webhook_url}")
    print(f"   Token: {os.getenv('BOT_TOKEN', 'Not set')}")
    print(f"   Hosting Mode: {os.getenv('HOSTING_MODE', 'auto')}")
    print(f"   Port: {os.getenv('PORT', '8000')}")
    print(f"   Host: {os.getenv('HOST', '0.0.0.0')}")

async def test_webhook_endpoint(webhook_url):
    """Test if webhook endpoint is accessible"""
    try:
        # Test with a simple GET request
        response = requests.get(webhook_url.replace('/webhook', '/health'), timeout=10)
        if response.status_code == 200:
            print("✅ Webhook endpoint is accessible")
            return True
        else:
            print(f"⚠️  Health check returned status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot access webhook endpoint: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 KOMIHUB Bot Webhook Setup")
    print("=" * 40)
    
    # Validate environment variables
    if not validate_env_vars():
        return False
    
    # Get webhook URL
    webhook_url = os.getenv("WEBHOOK_URL")
    
    # If using Render, auto-generate webhook URL
    if webhook_url == "https://your-domain.com/webhook" or not webhook_url:
        print("\n🔄 Auto-generating webhook URL for Render...")
        render_url = get_render_url()
        if render_url:
            webhook_url = render_url
            print(f"✅ Generated webhook URL: {webhook_url}")
    
    if not webhook_url:
        print("❌ No valid webhook URL configured")
        return False
    
    # Print configuration
    print_webhook_info(webhook_url)
    
    # Test endpoint accessibility
    print("\n🌐 Testing webhook endpoint...")
    endpoint_test = asyncio.run(test_webhook_endpoint(webhook_url))
    
    # Instructions for manual setup
    print("\n📋 Manual Setup Instructions:")
    print("1. Deploy your bot to Render")
    print("2. Get your service URL from Render dashboard")
    print("3. Set WEBHOOK_URL environment variable to:")
    print(f"   {webhook_url}")
    print("4. Restart your service")
    print("5. Send /start command to your bot to test")
    
    if endpoint_test:
        print("\n✅ Setup completed successfully!")
        print("Your bot should now respond to webhooks from Telegram.")
    else:
        print("\n⚠️  Setup completed but endpoint test failed.")
        print("Make sure your service is deployed and accessible.")
    
    return True

if __name__ == "__main__":
    main()