"""Question bank for journaling prompts."""

QUESTION_BANK = [
    # Mood Tracking
    {
        "category": "mood",
        "question_text": "How are you feeling right now?",
        "response_type": "yes_no",
        "options": ["Great 😊", "Good 🙂", "Okay 😐", "Not great 😔"],
        "order": 1
    },
    {
        "category": "mood",
        "question_text": "Do you feel energized today?",
        "response_type": "yes_no",
        "options": ["Yes ⚡", "No 😴"],
        "order": 2
    },
    {
        "category": "mood",
        "question_text": "Are you feeling stressed or anxious?",
        "response_type": "yes_no",
        "options": ["Yes 😰", "No 😌"],
        "order": 3
    },

    # Gratitude
    {
        "category": "gratitude",
        "question_text": "Did something make you smile today?",
        "response_type": "yes_no",
        "options": ["Yes 😊", "No 😐"],
        "order": 4
    },
    {
        "category": "gratitude",
        "question_text": "Are you grateful for someone in your life right now?",
        "response_type": "yes_no",
        "options": ["Yes ❤️", "No"],
        "order": 5
    },
    {
        "category": "gratitude",
        "question_text": "Did you experience a moment of beauty or peace today?",
        "response_type": "yes_no",
        "options": ["Yes 🌟", "No"],
        "order": 6
    },

    # Productivity
    {
        "category": "productivity",
        "question_text": "Did you accomplish something you're proud of today?",
        "response_type": "yes_no",
        "options": ["Yes 🎉", "No"],
        "order": 7
    },
    {
        "category": "productivity",
        "question_text": "Are you making progress on your important goals?",
        "response_type": "yes_no",
        "options": ["Yes 🎯", "No"],
        "order": 8
    },
    {
        "category": "productivity",
        "question_text": "Did you focus well today?",
        "response_type": "yes_no",
        "options": ["Yes 🧠", "No 😵"],
        "order": 9
    },
    {
        "category": "productivity",
        "question_text": "Do you have a clear plan for tomorrow?",
        "response_type": "yes_no",
        "options": ["Yes 📝", "No"],
        "order": 10
    },

    # Self-Care
    {
        "category": "self_care",
        "question_text": "Did you get enough sleep last night?",
        "response_type": "yes_no",
        "options": ["Yes 😴", "No 🥱"],
        "order": 11
    },
    {
        "category": "self_care",
        "question_text": "Did you exercise or move your body today?",
        "response_type": "yes_no",
        "options": ["Yes 💪", "No"],
        "order": 12
    },
    {
        "category": "self_care",
        "question_text": "Did you eat healthy meals today?",
        "response_type": "yes_no",
        "options": ["Yes 🥗", "No"],
        "order": 13
    },
    {
        "category": "self_care",
        "question_text": "Did you take time for yourself today?",
        "response_type": "yes_no",
        "options": ["Yes 🧘", "No"],
        "order": 14
    },
    {
        "category": "self_care",
        "question_text": "Did you connect with friends or family today?",
        "response_type": "yes_no",
        "options": ["Yes 👥", "No"],
        "order": 15
    },
    {
        "category": "self_care",
        "question_text": "Did you stay hydrated today?",
        "response_type": "yes_no",
        "options": ["Yes 💧", "No"],
        "order": 16
    },
]


def get_questions_by_category(category: str) -> list[dict]:
    """Get all questions for a specific category."""
    return [q for q in QUESTION_BANK if q["category"] == category]


def get_all_categories() -> list[str]:
    """Get all unique categories."""
    return list(set(q["category"] for q in QUESTION_BANK))


def init_questions(session):
    """Initialize questions in database if not already present."""
    from models import Question

    existing_count = session.query(Question).count()
    if existing_count > 0:
        return

    for q_data in QUESTION_BANK:
        question = Question(
            category=q_data["category"],
            question_text=q_data["question_text"],
            response_type=q_data["response_type"],
            order=q_data["order"],
            is_active=True
        )
        session.add(question)

    session.commit()
