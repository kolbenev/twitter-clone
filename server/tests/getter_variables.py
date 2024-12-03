"""
Модуль получения переменных из окружения для тестирования.
"""

import os

import dotenv


dotenv.load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
DB_HOST = os.getenv("DB_HOST")

TEST_APIKEY = os.getenv("APIKEY")
TEST_USERNAME = os.getenv("USERNAME")
API_URL = os.getenv("API_URL")
