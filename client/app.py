from flask import Flask, make_response, render_template, request, redirect, url_for
from dotenv import load_dotenv
import os
import requests

app = Flask(__name__)

# Load environment variables from .env file
load_dotenv()
# Set default backend URL (fallback if BACKEND_URL is not defined)
BACKEND_URL = os.getenv('BACKEND_URL', 'http://127.0.0.1:5050')


def get_access_token():
    return request.cookies.get('access_token')

@app.before_request
def require_login():
    # Exclude routes that do not require login (e.g., login, home)
    print('require login checking')
    if request.endpoint and request.endpoint not in ['login','signup']:
        access_token = get_access_token()
        if not access_token:
            # Redirect to login page if access token is missing
            return redirect(url_for('login'))
        
@app.route('/')
def home():
    home_url = f"{BACKEND_URL}/"
    access_token = get_access_token()
    headers = {'Authorization': f'Bearer {access_token}'}

    try:
        response = requests.get(home_url, headers=headers)
        if response.status_code == 200:
            username = response.json().get('username')
            rooms = response.json().get('rooms')
            return render_template("index.html", username=username, rooms=rooms)
        if response.status_code == 401:
            return redirect(url_for('login'))
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to backend server: {e}")
        return redirect(url_for('login'))

@app.route('/chat')
def chat():
    username = request.args.get('username')
    room = request.args.get('room')

    if username and room:
        return render_template('chat.html', username=username, room=room, backend_url=BACKEND_URL)
    else:
        return redirect(url_for('home'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    message = ''
    if request.method == 'POST':
        username = request.form.get('username')
        password_input = request.form.get('password')

        if username and password_input:
            backend_login_url = f"{BACKEND_URL}/login"
            login_data = {'username': username, 'password': password_input}

            try:
                response = requests.post(backend_login_url, json=login_data)
                if response.status_code == 200:
                    data = response.json()
                    access_token = data.get('accessToken')
                    if access_token:
                        response = make_response(redirect(url_for('home')))
                        response.set_cookie('access_token', access_token)
                        print('Login successfully')
                        return response
                    else:
                        message = 'Access token not found in response'
                else:
                    message = response.json()['error']
            except requests.exceptions.RequestException as e:
                print(f"Error connecting to backend server: {e}")
                message = 'Login failed due to server error. Please try again later.'

    return render_template('login.html', message=message)

@app.route('/logout', methods=['POST'])
def logout():
    backend_logout_url = f"{BACKEND_URL}/logout"
    access_token = get_access_token()
    headers = {'Authorization': f'Bearer {access_token}'}
    try:
        response = requests.post(backend_logout_url, headers=headers)
        if response.status_code == 204:
            print("Logout successfully")
            # Clear the access token cookie upon logout
            response = make_response(redirect(url_for('login')))
            response.set_cookie('access_token', '', expires=0)
            return response
        else:
            print("Cannot logout")
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to backend server: {e}")
    return redirect(url_for('home'))

@app.route('/signup', methods=['GET','POST'])
def signup():
    access_token = get_access_token()
    if access_token:
        return redirect(url_for('home'))
    message = ''
    if request.method == 'POST':
        username = request.form.get('username')
        password_input = request.form.get('password')

        if username and password_input:
            backend_signup_url = f"{BACKEND_URL}/signup"
            signup_data = {'username': username, 'password': password_input}

            try:
                response = requests.post(backend_signup_url, json=signup_data)
                if response.status_code == 200:
                    data = response.json()
                    access_token = data.get('accessToken')
                    if access_token:
                        response = make_response(redirect(url_for('home')))
                        response.set_cookie('access_token', access_token)
                        print('Signup successfully')
                        return response
                    else:
                        message = 'Access token not found in response'
                else:
                    message = response.json()['error']
            except requests.exceptions.RequestException as e:
                print(f"Error connecting to backend server: {e}")
                message = 'Signup failed due to server error. Please try again later.'

    return render_template('signup.html', message=message)

@app.route('/create-room', methods=['GET','POST'])
def create_room():
    access_token = get_access_token()
    headers = {'Authorization': f'Bearer {access_token}'}
    backend_create_room_url = f"{BACKEND_URL}/create-room"
    message = ''
    if request.method == 'POST':
        room_name = request.form.get('room_name')
        members = request.form.get('members')
        if room_name:
            create_room_data = {'room_name': room_name, 'members': members}
            try:
                response = requests.post(backend_create_room_url, json=create_room_data, headers=headers)
                room_id = response.json().get('room_id')
                if response.status_code == 200:
                    return redirect(url_for('view_room', room_id=room_id))
            except requests.exceptions.RequestException as e:
                print(f"Error connecting to backend server: {e}")
                print('Create room failed due to server error. Please try again later.')
        return redirect(url_for('create_room'))
    else:
        try:
            response = requests.get(backend_create_room_url, headers=headers)
            if response.status_code == 200:
                username = response.json().get('username')
                return render_template("create_room.html", username=username, message=message)
            if response.status_code == 401:
                return redirect(url_for('login'))
        except requests.exceptions.RequestException as e:
            print(f"Error connecting to backend server: {e}")
            return redirect(url_for('login'))

@app.route('/rooms/<room_id>/', methods=['GET'])
def view_room(room_id):
    view_room_url = f"{BACKEND_URL}/rooms/{room_id}/"
    access_token = get_access_token()
    headers = {'Authorization': f'Bearer {access_token}'}
    try:
        response = requests.get(view_room_url, headers=headers)
        if response.status_code == 200:
            username = response.json().get('username')
            room = response.json().get('room')
            room_members = response.json().get('room_members')
            return render_template('view_room.html', username=username, room=room, room_members=room_members, backend_url=BACKEND_URL)
            
        if response.status_code == 401:
            return redirect(url_for('login'))
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to backend server: {e}")
        return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)