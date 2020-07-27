import time
# from config import Session, engine, Base
from config import Session
from engine.models.tables import SQLDatabase
from datetime import datetime, timezone
from sqlalchemy import create_engine
import threading

    
def connection_status(db_name, db_type, connection_string, timeout=25, format_str='%d-%B-%Y %H:%M:%S %Z'):
    try:
        engine = create_engine(connection_string, connect_args={'connect_timeout': timeout})
        with engine.connect() as connection:
            connection.execute('select 1')	
        output = {
            'status': True,
            'timestamp': datetime.now(timezone.utc).strftime(format_str),
            'db_name': db_name,
            'db_type': db_type,
        }
        print(output)
        return output

    except Exception as e:
        output = {
            'status': False,
            'exception': str(e),
            'timestamp':  datetime.now(timezone.utc).strftime(format_str),
            'db_name': db_name,
            'db_type': db_type,
        }
        print(output)
        return output


if __name__ == '__main__':
    heartbeat_timeout = 10  # seconds
    session = Session()

    print("Starting main thread")

    while True:
        print()
        print(f'Start heartbeat: {datetime.today().strftime("%d %B %Y, %H:%M:%S")}')
        print('='*50)

        # Get DB Connections
        sql_dbs = session.query(SQLDatabase).all()

        # Check DB connectivity
        for conn in sql_dbs:
            t = threading.Thread(target=connection_status,
                                 kwargs=dict(connection_string=conn.connection_string,
                                             db_name=conn.db_name,
                                             db_type=conn.db_type)
                                 )
            t.start()

        # Print number of threads
        print('<<<')
        print(f"Threads: {threading.enumerate()}")
        print('>>>')

        time.sleep(heartbeat_timeout)
