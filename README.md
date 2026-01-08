# Telegram Journaling Bot

A friendly Telegram bot that helps you build a daily journaling habit through periodic prompts and interactive questions. Track your mood, gratitude, productivity, and self-care with simple yes/no responses.

## Features

- **Interactive Journaling**: Answer questions with simple button clicks
- **Customizable Schedules**: Set your own reminder times
- **Multiple Categories**:
  - 😊 Mood tracking
  - 🙏 Gratitude reminders
  - 🎯 Productivity check-ins
  - 💚 Self-care monitoring
- **Analytics & Insights**: Track streaks, view trends, and get weekly summaries
- **Privacy-Focused**: Your data stays in your database
- **Easy Deployment**: Run with Podman/Docker in minutes

## Quick Start

### Prerequisites

- Python 3.11+
- Telegram Bot Token (from [@BotFather](https://t.me/BotFather))
- Podman or Docker (optional, for containerized deployment)

### Option 1: Run with Podman (Recommended)

1. Clone the repository:
```bash
git clone <your-repo-url>
cd tg-botty
```

2. Create `.env` file:
```bash
cp .env.example .env
```

3. Edit `.env` and add your bot token:
```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
```

4. Build and run with Podman:
```bash
podman-compose up -d
```

Or with Docker Compose:
```bash
docker-compose up -d
```

5. Check logs:
```bash
podman-compose logs -f
```

### Option 2: Run Directly with Python

1. Create virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create `.env` file with your bot token:
```bash
cp .env.example .env
# Edit .env and add your TELEGRAM_BOT_TOKEN
```

4. Run the bot:
```bash
python bot.py
```

## Configuration

### Environment Variables

Edit `.env` file to configure:

```env
# Required
TELEGRAM_BOT_TOKEN=your_bot_token_here

# Optional
DATABASE_URL=sqlite:///./journaling_bot.db
DEFAULT_TIMEZONE=UTC
DEFAULT_SCHEDULE_TIMES=09:00,20:00
```

### Timezone Setup

Users can set their own timezone using the bot. Supported timezones follow the IANA Time Zone Database format (e.g., `America/New_York`, `Europe/London`, `Asia/Tokyo`).

## Bot Commands

- `/start` - Welcome message and setup
- `/journal` - Start a journaling session immediately
- `/schedule` - Configure when you receive prompts
- `/stats` - View your insights, streaks, and trends
- `/settings` - Manage preferences and data
- `/help` - Get help information

## How It Works

1. **Start the Bot**: Send `/start` to begin
2. **Set Your Schedule**: Use `/schedule` to choose when you want reminders
3. **Answer Questions**: When prompted, click buttons to answer
4. **Track Progress**: Use `/stats` to see your journaling journey
5. **Build Habits**: Maintain your streak and gain insights

## Question Categories

### Mood (3 questions)
- How are you feeling?
- Energy levels
- Stress/anxiety check

### Gratitude (3 questions)
- What made you smile?
- Who are you grateful for?
- Moments of peace or beauty

### Productivity (4 questions)
- Daily accomplishments
- Goal progress
- Focus assessment
- Tomorrow's planning

### Self-Care (6 questions)
- Sleep quality
- Exercise/movement
- Nutrition
- Personal time
- Social connections
- Hydration

## Database Schema

The bot uses SQLite by default. The schema includes:

- **users**: User profiles and settings
- **schedules**: Notification times per user
- **questions**: Question bank
- **responses**: User answers
- **conversation_states**: Current session tracking

## Analytics Features

- **Streak Tracking**: Count consecutive days of journaling
- **Weekly Summary**: Total responses and sessions
- **Mood Trends**: Analyze mood patterns over time
- **Category Insights**: Deep dive into specific areas
- **Monthly Reports**: Comprehensive overview

## Customization

### Adding Questions

Edit `questions.py` to add custom questions:

```python
{
    "category": "custom_category",
    "question_text": "Your question here?",
    "response_type": "yes_no",
    "options": ["Option 1", "Option 2"],
    "order": 17
}
```

### Modifying Schedule Times

Users can set custom times through the bot, or you can modify defaults in `.env`:

```env
DEFAULT_SCHEDULE_TIMES=07:00,12:00,19:00
```

## Development

### Project Structure

```
tg-botty/
├── bot.py              # Main bot logic and handlers
├── models.py           # Database models
├── questions.py        # Question bank
├── scheduler.py        # Periodic prompt scheduling
├── analytics.py        # Insights and statistics
├── config.py           # Configuration management
├── requirements.txt    # Python dependencies
├── Containerfile       # Container image definition
├── docker-compose.yml  # Container orchestration
└── README.md          # This file
```

### Running Tests

```bash
# TODO: Add test suite
pytest tests/
```

### Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Troubleshooting

### Bot not responding
- Check that the bot token is correct in `.env`
- Verify the bot is running: `podman-compose ps`
- Check logs: `podman-compose logs -f`

### Scheduled prompts not sending
- Verify timezone settings
- Check user schedule: send `/schedule` in Telegram
- Ensure the bot container has correct time

### Database issues
- Check database file permissions
- Verify volume mount in `docker-compose.yml`
- Check database path in `.env`

## Privacy & Data

- All data is stored locally in your SQLite database
- No data is sent to third parties
- Users can delete their data anytime with `/settings`
- Responses are only stored if tracking is enabled

## License

MIT License - feel free to use and modify as needed.

## Support

For issues, questions, or feature requests, please open an issue on GitHub.

## Roadmap

- [ ] Export data to CSV/JSON
- [ ] Custom question categories per user
- [ ] Group journaling support
- [ ] Voice note responses
- [ ] Integration with journaling apps
- [ ] Web dashboard for analytics
- [ ] Multi-language support
