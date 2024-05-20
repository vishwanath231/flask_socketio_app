from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import uuid

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode='eventlet', cors_allowed_origins="*")

clients = {}

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    client_id = str(uuid.uuid4())
    clients[client_id] = request.sid
    emit('client_id', {'clientId': client_id})
    print(f"Client connected: {client_id}")
    

@socketio.on('disconnect')
def handle_disconnect():
    client_id = None
    
    for cid, sid in clients.items():
        if sid == request.sid:
            client_id = cid
            break

    if client_id:
        del clients[client_id]
        print(f"Client disconnected: {client_id}")

@socketio.on('message')
def handle_message(data):
    target_client_id = data.get('targetClientId')
    message_content = data.get('message')
    if target_client_id in clients:
        target_sid = clients[target_client_id]
        emit('message', {'from': data.get('from'), 'content': message_content}, room=target_sid)
    else:
        emit('message', {'error': 'Target client ID not found'}, room=request.sid)

if __name__ == '__main__':
    socketio.run(app, port=5001, debug=True)
