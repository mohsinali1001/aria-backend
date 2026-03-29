from supabase import create_client, Client
from dotenv import load_dotenv
import os

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")

print("Connecting to Supabase...")

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
    print("✅ Supabase connected successfully!")
except Exception as e:
    print(f"❌ Supabase connection failed: {e}")
    supabase = None

def get_supabase() -> Client:
    if supabase is None:
        raise Exception("Supabase not connected")
    return supabase