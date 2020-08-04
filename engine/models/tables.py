from sqlalchemy import Integer, Column, Text, DateTime, Boolean
from config import Base


class SQLDatabase(Base):
    __tablename__ = 'sql_databases'

    name = Column('name', Text, primary_key=True)
    db_type = Column('db_type', Text)
    connection_string = Column('connection_string', Text)

    def __init__(self, name, db_type, connection_string):
        self.name = name
        self.db_type = db_type
        self.connection_string = connection_string


class DBCurrentStatus(Base):
    __tablename__ = 'db_current_status'
    name = Column('name', Text, primary_key=True)
    status = Column('status', Boolean)
    log = Column('log', Text, nullable=True)
    timestamp = Column('timestamp', DateTime)

    def __init__(self, name: str, status: str, timestamp: DateTime, log: str = None):
        self.name = name
        self.status = status
        self.log = log
        self.timestamp = timestamp


class StatusLog(Base):
    __tablename__ = 'status_log'
    status_id = Column('id', Integer, primary_key=True)
    name = Column('name', Text)
    status = Column('status', Boolean)
    log = Column('log', Text, nullable=True)
    timestamp = Column('timestamp', DateTime)

    def __init__(self, name: str, status: str, timestamp: DateTime, log: str = None):
        self.name = name
        self.status = status
        self.log = log
        self.timestamp = timestamp
