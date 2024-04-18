from flask import Flask, jsonify, request, Response
from flask_socketio import SocketIO, join_room, leave_room
from flask_jwt_extended import JWTManager, create_access_token, unset_access_cookies, jwt_required, get_jwt_identity
from db import get_user, save_user
from dotenv import load_dotenv
from datetime import timedelta
import os

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
app.config['JWT_TOKEN_LOCATION'] = ['headers', 'cookies']
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=360)
app.config['JWT_COOKIE_SECURE'] = True
app.config['JWT_COOKIE_SAMESITE'] = 'None'

socketio = SocketIO(app, cors_allowed_origins="*")
jwt = JWTManager(app)

@app.route('/',methods=['GET'])
@jwt_required() 
def home():
    current_username = get_jwt_identity()
    return jsonify({'username': current_username}), 200

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password_input = data.get('password')

    if not username or not password_input:
        return jsonify({'error': 'Invalid credentials'}), 400
    
    user = get_user(username)
    if user and user.check_password(password_input):
        access_token = create_access_token(identity=user.get_id())
        res = jsonify(accessToken=access_token, username = user.get_id())
        return res
    else:
        return jsonify({'error':'Failed to login'}), 401

@app.route('/logout', methods=['POST'])   
@jwt_required() 
def logout():
    print('Received POST request for /logout')
    res = Response(status=204)
    unset_access_cookies(res)
    return res

@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data.get('username')
    password_input = data.get('password')

    if not username or not password_input:
        return jsonify({'error': 'Invalid credentials'}), 400
    
    user = get_user(username)
    if user:
        return jsonify({'error': 'This username has been used!'}), 400    
        
    else:
        save_user(username, password_input)
        access_token = create_access_token(identity=username)
        res = jsonify(accessToken=access_token, username = username)
        return res
        

@socketio.on('send_message')
def handle_send_message_event(data):
    app.logger.info("{} has sent message to the room {}: {}".format(data['username'],
                                                                    data['room'],
                                                                    data['message']))
    socketio.emit('receive_message', data, room=data['room'])


@socketio.on('join_room')
def handle_join_room_event(data):
    app.logger.info("{} has joined the room {}".format(data['username'], data['room']))
    join_room(data['room'])
    socketio.emit('join_room_announcement', data, room=data['room'])


@socketio.on('leave_room')
def handle_leave_room_event(data):
    app.logger.info("{} has left the room {}".format(data['username'], data['room']))
    leave_room(data['room'])
    socketio.emit('leave_room_announcement', data, room=data['room'])

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5050)