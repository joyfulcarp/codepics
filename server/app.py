from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO

from game import GameList

frontend_url = 'http://localhost:5173'

app = Flask('codepics')
app.config.from_object(__name__)

# Enable CORS
CORS(app, resources={r'/*': {'origins': frontend_url}})

# WebSockets for communication in games
socketio = SocketIO(app, cors_allowed_origins=frontend_url, logger=True)

cafe = GameList()

###########
# Routing #
###########

@app.route('/ping', methods=['GET'])
def ping_pong():
    return jsonify('pong!')

@app.route('/games', methods=['GET'])
def games():
    return jsonify(cafe.games_to_dict())

@app.route('/create_game', methods=['POST'])
def create_game():
    game_id = cafe.reserve_lobby()
    return jsonify({'game_id': game_id})

###################
# Socket handling #
###################

@socketio.on('disconnect')
def on_disconnect():
    cafe.on_user_disconnect(request.sid)

@socketio.on('join')
def on_join(data):
    cafe.create_or_join_game(request.sid, data)

@socketio.on('leave')
def on_leave(data):
    cafe.on_user_disconnect(request.sid)

@socketio.on('switch_team')
def on_switch_team(data):
    cafe.on_switch_team(request.sid, data)

def main():
    socketio.run(debug=True)

if __name__ == '__main__':
    main()
