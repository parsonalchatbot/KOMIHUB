#!/usr/bin/env python3
"""
Automatic webhook URL setter for Render deployment
This script sets the correct webhook URL based on the Render environment
"""
import os
import sys

def get_render_webhook_url():
    """Generate webhook URL for Render deployment"""
    # Get Render's external hostname
    hostname = os.getenv("RENDER_EXTERNAL_HOSTNAME")
    if not hostname:
        print("❌ RENDER_EXTERNAL_HOSTNAME not found")
        print("This script should be run in a Render environment")
        return None
    
    # Construct webhook URL
    webhook_url = f"https://{hostname}/webhook"
    return webhook_url

def set_webhook_url_env():
    """Set webhook URL in environment"""
    webhook_url = get_render_webhook_url()
    if webhook_url:
        # Set environment variable
        os.environ["WEBHOOK_URL"] = webhook_url
        print(f"✅ Webhook URL set: {webhook_url}")
        return webhook_url
    return None

def print_deployment_info():
    """Print deployment information"""
    print("🌐 Render Deployment Information:")
    print(f"   Hostname: {os.getenv('RENDER_EXTERNAL_HOSTNAME', 'Not found')}")
    print(f"   Service Name: {os.getenv('RENDER_SERVICE_NAME', 'Not found')}")
    print(f"   Environment: {os.getenv('ENVIRONMENT', 'Not set')}")
    print(f"   Port: {os.getenv('PORT', 'Not set')}")

def main():
    """Main function"""
    print("🔧 KOMIHUB Bot Webhook URL Setter")
    print("=" * 40)
    
    print_deployment_info()
    print()
    
    webhook_url = set_webhook_url_env()
    
    if webhook_url:
        print(f"\n✅ Success! Webhook URL is now: {webhook_url}")
        print("The bot will automatically use this URL for webhooks.")
        
        # Print final environment check
        print(f"\n📋 Environment Variables:")
        print(f"   WEBHOOK_URL: {os.getenv('WEBHOOK_URL')}")
        print(f"   BOT_TOKEN: {'Set' if os.getenv('BOT_TOKEN') else 'Not set'}")
        print(f"   HOSTING_MODE: {os.getenv('HOSTING_MODE', 'auto')}")
        
    return webhook_url is not None

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)