import os

import dotenv

dotenv.load_dotenv()

URL_DB = os.getenv("TEST_DB_URL")
TEST_APIKEY = os.getenv("APIKEY")
TEST_USERNAME = os.getenv("USERNAME")
API_URL = os.getenv("API_URL")
