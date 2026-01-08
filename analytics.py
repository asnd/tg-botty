"""Analytics and insights for user journaling data."""

from datetime import datetime, timedelta
from collections import Counter
from sqlalchemy import func, distinct
from models import Response, Question, get_session


def get_user_streak(user_id: int) -> int:
    """Calculate user's current journaling streak (consecutive days)."""
    session = get_session()

    # Get all unique dates with responses
    response_dates = (
        session.query(func.date(Response.responded_at))
        .filter(Response.user_id == user_id)
        .distinct()
        .order_by(func.date(Response.responded_at).desc())
        .all()
    )

    if not response_dates:
        session.close()
        return 0

    # Calculate streak
    streak = 0
    today = datetime.utcnow().date()
    current_date = today

    for (response_date,) in response_dates:
        if response_date == current_date or response_date == current_date - timedelta(days=1):
            streak += 1
            current_date = response_date - timedelta(days=1)
        else:
            break

    session.close()
    return streak


def get_weekly_summary(user_id: int) -> dict:
    """Get summary of user's activity for the past week."""
    session = get_session()

    week_ago = datetime.utcnow() - timedelta(days=7)

    # Total responses
    total_responses = (
        session.query(Response)
        .filter(Response.user_id == user_id, Response.responded_at >= week_ago)
        .count()
    )

    # Unique sessions (days with activity)
    sessions_completed = (
        session.query(distinct(Response.session_id))
        .filter(Response.user_id == user_id, Response.responded_at >= week_ago)
        .count()
    )

    session.close()

    return {
        "total_responses": total_responses,
        "sessions_completed": sessions_completed,
    }


def get_mood_trend(user_id: int, days: int = 7) -> str:
    """Analyze mood trend over the past N days."""
    session = get_session()

    cutoff_date = datetime.utcnow() - timedelta(days=days)

    # Get mood-related responses
    mood_responses = (
        session.query(Response.answer)
        .join(Question)
        .filter(
            Response.user_id == user_id,
            Response.responded_at >= cutoff_date,
            Question.category == "mood"
        )
        .all()
    )

    if not mood_responses:
        session.close()
        return "Not enough data"

    # Count positive vs negative indicators
    positive_keywords = ["yes", "great", "good", "energized", "⚡", "😊", "🙂"]
    negative_keywords = ["no", "not great", "stressed", "anxious", "😔", "😰", "😴"]

    positive_count = 0
    negative_count = 0

    for (answer,) in mood_responses:
        answer_lower = answer.lower()
        if any(keyword in answer_lower for keyword in positive_keywords):
            positive_count += 1
        elif any(keyword in answer_lower for keyword in negative_keywords):
            negative_count += 1

    session.close()

    # Determine trend
    if positive_count > negative_count * 1.5:
        return "Improving 📈"
    elif negative_count > positive_count * 1.5:
        return "Needs attention 📉"
    else:
        return "Stable 😐"


def get_category_insights(user_id: int, category: str, days: int = 30) -> dict:
    """Get insights for a specific category."""
    session = get_session()

    cutoff_date = datetime.utcnow() - timedelta(days=days)

    responses = (
        session.query(Response.answer, Response.responded_at)
        .join(Question)
        .filter(
            Response.user_id == user_id,
            Response.responded_at >= cutoff_date,
            Question.category == category
        )
        .all()
    )

    if not responses:
        session.close()
        return {"message": "No data available"}

    # Count answer frequencies
    answer_counts = Counter(answer for answer, _ in responses)

    # Calculate yes/no ratio
    yes_count = sum(count for answer, count in answer_counts.items() if "yes" in answer.lower())
    no_count = sum(count for answer, count in answer_counts.items() if "no" in answer.lower())

    total = yes_count + no_count
    yes_percentage = (yes_count / total * 100) if total > 0 else 0

    session.close()

    return {
        "category": category,
        "total_responses": len(responses),
        "yes_percentage": round(yes_percentage, 1),
        "most_common": answer_counts.most_common(3),
    }


def get_monthly_report(user_id: int) -> dict:
    """Generate comprehensive monthly report."""
    session = get_session()

    month_ago = datetime.utcnow() - timedelta(days=30)

    # Total responses
    total_responses = (
        session.query(Response)
        .filter(Response.user_id == user_id, Response.responded_at >= month_ago)
        .count()
    )

    # Sessions completed
    sessions = (
        session.query(distinct(Response.session_id))
        .filter(Response.user_id == user_id, Response.responded_at >= month_ago)
        .count()
    )

    # Active days
    active_days = (
        session.query(distinct(func.date(Response.responded_at)))
        .filter(Response.user_id == user_id, Response.responded_at >= month_ago)
        .count()
    )

    # Category breakdown
    categories = ["mood", "gratitude", "productivity", "self_care"]
    category_stats = {}

    for category in categories:
        cat_responses = (
            session.query(Response)
            .join(Question)
            .filter(
                Response.user_id == user_id,
                Response.responded_at >= month_ago,
                Question.category == category
            )
            .count()
        )
        category_stats[category] = cat_responses

    session.close()

    return {
        "total_responses": total_responses,
        "sessions_completed": sessions,
        "active_days": active_days,
        "consistency_rate": round((active_days / 30) * 100, 1),
        "category_breakdown": category_stats,
    }


def get_best_time_analysis(user_id: int) -> dict:
    """Analyze when user is most consistent with journaling."""
    session = get_session()

    responses = (
        session.query(Response.responded_at)
        .filter(Response.user_id == user_id)
        .all()
    )

    if not responses:
        session.close()
        return {"message": "Not enough data"}

    # Count by hour
    hour_counts = Counter(response_time.hour for (response_time,) in responses)

    # Find most common hours
    most_active_hours = hour_counts.most_common(3)

    session.close()

    return {
        "most_active_times": [
            f"{hour:02d}:00" for hour, _ in most_active_hours
        ],
        "total_sessions": len(responses),
    }
