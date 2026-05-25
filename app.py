import eventlet
eventlet.monkey_patch() 
from flask_socketio import SocketIO, emit
from flask import Flask, render_template, request, redirect, session

app = Flask(__name__)
app.secret_key = "secret123"

socketio = SocketIO(app, cors_allowed_origins="*")

# ======================
# DATABASE SEDERHANA
# ======================
users_db = {
    "rin": "123",
    "andi": "123"
}

# ======================
# USER ONLINE
# ======================
online_users = {}

# ======================
# LOGIN
# ======================
@app.route('/track-loc-login', methods=['GET', 'POST'])
def loginlocLogin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username  and users_db['rin'] == password:
            session['username'] = username
            return redirect('/track-im-here')
        else:
            return "Login gagal"

    return render_template('login.html')

@app.route('/denied')
def denied():
    return render_template('denied.html')

# ======================
# MAIN PAGE
# ======================
@app.route('/track-im-here')
def index():
    if 'username' not in session:
        return redirect('/track-loc-login')

    return render_template('index.html', username=session['username'])

# ======================
# SOCKET CONNECT
# ======================
@socketio.on('connect')
def connect():
    username = session.get('username')

    if not username:
        return False  # tolak kalau belum login

    sid = request.sid

    online_users[sid] = {
        "name": username,
        "lat": None,
        "lng": None
    }

    emit('init', {
        "sid": sid,
        "users": online_users
    })

    emit('user_joined', online_users[sid], broadcast=True)

# ======================
# UPDATE LOKASI
# ======================
@socketio.on('update_location')
def update_location(data):
    sid = request.sid

    if sid in online_users:
        online_users[sid]["lat"] = data["lat"]
        online_users[sid]["lng"] = data["lng"]

    emit('update_users', online_users, broadcast=True)

# ======================
# DISCONNECT
# ======================
@socketio.on('disconnect')
def disconnect():
    sid = request.sid

    if sid in online_users:
        del online_users[sid]
        emit('remove_user', sid, broadcast=True)

# ======================
# RUN
# ======================
if __name__ == "__main__":
    socketio.run(app, debug=True)