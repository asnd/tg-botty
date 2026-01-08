from datetime import datetime
from typing import Optional
from sqlalchemy import (
    String,
    Integer,
    Boolean,
    DateTime,
    ForeignKey,
    Text,
    create_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, Session
from config import settings


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    username: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    timezone: Mapped[str] = mapped_column(String(50), default=settings.default_timezone)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    schedules: Mapped[list["Schedule"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    responses: Mapped[list["Response"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<User(telegram_id={self.telegram_id}, username={self.username})>"


class Schedule(Base):
    __tablename__ = "schedules"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    time: Mapped[str] = mapped_column(String(5))  # Format: "HH:MM"
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="schedules")

    def __repr__(self):
        return f"<Schedule(user_id={self.user_id}, time={self.time})>"


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(primary_key=True)
    category: Mapped[str] = mapped_column(
        String(50)
    )  # mood, gratitude, productivity, self_care
    question_text: Mapped[str] = mapped_column(Text)
    response_type: Mapped[str] = mapped_column(
        String(20), default="yes_no"
    )  # yes_no, scale, text
    order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    responses: Mapped[list["Response"]] = relationship(back_populates="question")

    def __repr__(self):
        return (
            f"<Question(category={self.category}, question={self.question_text[:30]})>"
        )


class Response(Base):
    __tablename__ = "responses"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"))
    answer: Mapped[str] = mapped_column(Text)
    responded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    session_id: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True
    )  # Group responses from same session

    # Relationships
    user: Mapped["User"] = relationship(back_populates="responses")
    question: Mapped["Question"] = relationship(back_populates="responses")

    def __repr__(self):
        return f"<Response(user_id={self.user_id}, question_id={self.question_id}, answer={self.answer})>"


class ConversationState(Base):
    __tablename__ = "conversation_states"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    current_question_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    session_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    state: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True
    )  # journaling, settings, etc
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def __repr__(self):
        return (
            f"<ConversationState(telegram_id={self.telegram_id}, state={self.state})>"
        )


# Database initialization
engine = create_engine(settings.database_url, echo=False)


def init_db():
    """Initialize database tables."""
    Base.metadata.create_all(engine)


def get_session() -> Session:
    """Get database session."""
    return Session(engine)
