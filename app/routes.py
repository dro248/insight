from flask import Flask, render_template, make_response
from flask_socketio import SocketIO, send, emit
from datetime import datetime
import json
from config import Session, HEARTBEAT_TIMEOUT
from engine.models.tables import SQLDatabase
import threading

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)


# -------------------------------------------------------------------#
# Flask app routes
# -------------------------------------------------------------------#

def set_interval(interval):
    def decorator(function):
        def wrapper(*args, **kwargs):
            stopped = threading.Event()

            def loop():  # executed in another thread
                while not stopped.wait(interval):   # until stopped
                    function(*args, **kwargs)

            t = threading.Thread(target=loop)
            t.daemon = True  # stop if the program exits
            t.start()
            return stopped
        return wrapper
    return decorator


@app.before_first_request
def start_cogsworth():
    """
    Start Cogsworth - the timekeeper thread that will make sure that the client sockets will
    all be updated every HEARTBEAT_TIMEOUT.
    :return:
    """
    print('Yop!')
    cogsworth_update()


@set_interval(3)
def cogsworth_update():
    update_all()


def update_all():
    print('Cogsworth says: DING!')
    insight_session = Session()

    # Testing: send some data from the insight database
    sql_dbs_list = [dict(name=row.db_name, status=True, timestamp=datetime.utcnow().strftime('%d %B %Y %H:%M:%S UTC'))
                    for row in insight_session.query(SQLDatabase).all()]

    # TODO: send all data from
    update_client(payload={'db_status_list': sql_dbs_list}, channel='db_connection_status')


@app.route('/')
def index_endpoint():
    return render_template('index.html')


@app.route('/demo')
def demo_endpoint():
    return render_template('index_demo.html')


@app.route('/update')
def update_endpoint():
    """
    This endpoint will be triggered by the heartbeat timekeeper.
    It will trigger a SocketIO broadcast to all clients.
    :return:
    """
    update_all()
    return 'Update Received'


# -------------------------------------------------------------------#
# SocketIO event handlers
# -------------------------------------------------------------------#

# Receive Messages
@socketio.on('message')
def handle_message(message):
    print(f'received message: {message}')

    data1 = dict(
        name='postgres_rds',
        status=True,
        timestamp=datetime.utcnow().strftime('%d %B %Y %H:%M:%S UTC'),
    )
    data2 = dict(
        name='rcm_odbc',
        status=False,
        timestamp=datetime.utcnow().strftime('%d %B %Y %H:%M:%S UTC'),
    )
    data3 = dict(
        name='airflow_metadata_db',
        status=True,
        timestamp=datetime.utcnow().strftime('%d %B %Y %H:%M:%S UTC'),
    )

    update_client(payload={'db_status_list': [data1, data2, data3]},
                  channel='db_connection_status')


# Send Messages
def update_client(payload, channel: str):
    """
    Sends a message to the frontend containing the serialized (JSON format) payload.

    :param payload: (required: `payload` object must be hashable)
    :param channel: (str) this should be within the set of supported channels.
    :return:
    """
    supported_channels = {'db_connection_status'}

    # Let the function caller know that this failed.
    if channel not in supported_channels:
        raise ValueError(f"Channel ('{channel}') not in supported_channels ({supported_channels})")

    # Send the message
    socketio.emit(channel, json.dumps(payload), broadcast=True)


if __name__ == '__main__':
    socketio.run(app=app, debug=True, use_reloader=True)
