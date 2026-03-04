import os
from dotenv import load_dotenv
load_dotenv()

# Model paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MODEL_DIR = os.path.join(BASE_DIR, "app", "models")

TESTING_MODE = os.getenv("TESTING_MODE", "false").lower() == "true"