from flask import Flask, jsonify, request
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

@socketio.on('disconnect')
def on_disconnect():
    app.logger.info(f'Client {request.sid} disconnected')
    game_list.on_user_disconnect(request.sid)

@socketio.on('join')
def on_join(data):
    client = request.sid
    game_id = data['game_id']
    name = data['name']
    app.logger.info(f'Client {client} (aka: {name}) joining game {game_id}')

    valid = game_list.create_or_join_game(game_id, name, client)
    if valid:
        join_room('game_id')
    else:
        send({'valid_game_id': False})

@socketio.on('leave')
def on_leave(data):
    app.logger.info(f'Client {request.sid} left the game')
    game_list.on_user_disconnect(request.sid)

if __name__ == '__main__':
    socketio.run()
