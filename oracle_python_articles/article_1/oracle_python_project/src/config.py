import pathlib
from os import environ, path

from dotenv import load_dotenv

PROJECT_ROOT = pathlib.Path(__file__).parent.parent.absolute()
TEMPLATES_DIR = "templates"
OUTPUT_DIR = "output"
MEV_FILE_EXTENSION = "*.txt"
REPORT_EXTENSION = ".xlsx"

load_dotenv(path.join(PROJECT_ROOT, ".env"))


def get_oracle_db_uri() -> str:
    """
    Load MPS database environment variables from .env
    :return: string db connection
    """
    host = environ.get("DB_HOST")
    user = environ.get("DB_USER")
    password = environ.get("DB_PASSWORD")
    service_name = environ.get("DB_SERVICE")
    port = environ.get("DB_PORT")
    return f"oracle+cx_oracle://{user}:{password}@{host}:{port}/{service_name}"
