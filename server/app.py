from flask import Flask, jsonify
from flask_cors import CORS
from flask_socketio import (
    SocketIO,
    join_room,
    leave_room,
    send
)

from game import GameList

frontend_url = 'http://localhost:5173'

app = Flask("codepics")
app.config.from_object(__name__)

# Enable CORS
CORS(app, resources={r'/*': {'origins': frontend_url}})

# WebSockets for communication in games
socketio = SocketIO(app, cors_allowed_origins=frontend_url, logger=True)

game_list = GameList()

###########
# Routing #
###########

@app.route('/ping', methods=['GET'])
def ping_pong():
    return jsonify('pong!')

@app.route('/games', methods=['GET'])
def games():
    return game_list.games_to_dict()

@app.route('/create_game', methods=['POST'])
def create_game():
    game_id = game_list.reserve_lobby()
    return jsonify({'game_id': game_id})

###################
# Socket handling #
###################

@socketio.on('connect')
def on_connect(auth):
    app.logger.info('Client connected')

@socketio.on('disconnect')
def on_disconnect():
    app.logger.info('Client disconnected')

@socketio.on('join')
def on_join(data):
    app.logger.info('Join game')
    # name = data['name']
    game_id = data['game_id']
    valid = game_list.create_or_join_game(game_id)
    if (valid):
        join_room('game_id')
        send({'valid_game_id': True})
    else:
        send({'valid_game_id': False})

@socketio.on('leave')
def on_leave(data):
    app.logger.info('Leave game')

if __name__ == '__main__':
    socketio.run()
