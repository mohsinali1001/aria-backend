# ARIA Backend API
> AI Personal Secretary — FastAPI Backend

![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.95.2-green)
![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-darkgreen)
![Railway](https://img.shields.io/badge/Hosted-Railway-purple)

ARIA is an AI-powered personal secretary app. This repository contains the FastAPI backend that handles email notifications from n8n, reminder management, and user data — all powered by Supabase (PostgreSQL).

---

## Architecture

```
Gmail → n8n Workflow → POST /notify → Supabase (notifications table)
                                            ↓
Flutter App ←────── GET /notifications ────┘
Firebase Auth → POST /users → Supabase (users table)
Flutter App → POST /reminders → Supabase (reminders table)
```

---

## Tech Stack

| Technology | Purpose |
|---|---|
| FastAPI | REST API framework |
| Supabase | PostgreSQL cloud database |
| Python Supabase Client | Database operations |
| Uvicorn | ASGI server |
| Railway | Cloud deployment |
| n8n | Gmail automation workflows |

---

## API Endpoints

### Health Check
```
GET /
```
Returns server status.

---

### Users
```
POST /users
```
Creates or retrieves a user after Firebase authentication.

**Request body:**
```json
{
  "firebase_uid": "firebase_user_id",
  "email": "user@example.com",
  "name": "User Name"
}
```

**Response:**
```json
{
  "id": "uuid",
  "firebase_uid": "firebase_user_id",
  "email": "user@example.com",
  "name": "User Name",
  "created_at": "2026-03-29T00:00:00",
  "existing": false
}
```

---

### Notifications (Emails from n8n)
```
POST /notify
```
Called by n8n when a new email arrives in Gmail.

**Request body:**
```json
{
  "from_email": "sender@gmail.com",
  "subject": "Meeting Tomorrow",
  "message": "Full email body text here",
  "category": "inbox",
  "message_id": "unique_gmail_message_id",
  "user_id": "optional_user_uuid"
}
```

**Response:**
```json
{
  "success": true,
  "notification_id": "uuid"
}
```

---

```
GET /notifications
```
Returns all notifications ordered by date.

---

```
GET /notifications/{user_id}
```
Returns notifications for a specific user.

---

```
PATCH /notifications/{notification_id}/read
```
Marks a notification as read.

---

### Reminders
```
POST /reminders
```
Creates a new reminder.

**Request body:**
```json
{
  "user_id": "user_uuid",
  "title": "Follow up with client",
  "note": "Call Ahmed about the contract",
  "remind_at": "2026-04-01T09:00:00"
}
```

---

```
GET /reminders/{user_id}
```
Returns all pending reminders for a user.

---

```
PATCH /reminders/{reminder_id}/done
```
Marks a reminder as completed.

---

```
DELETE /reminders/{reminder_id}
```
Deletes a reminder permanently.

---

## Database Schema

### users
| Column | Type | Description |
|---|---|---|
| id | uuid | Primary key |
| firebase_uid | text | Firebase Auth UID |
| email | text | User email |
| name | text | Display name |
| created_at | timestamptz | Creation timestamp |

### notifications
| Column | Type | Description |
|---|---|---|
| id | uuid | Primary key |
| user_id | uuid | References users.id |
| from_email | text | Sender email |
| subject | text | Email subject |
| message | text | Email body |
| category | text | Email category |
| message_id | text | Gmail message ID (unique) |
| is_read | boolean | Read status |
| created_at | timestamptz | Creation timestamp |

### reminders
| Column | Type | Description |
|---|---|---|
| id | uuid | Primary key |
| user_id | uuid | References users.id |
| title | text | Reminder title |
| note | text | Optional note |
| remind_at | timestamptz | Reminder datetime |
| is_done | boolean | Completion status |
| created_at | timestamptz | Creation timestamp |

### email_summaries
| Column | Type | Description |
|---|---|---|
| id | uuid | Primary key |
| user_id | uuid | References users.id |
| from_email | text | Sender email |
| from_name | text | Sender name |
| subject | text | Email subject |
| body | text | Full email body |
| summary | text | AI generated summary |
| priority | text | normal / high / urgent |
| is_read | boolean | Read status |
| created_at | timestamptz | Creation timestamp |

---

## Local Setup

### Prerequisites
- Python 3.11+
- Supabase account
- Git

### 1. Clone the repository
```bash
git clone https://github.com/mohsinali1001/aria-backend.git
cd aria-backend
```

### 2. Create virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Create `.env` file
Create a `.env` file in the project root:
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_KEY=your_service_role_key
SECRET_KEY=your_secret_key
```

Get these values from:
- `SUPABASE_URL` → Supabase Dashboard → Settings → API → Project URL
- `SUPABASE_ANON_KEY` → Supabase Dashboard → Settings → API → anon public key
- `SUPABASE_SERVICE_KEY` → Supabase Dashboard → Settings → API → service_role key (click Reveal)

### 5. Set up Supabase tables
Go to Supabase → SQL Editor → New Query and run the SQL from `supabase_schema.sql`

### 6. Run the server
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 7. Open API docs
```
http://localhost:8000/docs
```

---

## Deployment (Railway)

### 1. Push to GitHub
```bash
git add .
git commit -m "your message"
git push origin main
```

### 2. Deploy on Railway
1. Go to `railway.app`
2. Sign up with GitHub
3. Click **New Project** → **Deploy from GitHub repo**
4. Select `aria-backend`
5. Railway auto-detects Python and deploys

### 3. Add environment variables
In Railway → your project → **Variables** tab, add:
```
SUPABASE_URL
SUPABASE_ANON_KEY
SUPABASE_SERVICE_KEY
SECRET_KEY
```

### 4. Get your public URL
Railway → Settings → Domains → copy your URL

---

## n8n Integration

When setting up n8n to forward Gmail emails to this backend:

**HTTP Request Node settings:**
- Method: `POST`
- URL: `https://your-railway-url.up.railway.app/notify`
- Headers:
  - `Content-Type: application/json`
- Body:
```json
{
  "from_email": "{{$json.from}}",
  "subject": "{{$json.subject}}",
  "message": "{{$json.snippet}}",
  "category": "inbox",
  "message_id": "{{$json.id}}"
}
```

---

## Flutter Integration

Add your backend URL to Flutter `.env`:
```env
BACKEND_URL=https://your-railway-url.up.railway.app
```

Flutter calls these endpoints to:
- Sync user after login → `POST /users`
- Fetch email notifications → `GET /notifications/{user_id}`
- Create reminders → `POST /reminders`
- Fetch reminders → `GET /reminders/{user_id}`

---

## Project Structure

```
aria-backend/
├── main.py              # FastAPI app and all endpoints
├── database.py          # Supabase client setup
├── requirements.txt     # Python dependencies
├── Procfile             # Railway deployment config
├── runtime.txt          # Python version for Railway
├── .env                 # Environment variables (never commit)
├── .gitignore           # Git ignore rules
└── README.md            # This file
```

---

## Team

| Developer | Role |
|---|---|
| Mohsin | Backend & Auth |
| Huzaifa | Frontend |
| Team Member 3 | n8n Integration |
| Team Member 4 | AI & Chat |

---

## Related Repositories

- **Flutter App:** `aria-flutter-app` — Mobile frontend
- **Backend:** `aria-backend` — This repository

---

## License

This project is private and confidential. All rights reserved © 2026 ARIA Team.
