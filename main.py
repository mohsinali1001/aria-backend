from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from database import get_supabase
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI(
    title="ARIA Backend API",
    description="AI Personal Secretary — FastAPI Backend with Supabase",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Schemas ───────────────────────────────────────────────────────────────
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

class EmailSummaryCreate(BaseModel):
    user_id: str
    from_email: str
    from_name: Optional[str] = None
    subject: str
    body: Optional[str] = None
    summary: Optional[str] = None
    priority: Optional[str] = "normal"

# ── Health Check ──────────────────────────────────────────────────────────
@app.get("/")
async def root():
    return {
        "status": "ARIA Backend Running ✅",
        "version": "1.0.0",
        "docs": "/docs"
    }

# ── User Routes ───────────────────────────────────────────────────────────
@app.post("/users")
async def create_or_get_user(payload: UserCreate):
    try:
        db = get_supabase()

        # Check if user already exists
        existing = db.table("users") \
            .select("*") \
            .eq("firebase_uid", payload.firebase_uid) \
            .execute()

        if existing.data:
            return {**existing.data[0], "existing": True}

        # Create new user
        result = db.table("users").insert({
            "firebase_uid": payload.firebase_uid,
            "email": payload.email,
            "name": payload.name
        }).execute()

        if not result.data:
            raise HTTPException(status_code=500, detail="Failed to create user")

        return {**result.data[0], "existing": False}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/users/{firebase_uid}")
async def get_user(firebase_uid: str):
    try:
        db = get_supabase()

        result = db.table("users") \
            .select("*") \
            .eq("firebase_uid", firebase_uid) \
            .execute()

        if not result.data:
            raise HTTPException(status_code=404, detail="User not found")

        return result.data[0]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Notification Routes ───────────────────────────────────────────────────
@app.post("/notify")
async def notify(payload: NotifyPayload):
    try:
        db = get_supabase()

        # Check for duplicate message
        existing = db.table("notifications") \
            .select("*") \
            .eq("message_id", payload.message_id) \
            .execute()

        if existing.data:
            return {
                "success": True,
                "notification_id": existing.data[0]["id"],
                "duplicate": True
            }

        # Insert new notification
        result = db.table("notifications").insert({
            "from_email": payload.from_email,
            "subject": payload.subject,
            "message": payload.message,
            "category": payload.category,
            "message_id": payload.message_id,
            "user_id": payload.user_id,
            "is_read": False
        }).execute()

        if not result.data:
            raise HTTPException(status_code=500, detail="Failed to create notification")

        return {
            "success": True,
            "notification_id": result.data[0]["id"],
            "duplicate": False
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/notifications")
async def get_all_notifications():
    try:
        db = get_supabase()

        result = db.table("notifications") \
            .select("*") \
            .order("created_at", desc=True) \
            .limit(50) \
            .execute()

        return {
            "notifications": result.data,
            "count": len(result.data)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/notifications/{user_id}")
async def get_user_notifications(user_id: str):
    try:
        db = get_supabase()

        result = db.table("notifications") \
            .select("*") \
            .eq("user_id", user_id) \
            .order("created_at", desc=True) \
            .limit(50) \
            .execute()

        return {
            "notifications": result.data,
            "count": len(result.data)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.patch("/notifications/{notification_id}/read")
async def mark_notification_read(notification_id: str):
    try:
        db = get_supabase()

        result = db.table("notifications") \
            .update({"is_read": True}) \
            .eq("id", notification_id) \
            .execute()

        if not result.data:
            raise HTTPException(status_code=404, detail="Notification not found")

        return {"success": True, "id": notification_id}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/notifications/{notification_id}")
async def delete_notification(notification_id: str):
    try:
        db = get_supabase()

        db.table("notifications") \
            .delete() \
            .eq("id", notification_id) \
            .execute()

        return {"success": True}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Reminder Routes ───────────────────────────────────────────────────────
@app.post("/reminders")
async def create_reminder(payload: ReminderCreate):
    try:
        db = get_supabase()

        result = db.table("reminders").insert({
            "user_id": payload.user_id,
            "title": payload.title,
            "note": payload.note,
            "remind_at": payload.remind_at,
            "is_done": False
        }).execute()

        if not result.data:
            raise HTTPException(status_code=500, detail="Failed to create reminder")

        return {
            "success": True,
            "reminder": result.data[0]
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/reminders/{user_id}")
async def get_reminders(user_id: str):
    try:
        db = get_supabase()

        result = db.table("reminders") \
            .select("*") \
            .eq("user_id", user_id) \
            .eq("is_done", False) \
            .order("remind_at", desc=False) \
            .execute()

        return {
            "reminders": result.data,
            "count": len(result.data)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/reminders/{user_id}/all")
async def get_all_reminders(user_id: str):
    try:
        db = get_supabase()

        result = db.table("reminders") \
            .select("*") \
            .eq("user_id", user_id) \
            .order("remind_at", desc=False) \
            .execute()

        return {
            "reminders": result.data,
            "count": len(result.data)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.patch("/reminders/{reminder_id}/done")
async def mark_reminder_done(reminder_id: str):
    try:
        db = get_supabase()

        result = db.table("reminders") \
            .update({"is_done": True}) \
            .eq("id", reminder_id) \
            .execute()

        if not result.data:
            raise HTTPException(status_code=404, detail="Reminder not found")

        return {"success": True, "id": reminder_id}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/reminders/{reminder_id}")
async def delete_reminder(reminder_id: str):
    try:
        db = get_supabase()

        db.table("reminders") \
            .delete() \
            .eq("id", reminder_id) \
            .execute()

        return {"success": True}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Email Summary Routes ──────────────────────────────────────────────────
@app.post("/email-summaries")
async def create_email_summary(payload: EmailSummaryCreate):
    try:
        db = get_supabase()

        result = db.table("email_summaries").insert({
            "user_id": payload.user_id,
            "from_email": payload.from_email,
            "from_name": payload.from_name,
            "subject": payload.subject,
            "body": payload.body,
            "summary": payload.summary,
            "priority": payload.priority,
            "is_read": False
        }).execute()

        if not result.data:
            raise HTTPException(status_code=500, detail="Failed to create email summary")

        return {
            "success": True,
            "email_summary": result.data[0]
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/email-summaries/{user_id}")
async def get_email_summaries(user_id: str):
    try:
        db = get_supabase()

        result = db.table("email_summaries") \
            .select("*") \
            .eq("user_id", user_id) \
            .order("created_at", desc=True) \
            .limit(20) \
            .execute()

        return {
            "emails": result.data,
            "count": len(result.data)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.patch("/email-summaries/{email_id}/read")
async def mark_email_read(email_id: str):
    try:
        db = get_supabase()

        result = db.table("email_summaries") \
            .update({"is_read": True}) \
            .eq("id", email_id) \
            .execute()

        if not result.data:
            raise HTTPException(status_code=404, detail="Email summary not found")

        return {"success": True, "id": email_id}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))