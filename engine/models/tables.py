from sqlalchemy import Integer, Column, String, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from config import Base


class SQLDatabase(Base):
    __tablename__ = 'sql_databases'

    db_name = Column('name', String(100), primary_key=True)
    db_type = Column('db_type', String(50))
    connection_string = Column('connection_string', String(300))

    def __init__(self, db_name, db_type, connection_string):
        self.db_name = db_name
        self.db_type = db_type
        self.connection_string = connection_string
