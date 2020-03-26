#!/usr/bin/env python
from flask import Flask, session, request, g, current_app
from flask_socketio import SocketIO, emit, disconnect

async_mode = "eventlet"


app = Flask(__name__)
app.config['SECRET_KEY'] = 'cannot be guessed'
socketio = SocketIO(app, async_mode=async_mode, cors_allowed_origins="*")


@socketio.on('my_event', namespace='/test')
def test_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': message['data'], 'count': session['receive_count']})


@socketio.on('my_ping', namespace='/test')
def ping_pong():
    emit('my_pong')


@socketio.on('connect', namespace='/test')
def test_connect():
    emit('my_response', {'data': 'Connected', 'count': 0})


@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected', request.sid)


if __name__ == '__main__':
    socketio.run(app, debug=True)

