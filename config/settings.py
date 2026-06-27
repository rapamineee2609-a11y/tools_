import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings:
    APP_NAME = os.getenv("APP_NAME", "Cyber Security Suite Pro 2026")
    APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR}/cyber-suite.db")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    REPORT_PATH = Path(os.getenv("REPORT_PATH", "./reports"))
    
    # Directories
    BASE_DIR = BASE_DIR
    CONFIG_DIR = BASE_DIR / "config"
    MODULES_DIR = BASE_DIR / "modules"
    LOGS_DIR = BASE_DIR / "logs"
    PLUGINS_DIR = BASE_DIR / "plugins"
    
    # Create directories
    for dir_path in [REPORT_PATH, LOGS_DIR, PLUGINS_DIR]:
        dir_path.mkdir(exist_ok=True)

settings = Settings()
