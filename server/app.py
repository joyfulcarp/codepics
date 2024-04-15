import os

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO

from cafe import Cafe

app = Flask('codepics')
app.config.from_object(__name__)
app.config['CORS_HEADERS'] = 'Content-Type'

# Enable CORS
CORS(app)

# WebSockets for communication in games
socketio = SocketIO(app, cors_allowed_origins='*', logger=True)

cafe = Cafe(app.debug)

###########
# Routing #
###########

@app.route('/ping', methods=['GET'])
def ping_pong():
    return jsonify('pong!')


@app.route('/games', methods=['GET'])
def games():
    return jsonify(cafe.list_games())


@app.route('/card_collections', methods=['GET'])
def card_collections():
    return jsonify(cafe.list_card_collections())


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


@socketio.on('switch_collection')
def on_switch_collection(data):
    cafe.on_switch_collection(request.sid, data)


@socketio.on('start_game')
def on_start_game(data):
    cafe.on_start_game(request.sid, data)


@socketio.on('reset_game')
def on_reset_game(data):
    cafe.on_reset_game(request.sid, data)


@socketio.on('randomize_teams')
def on_randomize_teams(data):
    cafe.on_randomize_teams(request.sid, data)


@socketio.on('give_hint')
def on_give_hint(data):
    cafe.on_give_hint(request.sid, data)


@socketio.on('vote')
def on_vote(data):
    cafe.on_vote(request.sid, data)


@socketio.on('reveal_card')
def on_reveal_card(data):
    cafe.on_reveal_card(request.sid, data)


@socketio.on('end_guessing')
def on_end_guessing(data):
    cafe.on_end_guessing(request.sid, data)


@socketio.on('debug_fill_game')
def on_debug_fill_game(data):
    if app.debug:
        cafe.debug_fill_game(request.sid, data)


@socketio.on('debug_leave_all')
def on_debug_leave_all(data):
    if app.debug:
        cafe.debug_leave_all()


@socketio.on('debug_give_hint')
def on_debug_give_hint(data):
    if app.debug:
        cafe.debug_give_hint(request.sid, data)


@socketio.on('debug_vote')
def on_debug_vote(data):
    if app.debug:
        cafe.debug_vote(request.sid, data)


@socketio.on('debug_reveal_card')
def on_debug_reveal_card(data):
    if app.debug:
        cafe.debug_reveal_card(request.sid, data)


@socketio.on('debug_end_guessing')
def on_debug_end_guessing(data):
    if app.debug:
        cafe.debug_end_guessing(request.sid, data)


def main():
    socketio.run()


if __name__ == '__main__':
    main()
