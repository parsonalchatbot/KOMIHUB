# Render Deployment Guide for KOMIHUB Bot

## 🎯 Problem Solved
This guide fixes the webhook issues that prevented your bot from responding on Render.

## 🔧 What Was Fixed

### 1. **Webhook Processing Fixed**
- Updated `web_server.py` to properly process webhook updates through the bot's dispatcher
- Fixed the webhook endpoint to feed updates to `aiogram` properly

### 2. **Automatic Webhook Setup**
- Bot now automatically sets webhook URL on startup
- Automatic detection of Render environment
- Proper webhook URL generation based on Render's hostname

### 3. **Environment Configuration**
- Fixed Render deployment configuration
- Updated start command for proper web server startup

## 🚀 Quick Setup Steps

### Step 1: Update Environment Variables in Render

1. Go to your Render dashboard
2. Select your bot service
3. Go to **Environment** tab
4. Add/Update these environment variables:

```env
# Required Variables
BOT_TOKEN=7725786056:AAE4ZoqdXmsOVLu2SjiMLQOTq7QWt1-8O8Q
WEBHOOK_URL=https://your-service-name.onrender.com/webhook
HOSTING_MODE=webhook

# Optional but recommended
PORT=8000
HOST=0.0.0.0
LOG_LEVEL=INFO
ADMIN_NAME=YourName
ADMIN_ID=YourTelegramID
```

**Important**: Replace `your-service-name.onrender.com` with your actual Render service URL!

### Step 2: Deploy to Render

1. Commit and push your changes to GitHub
2. Render will automatically deploy from your repository
3. Wait for deployment to complete

### Step 3: Verify Webhook Setup

1. Check the deployment logs in Render dashboard
2. Look for "Bot initialized successfully" and "Webhook setup completed" messages
3. Visit your service URL: `https://your-service-name.onrender.com`

### Step 4: Test Your Bot

1. Send `/start` to your bot on Telegram
2. The bot should respond immediately
3. Try other commands to ensure everything works

## 🔍 Troubleshooting

### Bot Not Responding?

**Check these logs in Render dashboard:**

1. **Bot Initialization**: Look for "Bot initialized successfully"
2. **Webhook Setup**: Look for "Webhook set to: https://..." or "Webhook already configured correctly"
3. **Health Check**: Visit `https://your-service-name.onrender.com/health`

### Common Issues:

#### 1. Wrong Webhook URL
- **Problem**: Using placeholder URL `https://your-domain.com/webhook`
- **Solution**: Use actual Render service URL: `https://your-service-name.onrender.com/webhook`

#### 2. Bot Not Processing Updates
- **Problem**: Webhook received but bot doesn't respond
- **Solution**: Check that `/webhook` endpoint processes updates through bot dispatcher

#### 3. Service Not Accessible
- **Problem**: Health check fails
- **Solution**: Check start command and port configuration

### Manual Webhook Setup

If automatic setup fails, you can manually set the webhook:

1. Visit: `https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url=https://your-service-name.onrender.com/webhook`
2. Replace `{BOT_TOKEN}` with your actual bot token
3. You should see: `{"ok":true,"result":true,"url":"https://..."}`

## 🛠️ Useful Scripts

### Check Webhook Status
```bash
curl https://api.telegram.org/bot{BOT_TOKEN}/getWebhookInfo
```

### Delete Webhook (if needed)
```bash
curl https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook
```

### Test Health Endpoint
```bash
curl https://your-service-name.onrender.com/health
```

## 📊 Monitoring

### Health Check Endpoint
- URL: `https://your-service-name.onrender.com/health`
- Should return: `{"status": "healthy", "bot_status": "initialized"}`

### Info Endpoint
- URL: `https://your-service-name.onrender.com/info`
- Shows bot information and status

### Logs Location
- Check Render dashboard → Your Service → Logs
- Look for startup messages and error logs

## 🎯 Expected Behavior

After successful deployment:

1. **Service starts**: "Starting Telegram Bot Web Server..."
2. **Bot initializes**: "Bot initialized successfully"
3. **Webhook sets**: "Webhook set to: https://..." or "Webhook already configured correctly"
4. **Health check**: Service responds on `/health` endpoint
5. **Bot responds**: Commands work when sent via Telegram

## 🔧 Configuration Files Updated

- ✅ `web_server.py` - Fixed webhook processing
- ✅ `core/bot.py` - Added webhook setup
- ✅ `render.yaml` - Updated start command
- ✅ Environment validation scripts added

Your bot should now respond properly on Render! 🎉