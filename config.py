import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


# base directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# InsightDB path (sqlite3 database)
META_DB_PATH = os.path.join(BASE_DIR, 'metadata.sqlite3')

# InsightDB connection string
META_DB_CONNECTION_STRING = f'sqlite:///{META_DB_PATH}'

# Number of seconds to wait between checks
HEARTBEAT_TIMEOUT = 60

# ----------------------------- #
# SQLAlchemy Connection Objects #
# ----------------------------- #
engine = create_engine(META_DB_CONNECTION_STRING)
Session = sessionmaker(bind=engine)
Base = declarative_base()
