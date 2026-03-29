from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from database import get_db
from models import User, Notification, Reminder, EmailSummary
from dotenv import load_dotenv
import uuid
import os

load_dotenv()

app = FastAPI(
    title="ARIA Backend API",
    description="AI Personal Secretary Backend",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Schemas ───────────────────────────────────────────
class UserCreate(BaseModel):
    firebase_uid: str
    email: str
    name: Optional[str] = None

class NotifyPayload(BaseModel):
    from_email: str
    subject: str
    message: str
    category: str
    message_id: str
    user_id: Optional[str] = None

class ReminderCreate(BaseModel):
    user_id: str
    title: str
    note: Optional[str] = None
    remind_at: str

# ── Health Check ──────────────────────────────────────
@app.get("/")
async def root():
    return {"status": "ARIA Backend Running ✅", "version": "1.0.0"}

# ── User Routes ───────────────────────────────────────
@app.post("/users")
async def create_or_get_user(
    payload: UserCreate,
    db: Session = Depends(get_db)
):
    existing = db.query(User).filter(
        User.firebase_uid == payload.firebase_uid
    ).first()

    if existing:
        return {
            "id": str(existing.id),
            "firebase_uid": existing.firebase_uid,
            "email": existing.email,
            "name": existing.name,
            "created_at": str(existing.created_at),
            "existing": True
        }

    user = User(
        firebase_uid=payload.firebase_uid,
        email=payload.email,
        name=payload.name
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "id": str(user.id),
        "firebase_uid": user.firebase_uid,
        "email": user.email,
        "name": user.name,
        "created_at": str(user.created_at),
        "existing": False
    }

# ── Notification Routes ───────────────────────────────
@app.post("/notify")
async def notify(
    payload: NotifyPayload,
    db: Session = Depends(get_db)
):
    existing = db.query(Notification).filter(
        Notification.message_id == payload.message_id
    ).first()

    if existing:
        return {
            "success": True,
            "notification_id": str(existing.id),
            "duplicate": True
        }

    notification = Notification(
        from_email=payload.from_email,
        subject=payload.subject,
        message=payload.message,
        category=payload.category,
        message_id=payload.message_id
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)

    return {
        "success": True,
        "notification_id": str(notification.id)
    }

@app.get("/notifications")
async def get_notifications(db: Session = Depends(get_db)):
    notifications = db.query(Notification)\
        .order_by(Notification.created_at.desc())\
        .limit(50)\
        .all()

    return {
        "notifications": [
            {
                "id": str(n.id),
                "from_email": n.from_email,
                "subject": n.subject,
                "message": n.message,
                "category": n.category,
                "message_id": n.message_id,
                "is_read": n.is_read,
                "created_at": str(n.created_at)
            }
            for n in notifications
        ]
    }

@app.patch("/notifications/{notification_id}/read")
async def mark_read(
    notification_id: str,
    db: Session = Depends(get_db)
):
    notification = db.query(Notification).filter(
        Notification.id == notification_id
    ).first()

    if not notification:
        raise HTTPException(status_code=404, detail="Not found")

    notification.is_read = True
    db.commit()
    return {"success": True}

# ── Reminder Routes ───────────────────────────────────
@app.post("/reminders")
async def create_reminder(
    payload: ReminderCreate,
    db: Session = Depends(get_db)
):
    reminder = Reminder(
        user_id=payload.user_id,
        title=payload.title,
        note=payload.note,
        remind_at=payload.remind_at
    )
    db.add(reminder)
    db.commit()
    db.refresh(reminder)

    return {
        "id": str(reminder.id),
        "title": reminder.title,
        "remind_at": str(reminder.remind_at),
        "created_at": str(reminder.created_at)
    }

@app.get("/reminders/{user_id}")
async def get_reminders(
    user_id: str,
    db: Session = Depends(get_db)
):
    reminders = db.query(Reminder)\
        .filter(Reminder.user_id == user_id)\
        .filter(Reminder.is_done == False)\
        .order_by(Reminder.remind_at.asc())\
        .all()

    return {
        "reminders": [
            {
                "id": str(r.id),
                "title": r.title,
                "note": r.note,
                "remind_at": str(r.remind_at),
                "is_done": r.is_done
            }
            for r in reminders
        ]
    }

@app.patch("/reminders/{reminder_id}/done")
async def reminder_done(
    reminder_id: str,
    db: Session = Depends(get_db)
):
    reminder = db.query(Reminder).filter(
        Reminder.id == reminder_id
    ).first()

    if not reminder:
        raise HTTPException(status_code=404, detail="Not found")

    reminder.is_done = True
    db.commit()
    return {"success": True}

@app.delete("/reminders/{reminder_id}")
async def delete_reminder(
    reminder_id: str,
    db: Session = Depends(get_db)
):
    reminder = db.query(Reminder).filter(
        Reminder.id == reminder_id
    ).first()

    if not reminder:
        raise HTTPException(status_code=404, detail="Not found")

    db.delete(reminder)
    db.commit()
    return {"success": True}