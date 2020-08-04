import time
# from config import Session, engine, Base
from config import Session, HEARTBEAT_TIMEOUT, CONNECTION_TIMEOUT
from engine.models.tables import SQLDatabase, DBCurrentStatus, StatusLog
from datetime import datetime, timezone
from sqlalchemy import create_engine
import threading

    
def log_connection_status(db_name,
                          connection_string,
                          timeout=CONNECTION_TIMEOUT,
                          format_str='%d-%B-%Y %H:%M:%S %Z'):
    """
    Attempt to connect to a given database. Log the info in the Insight DB.

    :param db_name:
    :param connection_string:
    :param timeout:
    :param format_str:
    :return:
    """
    # Create a session to the Insight Database
    insight_session = Session()

    # Create a connection engine for the database we are checking in this thread
    try:
        engine = create_engine(connection_string, connect_args={'connect_timeout': timeout})

        # Check the connection
        with engine.connect() as connection:
            connection.execute('select 1')

        output = {
            'name': db_name,
            'status': True,
            'timestamp': datetime.now(timezone.utc),
        }

    except Exception as e:
        output = {
            'name': db_name,
            'status': False,
            'log': str(e),
            'timestamp':  datetime.now(timezone.utc),
        }

    finally:
        # Update current DB Status (`db_status` table)
        db_status = DBCurrentStatus(**output)
        status_log = StatusLog(**output)

        insight_session.merge(db_status)    # merge: insert or update
        insight_session.add(status_log)     # append

        insight_session.commit()
        insight_session.close()


if __name__ == '__main__':
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
            t = threading.Thread(target=log_connection_status,
                                 kwargs=dict(connection_string=conn.connection_string,
                                             db_name=conn.name)
                                 )
            t.start()

        # Print number of threads
        print('<<<')
        print(f"Threads: {threading.enumerate()}")
        print('>>>')

        time.sleep(HEARTBEAT_TIMEOUT)
