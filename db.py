from google.cloud import firestore

from sa import credentials
from config import DATABASE_NAME


db = firestore.AsyncClient(credentials=credentials, database=DATABASE_NAME)
