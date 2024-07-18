from dotenv import load_dotenv
from os import environ

load_dotenv()

SA_KEY_PATH = environ["SA_KEY_PATH"]
BUCKET_NAME = environ["BUCKET_NAME"]
DATABASE_NAME = environ["DATABASE_NAME"]
JWT_KEY = environ["JWT_KEY"]
