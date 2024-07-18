from google.oauth2 import service_account

from config import SA_KEY_PATH


credentials = service_account.Credentials.from_service_account_file(SA_KEY_PATH)
