import os
from services.sessions_service import SessionsService
from services.database_service import DataBaseService, DataBaseRepo
from dotenv import load_dotenv

load_dotenv()

sessions_service = SessionsService(os.getenv("SECRET_KEY"))

database_repo = DataBaseRepo()
database_service = DataBaseService(database_repo)


def get_sessions_service():
    return sessions_service


def get_database_service():
    return database_service
