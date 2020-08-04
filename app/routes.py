import json
import threading

from flask import Flask, render_template
from flask_socketio import SocketIO

from config import Session, HEARTBEAT_TIMEOUT
from engine.models.tables import DBCurrentStatus

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
    print('Starting Cogsworth')
    cogsworth_update()


@set_interval(HEARTBEAT_TIMEOUT)
def cogsworth_update():
    update_all()


def update_all():
    print('Cogsworth UPDATE!')
    insight_session = Session()

    # Testing: send some data from the insight database
    db_status_list = [dict(name=row.name, status=row.status, timestamp=row.timestamp.strftime('%d %B %Y %H:%M:%S UTC'))
                      for row in insight_session.query(DBCurrentStatus).all()]

    # TODO: send all data from
    update_client(payload={'db_status_list': db_status_list}, channel='db_connection_status')


@app.route('/')
def index_endpoint():
    return render_template('home.html')


@app.route('/database_uptime')
def db_uptime_endpoint():
    return render_template('database_uptime.html')


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
    update_all()


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
