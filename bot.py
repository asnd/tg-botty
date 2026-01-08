"""Main Telegram bot handlers and conversation flow."""

import logging
from datetime import datetime
from uuid import uuid4
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters
)
from models import User, Question, Response, ConversationState, get_session
from questions import QUESTION_BANK, init_questions
from analytics import get_user_streak, get_weekly_summary, get_mood_trend
from config import settings

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


# Helper functions
def get_or_create_user(telegram_id: int, username: str = None) -> User:
    """Get existing user or create new one."""
    session = get_session()
    user = session.query(User).filter_by(telegram_id=telegram_id).first()

    if not user:
        user = User(telegram_id=telegram_id, username=username)
        session.add(user)
        session.commit()
        logger.info(f"Created new user: {telegram_id}")

    session.close()
    return user


def get_conversation_state(telegram_id: int) -> ConversationState:
    """Get or create conversation state."""
    session = get_session()
    state = session.query(ConversationState).filter_by(telegram_id=telegram_id).first()

    if not state:
        state = ConversationState(telegram_id=telegram_id)
        session.add(state)
        session.commit()

    session.close()
    return state


def update_conversation_state(telegram_id: int, question_id: int = None,
                              session_id: str = None, state: str = None):
    """Update conversation state."""
    session = get_session()
    conv_state = session.query(ConversationState).filter_by(telegram_id=telegram_id).first()

    if not conv_state:
        conv_state = ConversationState(telegram_id=telegram_id)
        session.add(conv_state)

    if question_id is not None:
        conv_state.current_question_id = question_id
    if session_id is not None:
        conv_state.session_id = session_id
    if state is not None:
        conv_state.state = state

    conv_state.updated_at = datetime.utcnow()
    session.commit()
    session.close()


def get_next_question(current_question_id: int = None) -> Question:
    """Get next question in sequence."""
    session = get_session()

    if current_question_id is None:
        question = session.query(Question).filter_by(is_active=True).order_by(Question.order).first()
    else:
        current_q = session.query(Question).filter_by(id=current_question_id).first()
        question = (session.query(Question)
                   .filter(Question.is_active == True, Question.order > current_q.order)
                   .order_by(Question.order)
                   .first())

    session.close()
    return question


def get_question_options(question: Question) -> InlineKeyboardMarkup:
    """Generate inline keyboard buttons for question."""
    q_data = next((q for q in QUESTION_BANK if q["question_text"] == question.question_text), None)

    if not q_data or "options" not in q_data:
        # Default yes/no buttons
        keyboard = [
            [InlineKeyboardButton("Yes ✅", callback_data=f"answer_yes_{question.id}"),
             InlineKeyboardButton("No ❌", callback_data=f"answer_no_{question.id}")]
        ]
    else:
        # Custom options
        keyboard = []
        row = []
        for option in q_data["options"]:
            row.append(InlineKeyboardButton(option, callback_data=f"answer_{option}_{question.id}"))
            if len(row) == 2:
                keyboard.append(row)
                row = []
        if row:
            keyboard.append(row)

    # Add skip button
    keyboard.append([InlineKeyboardButton("Skip ⏭️", callback_data=f"skip_{question.id}")])

    return InlineKeyboardMarkup(keyboard)


# Command handlers
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    telegram_id = update.effective_user.id
    username = update.effective_user.username

    user = get_or_create_user(telegram_id, username)

    welcome_message = (
        "🌟 *Welcome to Your Journaling Bot!* 🌟\n\n"
        "I'll help you build a daily journaling habit with quick check-ins.\n\n"
        "📝 *What I do:*\n"
        "• Send you journaling prompts at your preferred times\n"
        "• Ask about your mood, gratitude, productivity, and self-care\n"
        "• Track your responses and show you insights\n"
        "• Help you build consistency with streak tracking\n\n"
        "⚙️ *Commands:*\n"
        "/journal - Start a journaling session now\n"
        "/schedule - Set your preferred times\n"
        "/stats - View your insights and trends\n"
        "/settings - Manage your preferences\n"
        "/help - Show help information\n\n"
        "Ready to start? Use /journal to begin your first check-in!"
    )

    await update.message.reply_text(welcome_message, parse_mode="Markdown")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command."""
    help_text = (
        "📖 *Help & Commands*\n\n"
        "*Main Commands:*\n"
        "/journal - Start a journaling session\n"
        "/schedule - Configure when you receive prompts\n"
        "/stats - View your statistics and insights\n"
        "/settings - Manage your preferences\n\n"
        "*How it works:*\n"
        "1. I'll ask you questions one at a time\n"
        "2. Answer with the button options\n"
        "3. Skip questions you don't want to answer\n"
        "4. Complete the session to log your responses\n\n"
        "*Question Categories:*\n"
        "😊 Mood - How you're feeling\n"
        "🙏 Gratitude - What you're thankful for\n"
        "🎯 Productivity - Your accomplishments\n"
        "💚 Self-care - Health and wellness\n\n"
        "Need more help? Contact the bot administrator."
    )

    await update.message.reply_text(help_text, parse_mode="Markdown")


async def journal_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /journal command - start journaling session."""
    telegram_id = update.effective_user.id
    username = update.effective_user.username

    user = get_or_create_user(telegram_id, username)

    if not user.is_active:
        await update.message.reply_text("Your account is inactive. Please contact support.")
        return

    # Generate new session ID
    session_id = str(uuid4())

    # Get first question
    first_question = get_next_question()

    if not first_question:
        await update.message.reply_text("No questions available. Please contact support.")
        return

    # Update conversation state
    update_conversation_state(telegram_id, first_question.id, session_id, "journaling")

    # Send first question
    keyboard = get_question_options(first_question)
    category_emoji = {
        "mood": "😊",
        "gratitude": "🙏",
        "productivity": "🎯",
        "self_care": "💚"
    }
    emoji = category_emoji.get(first_question.category, "📝")

    await update.message.reply_text(
        f"{emoji} *{first_question.category.replace('_', ' ').title()}*\n\n{first_question.question_text}",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /stats command - show user statistics."""
    telegram_id = update.effective_user.id
    user = get_or_create_user(telegram_id, update.effective_user.username)

    session = get_session()
    user_obj = session.query(User).filter_by(telegram_id=telegram_id).first()

    if not user_obj:
        await update.message.reply_text("No data available yet. Complete your first journal session!")
        session.close()
        return

    # Get analytics
    streak = get_user_streak(user_obj.id)
    weekly_summary = get_weekly_summary(user_obj.id)
    mood_trend = get_mood_trend(user_obj.id)

    stats_message = (
        "📊 *Your Journaling Stats*\n\n"
        f"🔥 Current Streak: *{streak} days*\n\n"
        f"📅 *This Week:*\n"
        f"Total responses: {weekly_summary['total_responses']}\n"
        f"Sessions completed: {weekly_summary['sessions_completed']}\n\n"
    )

    if mood_trend:
        stats_message += f"😊 *Mood Trend:* {mood_trend}\n\n"

    stats_message += "Keep up the great work! 🌟"

    session.close()
    await update.message.reply_text(stats_message, parse_mode="Markdown")


async def schedule_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /schedule command - manage notification times."""
    keyboard = [
        [InlineKeyboardButton("⏰ Morning (9:00 AM)", callback_data="schedule_09:00")],
        [InlineKeyboardButton("🌅 Afternoon (2:00 PM)", callback_data="schedule_14:00")],
        [InlineKeyboardButton("🌙 Evening (8:00 PM)", callback_data="schedule_20:00")],
        [InlineKeyboardButton("⚙️ Custom times", callback_data="schedule_custom")],
        [InlineKeyboardButton("📋 View current schedule", callback_data="schedule_view")],
    ]

    await update.message.reply_text(
        "⏰ *Schedule Your Journaling Times*\n\nWhen would you like to receive journaling prompts?",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )


async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /settings command."""
    keyboard = [
        [InlineKeyboardButton("⏰ Notification Schedule", callback_data="settings_schedule")],
        [InlineKeyboardButton("🌍 Timezone", callback_data="settings_timezone")],
        [InlineKeyboardButton("🔔 Enable/Disable Notifications", callback_data="settings_toggle")],
        [InlineKeyboardButton("🗑️ Clear My Data", callback_data="settings_clear")],
    ]

    await update.message.reply_text(
        "⚙️ *Settings*\n\nWhat would you like to configure?",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )


# Callback query handler
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button clicks."""
    query = update.callback_query
    await query.answer()

    telegram_id = update.effective_user.id
    callback_data = query.data

    # Handle answer callbacks
    if callback_data.startswith("answer_") or callback_data.startswith("skip_"):
        await handle_answer_callback(query, telegram_id, callback_data)

    # Handle schedule callbacks
    elif callback_data.startswith("schedule_"):
        await handle_schedule_callback(query, telegram_id, callback_data)

    # Handle settings callbacks
    elif callback_data.startswith("settings_"):
        await handle_settings_callback(query, telegram_id, callback_data)


async def handle_answer_callback(query, telegram_id: int, callback_data: str):
    """Handle answer button clicks."""
    session = get_session()

    # Parse callback data
    if callback_data.startswith("skip_"):
        question_id = int(callback_data.split("_")[1])
        answer = "skipped"
    else:
        parts = callback_data.split("_")
        question_id = int(parts[-1])
        answer = "_".join(parts[1:-1])

    # Get conversation state
    conv_state = session.query(ConversationState).filter_by(telegram_id=telegram_id).first()

    if not conv_state or conv_state.state != "journaling":
        await query.edit_message_text("Session expired. Use /journal to start a new session.")
        session.close()
        return

    # Save response if not skipped
    if answer != "skipped":
        user = session.query(User).filter_by(telegram_id=telegram_id).first()
        response = Response(
            user_id=user.id,
            question_id=question_id,
            answer=answer,
            session_id=conv_state.session_id
        )
        session.add(response)
        session.commit()

    # Get next question
    next_question = get_next_question(question_id)

    if next_question:
        # Update state
        conv_state.current_question_id = next_question.id
        session.commit()

        # Send next question
        keyboard = get_question_options(next_question)
        category_emoji = {
            "mood": "😊",
            "gratitude": "🙏",
            "productivity": "🎯",
            "self_care": "💚"
        }
        emoji = category_emoji.get(next_question.category, "📝")

        await query.edit_message_text(
            f"{emoji} *{next_question.category.replace('_', ' ').title()}*\n\n{next_question.question_text}",
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
    else:
        # Session complete
        conv_state.state = None
        conv_state.current_question_id = None
        session.commit()

        completion_message = (
            "✨ *Session Complete!* ✨\n\n"
            "Thank you for taking time to journal today.\n"
            "Your responses have been saved.\n\n"
            "Use /stats to see your progress!\n"
            "Use /journal to start another session anytime."
        )

        await query.edit_message_text(completion_message, parse_mode="Markdown")

    session.close()


async def handle_schedule_callback(query, telegram_id: int, callback_data: str):
    """Handle schedule button clicks."""
    from scheduler import add_user_schedule

    if callback_data == "schedule_view":
        session = get_session()
        user = session.query(User).filter_by(telegram_id=telegram_id).first()
        schedules = user.schedules if user else []

        if not schedules:
            message = "You don't have any scheduled times yet."
        else:
            times = [s.time for s in schedules if s.is_enabled]
            message = f"⏰ Your scheduled times:\n" + "\n".join([f"• {t}" for t in times])

        session.close()
        await query.edit_message_text(message)

    elif callback_data == "schedule_custom":
        await query.edit_message_text(
            "⚙️ *Custom Schedule*\n\n"
            "Send me your preferred times in 24-hour format (HH:MM), separated by commas.\n\n"
            "Example: `09:00, 14:30, 20:00`",
            parse_mode="Markdown"
        )

    else:
        time = callback_data.split("_")[1]
        add_user_schedule(telegram_id, [time])
        await query.edit_message_text(f"✅ Schedule set for {time}. You'll receive prompts at this time daily!")


async def handle_settings_callback(query, telegram_id: int, callback_data: str):
    """Handle settings button clicks."""
    session = get_session()
    user = session.query(User).filter_by(telegram_id=telegram_id).first()

    if callback_data == "settings_toggle":
        if user:
            user.is_active = not user.is_active
            session.commit()
            status = "enabled" if user.is_active else "disabled"
            await query.edit_message_text(f"✅ Notifications {status}!")
        session.close()

    elif callback_data == "settings_schedule":
        session.close()
        await query.edit_message_text("Use /schedule to manage your notification times.")

    elif callback_data == "settings_timezone":
        await query.edit_message_text(
            "🌍 *Timezone Settings*\n\n"
            "Send me your timezone (e.g., America/New_York, Europe/London, Asia/Tokyo)",
            parse_mode="Markdown"
        )
        session.close()

    elif callback_data == "settings_clear":
        keyboard = [
            [InlineKeyboardButton("Yes, delete everything", callback_data="confirm_clear_yes")],
            [InlineKeyboardButton("No, cancel", callback_data="confirm_clear_no")],
        ]
        await query.edit_message_text(
            "⚠️ *Warning*\n\nThis will delete all your data including responses and stats. Are you sure?",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
        session.close()

    elif callback_data == "confirm_clear_yes":
        if user:
            session.delete(user)
            session.commit()
        session.close()
        await query.edit_message_text("✅ Your data has been cleared. Use /start to begin again.")

    elif callback_data == "confirm_clear_no":
        session.close()
        await query.edit_message_text("Cancelled. Your data is safe!")


def main():
    """Start the bot."""
    from models import init_db
    from scheduler import JournalScheduler

    # Initialize database
    init_db()

    # Initialize questions
    session = get_session()
    init_questions(session)
    session.close()

    # Create application
    application = Application.builder().token(settings.telegram_bot_token).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("journal", journal_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("schedule", schedule_command))
    application.add_handler(CommandHandler("settings", settings_command))
    application.add_handler(CallbackQueryHandler(button_callback))

    # Initialize and start scheduler
    scheduler = JournalScheduler(application.bot)
    scheduler.start()

    # Start bot
    logger.info("Bot started!")
    try:
        application.run_polling(allowed_updates=Update.ALL_TYPES)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        scheduler.stop()


if __name__ == "__main__":
    main()
