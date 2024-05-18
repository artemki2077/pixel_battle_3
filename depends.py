import os

from pydantic_redis import RedisConfig

from services.sessions_service import SessionsService
from services.database_user_service import DataBaseUserService, DataBaseUserRepo
from services.database_map_service import DataBaseMapRepo, DataBaseMapService
from dotenv import load_dotenv

load_dotenv()

sessions_service = SessionsService(os.getenv("SECRET_KEY"))

database_user_repo = DataBaseUserRepo(redis_config=RedisConfig(host="localhost", port=6379, password=os.getenv("DB_PASSWORD")))
# database_user_repo = DataBaseUserRepo(redis_config=RedisConfig(host="artemki77.ru",port=6379,password=os.getenv("DB_PASSWORD")))

database_user_service = DataBaseUserService(database_user_repo)
database_map_repo = DataBaseMapRepo(password=os.getenv("DB_PASSWORD"))
database_map_service = DataBaseMapService(database_map_repo)


def get_sessions_service():
    return sessions_service


def get_database_user_service():
    return database_user_service


def get_database_map_service():
    return database_map_service