#!/bin/bash

set -e

echo "🤖 Telegram Journaling Bot Setup"
echo "================================"
echo ""

# Check if .env exists
if [ -f .env ]; then
    echo "✓ .env file already exists"
else
    echo "Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your TELEGRAM_BOT_TOKEN"
    echo ""
    read -p "Press Enter to open .env in your editor (Ctrl+C to skip): "
    ${EDITOR:-nano} .env
fi

echo ""
echo "Choose deployment method:"
echo "1) Podman (recommended)"
echo "2) Docker"
echo "3) Python virtual environment"
read -p "Enter your choice (1-3): " choice

case $choice in
    1)
        echo ""
        echo "Building with Podman..."
        podman-compose up -d
        echo ""
        echo "✓ Bot is running!"
        echo "View logs: podman-compose logs -f"
        echo "Stop bot: podman-compose down"
        ;;
    2)
        echo ""
        echo "Building with Docker..."
        docker-compose up -d
        echo ""
        echo "✓ Bot is running!"
        echo "View logs: docker-compose logs -f"
        echo "Stop bot: docker-compose down"
        ;;
    3)
        echo ""
        echo "Setting up Python virtual environment..."
        python3 -m venv venv
        source venv/bin/activate
        pip install -r requirements.txt
        echo ""
        echo "✓ Environment ready!"
        echo "Run bot: source venv/bin/activate && python bot.py"
        echo ""
        read -p "Start bot now? (y/n): " start_now
        if [ "$start_now" = "y" ]; then
            python bot.py
        fi
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Open Telegram and search for your bot"
echo "2. Send /start to begin"
echo "3. Use /schedule to set your reminder times"
echo "4. Start journaling with /journal"
