from sqlalchemy import Column, String, Boolean, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from database import Base
import uuid

class User(Base):
    __tablename__ = "users"
    id           = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    firebase_uid = Column(String, unique=True, nullable=False)
    email        = Column(String, unique=True, nullable=False)
    name         = Column(String, nullable=True)
    created_at   = Column(DateTime(timezone=True), server_default=func.now())

class Notification(Base):
    __tablename__ = "notifications"
    id         = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id    = Column(UUID(as_uuid=True), nullable=True)
    from_email = Column(String, nullable=False)
    subject    = Column(String, nullable=False)
    message    = Column(Text, nullable=False)
    category   = Column(String, nullable=False)
    message_id = Column(String, unique=True, nullable=False)
    is_read    = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Reminder(Base):
    __tablename__ = "reminders"
    id         = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id    = Column(UUID(as_uuid=True), nullable=False)
    title      = Column(String, nullable=False)
    note       = Column(Text, nullable=True)
    remind_at  = Column(DateTime(timezone=True), nullable=False)
    is_done    = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class EmailSummary(Base):
    __tablename__ = "email_summaries"
    id         = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id    = Column(UUID(as_uuid=True), nullable=False)
    from_email = Column(String, nullable=False)
    from_name  = Column(String, nullable=True)
    subject    = Column(String, nullable=False)
    body       = Column(Text, nullable=True)
    summary    = Column(Text, nullable=True)
    priority   = Column(String, default='normal')
    is_read    = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())