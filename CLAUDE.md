# CLAUDE.md - Telegram Journaling Bot

This document provides AI assistants with context about the project structure, architecture, and development guidelines.

## Project Overview

**Purpose**: A Telegram bot that helps users build daily journaling habits through periodic prompts and interactive yes/no questions.

**Tech Stack**:
- Python 3.11+
- python-telegram-bot v20+ (async)
- SQLAlchemy (ORM)
- APScheduler (job scheduling)
- SQLite (database)
- Pydantic (settings management)

## Architecture

### High-Level Flow

```
User → Telegram → Bot Handlers → Database ← Scheduler
                       ↓
                  Analytics
```

1. **User Interaction**: Users interact via Telegram commands and inline buttons
2. **Bot Handlers**: Process commands and callbacks, manage conversation state
3. **Database**: Store users, questions, responses, schedules, conversation states
4. **Scheduler**: Send periodic journaling prompts based on user preferences
5. **Analytics**: Calculate streaks, trends, and insights from user responses

### Core Components

#### bot.py (Main Application)
- **Command Handlers**: `/start`, `/journal`, `/stats`, `/schedule`, `/settings`, `/help`
- **Callback Handlers**: Process inline button clicks
- **Conversation Flow**: One-question-at-a-time interactive journaling
- **State Management**: Track current question and session

**Key Functions**:
- `get_or_create_user()`: User registration/retrieval
- `get_next_question()`: Sequential question fetching
- `get_question_options()`: Generate inline keyboard buttons
- `handle_answer_callback()`: Process user responses
- `button_callback()`: Route callback queries

#### models.py (Database Schema)
```
User (1) ──── (M) Schedule
  │
  └──── (M) Response ──── (1) Question

ConversationState (1:1 with telegram_id)
```

**Tables**:
- `users`: User profiles, timezone, active status
- `schedules`: Notification times per user
- `questions`: Question bank (pre-seeded)
- `responses`: User answers with session tracking
- `conversation_states`: Current session state

#### questions.py (Question Bank)
- 16 pre-defined questions across 4 categories
- Categories: mood, gratitude, productivity, self_care
- Each question has text, options, and display order
- `init_questions()`: Seeds database on first run

#### scheduler.py (Periodic Prompts)
- `JournalScheduler`: Manages APScheduler instance
- `add_job()`: Schedule reminders for specific times
- `send_journal_prompt()`: Send Telegram messages
- Timezone-aware scheduling with pytz

#### analytics.py (Insights & Trends)
- `get_user_streak()`: Calculate consecutive journaling days
- `get_weekly_summary()`: Count responses and sessions
- `get_mood_trend()`: Analyze mood patterns (improving/stable/declining)
- `get_category_insights()`: Deep dive into specific categories
- `get_monthly_report()`: Comprehensive 30-day overview

#### config.py (Settings)
- Pydantic-based configuration
- Environment variables from `.env`
- Settings: `TELEGRAM_BOT_TOKEN`, `DATABASE_URL`, `DEFAULT_TIMEZONE`

## Development Guidelines

### Code Style
- **Formatting**: Use `ruff format .` before committing
- **Linting**: Run `ruff check .` to catch issues
- **Type Hints**: Use for function signatures when possible
- **Docstrings**: Required for public functions

### Database Patterns
```python
# Always close sessions
session = get_session()
try:
    # database operations
finally:
    session.close()
```

### Adding New Questions
1. Edit `questions.py` → Add to `QUESTION_BANK`
2. Set unique `order` number
3. Choose `category` and define `options`
4. Database auto-seeds on next run

### Adding New Commands
1. Create async handler: `async def command_name(update, context)`
2. Register in `main()`: `application.add_handler(CommandHandler("name", command_name))`
3. Add to help text in `/help` command

### Adding New Callback Actions
1. Add button in command with `callback_data="action_param"`
2. Handle in `button_callback()` with condition checking `callback_data`
3. Use `query.answer()` and `query.edit_message_text()` for responses

## Common Tasks

### Testing Locally
```bash
# Set up environment
cp .env.example .env
# Edit .env with your bot token

# Install dependencies
pip install -r requirements.txt

# Run bot
python bot.py
```

### Running with Podman
```bash
# Build and run
podman-compose up -d

# View logs
podman-compose logs -f

# Stop
podman-compose down
```

### Database Inspection
```python
from models import get_session, User, Response, Question

session = get_session()

# Get all users
users = session.query(User).all()

# Get user responses
responses = session.query(Response).filter_by(user_id=1).all()

# Get active questions
questions = session.query(Question).filter_by(is_active=True).all()

session.close()
```

### Debugging Scheduler
- Check logs: `logger.info()` messages show job additions
- Verify timezone: `pytz.timezone(user.timezone)`
- List jobs: `scheduler.scheduler.get_jobs()`

## File Structure

```
tg-botty/
├── bot.py                  # Main bot logic (495 lines)
├── models.py               # SQLAlchemy models (120 lines)
├── questions.py            # Question bank (154 lines)
├── scheduler.py            # APScheduler integration (170 lines)
├── analytics.py            # Statistics & insights (236 lines)
├── config.py               # Pydantic settings (21 lines)
├── requirements.txt        # Python dependencies
├── .env.example            # Environment template
├── Containerfile           # Container image definition
├── docker-compose.yml      # Container orchestration
├── setup.sh                # Quick setup script
├── journaling-bot.service  # Systemd service template
├── .github/
│   └── workflows/
│       └── ci.yml          # GitHub Actions CI/CD
└── README.md               # User documentation
```

## Important Notes

### Session Management
- Each journaling session has unique `session_id` (UUID)
- Sessions tracked in `conversation_states` table
- Sessions expire if user doesn't complete within reasonable time
- State includes: current_question_id, session_id, state ("journaling", etc.)

### Inline Keyboards
- Generated dynamically based on question data
- Custom options from `questions.py`
- Default to Yes/No if no options specified
- Always include "Skip" button

### Timezone Handling
- Users can set their own timezone
- Default: UTC (from config)
- Scheduler uses `pytz.timezone()` for conversion
- Important: Always store UTC in database, convert for display

### Security Considerations
- Never hardcode bot token (use .env)
- CI checks for secrets in code
- `.env` file ignored by git
- User data deletable via `/settings`

## CI/CD Pipeline

### GitHub Actions Workflow
```yaml
Jobs:
1. lint-and-test: Ruff linting, formatting, mypy, bandit
2. build-container: Docker build test
3. validate-config: docker-compose validation, secrets check
```

### Pre-commit Checklist
```bash
ruff format .              # Format code
ruff check .               # Lint code
git status                 # Check changes
git add .                  # Stage changes
git commit -m "message"    # Commit
git push                   # Push to GitHub
```

## Known Issues & Limitations

1. **No Tests**: Test suite not yet implemented
2. **Single Language**: English only, no i18n support
3. **SQLite**: Not ideal for high-concurrency (consider PostgreSQL for scale)
4. **No Data Export**: Users can't export their responses yet
5. **Basic Analytics**: Mood trend analysis is simplistic

## Extension Ideas

### Easy Additions
- More question categories
- Custom reminder messages
- Multiple reminders per day
- Weekly email summaries

### Medium Complexity
- Voice note responses
- Photo attachments for gratitude
- Goal setting and tracking
- Sharing features (anonymous)

### Advanced Features
- NLP analysis of text responses
- Personalized question recommendations
- Integration with calendars
- Web dashboard
- Multi-language support

## Troubleshooting

### Bot Not Responding
1. Check token in `.env`
2. Verify bot running: `ps aux | grep bot.py`
3. Check logs for errors
4. Verify database exists and is writable

### Scheduler Not Working
1. Check user has active schedule: `SELECT * FROM schedules`
2. Verify timezone settings
3. Check APScheduler logs
4. Confirm system time is correct

### Database Errors
1. Delete database file to reset: `rm journaling_bot.db`
2. Check file permissions
3. Verify SQLAlchemy connection string
4. Run `init_db()` to recreate tables

## Contact & Support

- **Repository**: https://github.com/asnd/tg-botty
- **Issues**: https://github.com/asnd/tg-botty/issues
- **License**: MIT

## Version History

- **v1.0.0**: Initial release with core journaling features
- Interactive yes/no questions
- Scheduling system
- Basic analytics
- Container deployment support

---

*This file is designed for AI assistants. For user documentation, see README.md*
