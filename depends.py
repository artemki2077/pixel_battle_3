import os
from services.sessions_service import SessionsService
from dotenv import load_dotenv

load_dotenv()

sessions_service = SessionsService(os.getenv("SECRET_KEY"))