from func_timeout import func_timeout, FunctionTimedOut
from sqlalchemy import create_engine
from sqlalchemy.sql import text
from datetime import datetime
import time
import json
import threading
import pandas as pd

"""
HEARTBEAT_TIMEOUT: this is the tempo of how often every connection will be checked (in seconds).
CONNECTION_TIMEOUT: this is the number of seconds to wait before giving up on a connection.
"""
HEARTBEAT_TIMEOUT = 60
CONNECTION_TIMEOUT = 10
    
def generate_cbo_connection_list(cbo_df: pd.DataFrame):
    get_test_query = lambda cbo: f"SELECT * FROM OPENQUERY([OAK{cbo}],'SELECT TOP 1 1 AS ON_OFF_FLAG from vw_ODBC_main_AccountsReceivable');"
    
    cbo_connection_entries = [
        {
            'name': f"cbo_{d['LicenseKey']}",
            '_type': 'sqlalchemy',
            'connection_string': 'mssql+pyodbc:///?odbc_connect=DSN%3DRCM%3BUID%3Ddatajobs%3BPWD%3DDmIk0ObJlnq5NTN54BjK',
            'properties': json.dumps({
                'type': 'cbo', 
                'license_key': d['LicenseKey'], 
                'test_query': get_test_query(d['LicenseKey'])
            })
        }
        for d in cbo_df.to_dict('records')
    ]
    
    return cbo_connection_entries


def log_to_db(engine, connection_name: str, status: bool, created_at, stacktrace=None):
    with engine.connect() as con:
        # Put the args into a dict for insertion
        data = { "connection_name": connection_name, "status": int(status), "created_at": created_at, "stacktrace": stacktrace }

        # Form the insert statement
        statement = text("INSERT INTO insight.logs(connection_name, status, created_at, stacktrace) VALUES(:connection_name, :status, :created_at, :stacktrace)")

        # Execute statement
        con.execute(statement, **data)


def connect(connection, connection_timeout_seconds=1):  
    """
    Attempts to make contact with a given connection object.
    """
    
    created_at = datetime.utcnow()
    log_engine = pg_etl_engine
    
    # Create test_engine; for now, assume SQLAlchemy
    test_engine = create_engine(con['connection_string'] if con['_type'] == 'sqlalchemy' else None)
    
    # If connection.properties exists, use the test_query in it; otherwise use the default "select 1" query
    test_connection_query = connection['properties']['test_query'] if (connection.get('properties')) else 'select 1'
    
    # Attempt to connect to the current database
    try:
        func_timeout(
            timeout=connection_timeout_seconds,
            func=pd.read_sql,
            kwargs=dict(
                sql=test_connection_query, 
                con=test_engine,
            ),
        )
        
    except (FunctionTimedOut, Exception) as e:
        # connection failed
        print(f"{connection['name']}: FAILED")
#        log_to_db(
#            engine=log_engine, 
#            connection_name=connection['name'],
#            status=False,
#            created_at=created_at,
#            stacktrace=str(e)
#        )

        return {
	    'engine': log_engine,
	    'connection_name': connection['name'],
	    'status': False,
	    'created_at': created_at,
	    'stacktrace': str(e),
	}
    
    # connection successful
    #print(f"{connection['name']}: SUCCESS")
    #log_to_db(
    #    engine=log_engine, 
    #    connection_name=connection['name'],
    #    status=True,
    #    created_at=created_at,
    #    stacktrace=None
    #)

    return {
	'engine': log_engine,
	'connection_name': connection['name'],
	'status': True,
	'created_at': created_at,
	'stacktrace': None,
    }


connect_and_log = lambda connection, con_timeout: log_to_db(**connect(connection, connection_timeout_seconds=con_timeout))
        
        
if __name__ == '__main__':
    print("Starting main thread")
    
    # Create Connections
    pg_etl_connection_string = 'postgres://postgres:docker@172.23.4.217:8089/postgres'
    pg_etl_engine = create_engine(pg_etl_connection_string, use_batch_mode=True)
    pg_schema = 'insight'
    
    #mbs_connection_string = 'mssql+pyodbc:///?odbc_connect=DSN%3DRCM%3BUID%3Ddatajobs%3BPWD%3DDmIk0ObJlnq5NTN54BjK'
    #mbs_engine = create_engine(mbs_connection_string)
    

    while True:
        print()
        print(f'Start heartbeat: {datetime.today().strftime("%d %B %Y, %H:%M:%S")}')
        print('='*50)

        # Get DB Connections
        connections_df = pd.read_sql('select * from insight.connections', con=pg_etl_engine)

        # Check DB connectivity
        for con in connections_df.to_dict('records'):
            t = threading.Thread(
                target=connect_and_log,
                kwargs=dict(
                    connection=con,
		    con_timeout=CONNECTION_TIMEOUT,
                )
            )
            t.start()

        # Print number of threads
        print('<<<')
        print(f"Number of Threads: {len(threading.enumerate())}")
        print('>>>')

	# Sleep for the duration of the HEARTBEAT_TIMEOUT before checking again.
        time.sleep(HEARTBEAT_TIMEOUT)
