import os
from services.sessions_service import SessionsService
from services.database_user_service import DataBaseUserService, DataBaseUserRepo
from services.database_map_service import DataBaseMapRepo, DataBaseMapService
from dotenv import load_dotenv

load_dotenv()

sessions_service = SessionsService(os.getenv("SECRET_KEY"))

database_user_repo = DataBaseUserRepo()
database_user_service = DataBaseUserService(database_user_repo)

database_map_repo = DataBaseMapRepo()
database_map_service = DataBaseMapService(database_map_repo)


def get_sessions_service():
    return sessions_service


def get_database_user_service():
    return database_user_service


def get_database_map_service():
    return database_map_service