"""Scheduler for periodic journaling prompts."""

import logging
from datetime import datetime, time
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz
from telegram import Bot
from telegram.error import TelegramError
from models import User, Schedule, get_session
from config import settings

logger = logging.getLogger(__name__)


class JournalScheduler:
    """Manages scheduled journaling prompts."""

    def __init__(self, bot: Bot):
        self.bot = bot
        self.scheduler = AsyncIOScheduler()

    def start(self):
        """Start the scheduler."""
        # Load all user schedules
        self.load_all_schedules()
        self.scheduler.start()
        logger.info("Scheduler started")

    def stop(self):
        """Stop the scheduler."""
        self.scheduler.shutdown()
        logger.info("Scheduler stopped")

    def load_all_schedules(self):
        """Load schedules for all active users."""
        session = get_session()
        users = session.query(User).filter_by(is_active=True).all()

        for user in users:
            for schedule in user.schedules:
                if schedule.is_enabled:
                    self.add_job(user.telegram_id, schedule.time, user.timezone)

        session.close()
        logger.info(f"Loaded schedules for {len(users)} users")

    def add_job(self, telegram_id: int, time_str: str, timezone_str: str = "UTC"):
        """Add a scheduled job for a user."""
        try:
            hour, minute = map(int, time_str.split(":"))
            tz = pytz.timezone(timezone_str)

            job_id = f"journal_{telegram_id}_{time_str}"

            # Remove existing job if present
            if self.scheduler.get_job(job_id):
                self.scheduler.remove_job(job_id)

            # Add new job
            self.scheduler.add_job(
                self.send_journal_prompt,
                trigger=CronTrigger(hour=hour, minute=minute, timezone=tz),
                args=[telegram_id],
                id=job_id,
                replace_existing=True
            )

            logger.info(f"Added schedule for user {telegram_id} at {time_str} ({timezone_str})")

        except Exception as e:
            logger.error(f"Error adding job for user {telegram_id}: {e}")

    def remove_job(self, telegram_id: int, time_str: str):
        """Remove a scheduled job."""
        job_id = f"journal_{telegram_id}_{time_str}"
        if self.scheduler.get_job(job_id):
            self.scheduler.remove_job(job_id)
            logger.info(f"Removed schedule {job_id}")

    async def send_journal_prompt(self, telegram_id: int):
        """Send journaling prompt to user."""
        try:
            message = (
                "🌟 *Time for your journal check-in!* 🌟\n\n"
                "Take a moment to reflect on your day.\n\n"
                "Use /journal to start your session."
            )

            await self.bot.send_message(
                chat_id=telegram_id,
                text=message,
                parse_mode="Markdown"
            )

            logger.info(f"Sent journal prompt to user {telegram_id}")

        except TelegramError as e:
            logger.error(f"Error sending prompt to user {telegram_id}: {e}")


def add_user_schedule(telegram_id: int, times: list[str], timezone_str: str = None):
    """Add schedule times for a user."""
    session = get_session()

    user = session.query(User).filter_by(telegram_id=telegram_id).first()
    if not user:
        logger.error(f"User {telegram_id} not found")
        session.close()
        return

    # Update timezone if provided
    if timezone_str:
        user.timezone = timezone_str

    # Clear existing schedules
    for schedule in user.schedules:
        session.delete(schedule)

    # Add new schedules
    for time_str in times:
        schedule = Schedule(
            user_id=user.id,
            time=time_str,
            is_enabled=True
        )
        session.add(schedule)

    session.commit()
    session.close()

    logger.info(f"Updated schedule for user {telegram_id}: {times}")


def remove_user_schedule(telegram_id: int, time_str: str = None):
    """Remove schedule for a user."""
    session = get_session()

    user = session.query(User).filter_by(telegram_id=telegram_id).first()
    if not user:
        session.close()
        return

    if time_str:
        # Remove specific time
        schedule = session.query(Schedule).filter_by(user_id=user.id, time=time_str).first()
        if schedule:
            session.delete(schedule)
    else:
        # Remove all schedules
        for schedule in user.schedules:
            session.delete(schedule)

    session.commit()
    session.close()

    logger.info(f"Removed schedule for user {telegram_id}")


def get_user_schedules(telegram_id: int) -> list[dict]:
    """Get all schedules for a user."""
    session = get_session()

    user = session.query(User).filter_by(telegram_id=telegram_id).first()
    if not user:
        session.close()
        return []

    schedules = [
        {"time": s.time, "enabled": s.is_enabled}
        for s in user.schedules
    ]

    session.close()
    return schedules
