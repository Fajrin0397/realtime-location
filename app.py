
from flask_socketio import SocketIO, emit
#from flask_cors import CORS
from flask import Flask, render_template, request

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
#CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

clickMarkers = {}
idLinks = {}

@socketio.on('connect')
def client_connect():
    emit('on_connect', 'connected')
    emit('update_marker', clickMarkers)

@socketio.on('on_click')
def on_click(sendlist):
    clickMarkers[sendlist[0]] = sendlist[1]
    idLinks[request.sid]=sendlist[0]
    emit('update_marker', clickMarkers, broadcast=True)

@socketio.on('disconnect')
def client_disconnect():
    if request.sid in idLinks:
        print('marker remove')
        del clickMarkers[idLinks[request.sid]]
        emit('remove_marker', idLinks[request.sid], broadcast=True)

if __name__ == "__main__":
    print('server has run')
    socketio.run(app,debug=True,)