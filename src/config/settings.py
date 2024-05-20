import os
from dotenv import load_dotenv

load_dotenv()

IDENTIFIER = os.getenv('IDENTIFIER')
KEY = os.getenv('KEY')
SECRET = os.getenv('SECRET')
SITE_ID = os.getenv('SITE_ID')
