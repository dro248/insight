import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session


# base directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# InsightDB path (sqlite3 database)
META_DB_PATH = os.path.join(BASE_DIR, 'insight.sqlite3')

# InsightDB connection string
META_DB_CONNECTION_STRING = f'sqlite:///{META_DB_PATH}'

# Number of seconds to wait between checks
HEARTBEAT_TIMEOUT = 60

# Number of seconds to wait on a connection before terminating
CONNECTION_TIMEOUT = 10

# ----------------------------- #
# SQLAlchemy Connection Objects #
# ----------------------------- #
engine = create_engine(META_DB_CONNECTION_STRING)
session_factory = sessionmaker(bind=engine)

# Use a scoped_session for this to work well with use in different threads
Session = scoped_session(session_factory)

Base = declarative_base()
