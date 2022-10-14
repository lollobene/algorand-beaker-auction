from dotenv import load_dotenv
import os

load_dotenv()
PURESTAKE_API_KEY = os.getenv('PURESTAKE_API_KEY')
print(PURESTAKE_API_KEY)