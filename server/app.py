from flask import Flask, jsonify
from flask_cors import CORS

from game import GameList

app = Flask(__name__)
app.config.from_object(__name__)

# Enable CORS
CORS(app, resources={r'/*': {'origins': '*'}})

game_list = GameList()

# Sanity check
@app.route('/ping', methods=['GET'])
def ping_pong():
    return jsonify('pong!')

@app.route('/games', methods=['GET'])
def games():
    return game_list.games_to_dict()

@app.route('/create_game', methods=['POST'])
def create_game():
    return jsonify({'game_id': game_list.create_game()})

if __name__ == '__main__':
    app.run()
