# KOMIHUB Bot Deployment Guide

This guide covers deploying the KOMIHUB Telegram Bot on various hosting platforms including Render, VPS, and Termux.

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- Bot token from [@BotFather](https://t.me/BotFather)
- Basic understanding of the platform you're deploying to

### Environment Setup

1. **Copy environment template:**
   ```bash
   cp .env.example .env
   ```

2. **Configure your `.env` file:**
   ```env
   BOT_TOKEN=your_bot_token_here
   BOT_NAME=Your Bot Name
   ADMIN_NAME=Your Name
   ADMIN_ID=your_user_id
   ```

3. **Choose hosting mode:**
   - **Polling**: For VPS, Termux, local development
   - **Webhook**: For Render, Heroku, Railway, etc.

## 🌐 Web Service Hosting (Render, Heroku, Railway)

### Render Deployment

1. **Fork/clone this repository**

2. **Connect to Render:**
   - Go to [Render.com](https://render.com)
   - Click "New" → "Web Service"
   - Connect your repository

3. **Configuration:**
   - **Environment:** Python 3.12
   - **Build Command:** `pip install -r pyproject.toml`
   - **Start Command:** `uvicorn app:app --host 0.0.0.0 --port $PORT`
   - **Plan:** Free or Starter

4. **Environment Variables:**
   Add these in Render dashboard:
   ```
   BOT_TOKEN=your_bot_token
   WEBHOOK_URL=https://your-service.onrender.com/webhook
   HOSTING_MODE=webhook
   LOG_LEVEL=INFO
   ```

5. **Deploy and test:**
   - Visit your service URL
   - Check `/health` endpoint
   - Set webhook via `/set_webhook` endpoint

### Railway Deployment

1. **Connect repository to Railway**
2. **Set environment variables:**
   ```bash
   railway variables set BOT_TOKEN=your_bot_token
   railway variables set WEBHOOK_URL=https://your-app.railway.app/webhook
   railway variables set HOSTING_MODE=webhook
   ```
3. **Deploy automatically**

### Heroku Deployment

1. **Create Procfile:**
   ```
   web: uvicorn app:app --host 0.0.0.0 --port $PORT
   ```

2. **Deploy:**
   ```bash
   heroku create your-bot-name
   git push heroku main
   ```

3. **Set config vars:**
   ```bash
   heroku config:set BOT_TOKEN=your_bot_token
   heroku config:set WEBHOOK_URL=https://your-bot-name.herokuapp.com/webhook
   heroku config:set HOSTING_MODE=webhook
   ```

## 🖥️ VPS Deployment

### Ubuntu/Debian VPS

1. **Server setup:**
   ```bash
   # Update system
   sudo apt update && sudo apt upgrade -y
   
   # Install Python and dependencies
   sudo apt install python3.12 python3.12-venv python3-pip git -y
   
   # Clone repository
   git clone https://github.com/GrandpaEJ/KOMIHUB.git
   cd KOMIHUB
   
   # Create virtual environment
   python3.12 -m venv venv
   source venv/bin/activate
   
   # Install dependencies
   pip install -r pyproject.toml
   ```

2. **Configuration:**
   ```bash
   cp .env.example .env
   # Edit .env file with your settings
   nano .env
   ```

3. **Systemd service (optional):**
   ```bash
   sudo nano /etc/systemd/system/KOMIHUB.service
   ```

   **Service file content:**
   ```ini
   [Unit]
   Description=KOMIHUB Telegram Bot
   After=network.target
   
   [Service]
   Type=simple
   User=your_user
   WorkingDirectory=/path/to/KOMIHUB
   Environment=PATH=/path/to/KOMIHUB/venv/bin
   ExecStart=/path/to/KOMIHUB/venv/bin/python app.py
   Restart=always
   
   [Install]
   WantedBy=multi-user.target
   ```

4. **Start service:**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable KOMIHUB
   sudo systemctl start KOMIHUB
   ```

## 📱 Termux Deployment

### Android Termux

1. **Install Termux:**
   - Download from F-Droid or Google Play

2. **Setup:**
   ```bash
   # Update packages
   pkg update && pkg upgrade -y
   
   # Install Python
   pkg install python git
   
   # Clone repository
   git clone https://github.com/GrandpaEJ/KOMIHUB.git
   cd KOMIHUB
   
   # Install dependencies
   pip install -r pyproject.toml
   ```

3. **Configuration:**
   ```bash
   cp .env.example .env
   nano .env
   ```

4. **Run bot:**
   ```bash
   # Set hosting mode for polling
   export HOSTING_MODE=polling
   python app.py
   ```

5. **Background execution:**
   ```bash
   # Install tmux or screen for background sessions
   pkg install tmux
   tmux
   python app.py
   # Press Ctrl+B then D to detach
   ```

## 🐳 Docker Deployment (Optional)

1. **Create Dockerfile:**
   ```dockerfile
   FROM python:3.12-slim
   
   WORKDIR /app
   
   COPY pyproject.toml .
   RUN pip install -r pyproject.toml
   
   COPY . .
   
   EXPOSE 8000
   
   CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
   ```

2. **Build and run:**
   ```bash
   docker build -t KOMIHUB .
   docker run -p 8000:8000 -e BOT_TOKEN=your_token KOMIHUB
   ```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `BOT_TOKEN` | Telegram bot token | - | ✅ |
| `BOT_NAME` | Bot display name | KOMIHUB BOT | ❌ |
| `ADMIN_NAME` | Admin display name | Admin | ❌ |
| `ADMIN_ID` | Admin Telegram user ID | - | ❌ |
| `HOSTING_MODE` | hosting_mode | auto | ❌ |
| `WEBHOOK_URL` | Webhook URL for web hosting | - | ⚠️ |
| `LOG_LEVEL` | Log level (DEBUG, INFO, etc.) | INFO | ❌ |
| `DATABASE_URL` | Database connection string | sqlite:///./data/komihub.db | ❌ |

### Hosting Mode Selection

- **`polling`**: For VPS, Termux, local development
- **`webhook`**: For web services (Render, Heroku, Railway)
- **`auto`**: Auto-detect based on environment

## 📊 Health Checks

### Web Services
- **Health Endpoint:** `GET /health`
- **Info Endpoint:** `GET /info`
- **Webhook Test:** `POST /set_webhook`

### Polling Services
- Check logs in `logs/` directory
- Monitor bot status via `/info` command

## 🔍 Troubleshooting

### Common Issues

1. **Bot not responding:**
   - Check bot token is correct
   - Verify hosting mode matches environment
   - Check logs for errors

2. **Webhook not working:**
   - Ensure WEBHOOK_URL is set correctly
   - Check if service is accessible publicly
   - Verify PORT environment variable

3. **Database errors:**
   - Check DATABASE_URL configuration
   - Ensure data directory permissions

### Log Files

- **Main logs:** `logs/komihub.log`
- **Error logs:** `logs/error.log`
- **Web service logs:** Check platform's log viewer

## 🔐 Security

1. **Environment variables:** Never commit `.env` file
2. **Bot token:** Keep it secure and private
3. **Webhook URL:** Use HTTPS for production
4. **Admin access:** Verify admin ID for security

## 📈 Monitoring

### Web Services
- Use platform monitoring (Render Dashboard, Heroku Metrics)
- Health check endpoints for monitoring services

### VPS/Termux
- Setup process monitoring with systemd (VPS)
- Use termux services (Termux)
- Monitor log files regularly

## 🚀 Performance Tips

1. **Optimize for your platform:**
   - Use appropriate hosting mode
   - Configure proper log levels
   - Monitor resource usage

2. **Scaling:**
   - Web services can auto-scale
   - VPS can upgrade resources
   - Consider load balancing for high traffic

## 📞 Support

- Check logs for error messages
- Review this deployment guide
- Create GitHub issues for bugs
- Join our community discussions

---

**Happy Deploying! 🎉**