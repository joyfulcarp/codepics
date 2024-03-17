from enum import Enum
from flask import jsonify

import logging

log = logging.getLogger('codepics')

class LobbyState(str, Enum):
    WAITING = "waiting"
    PLAYING = "playing"


class PlayState(str, Enum):
    BLUE_SPYMASTER = "blue_spymaster"
    BLUE_AGENTS = "blue_agents"
    RED_SPYMASTER = "red_spymaster"
    RED_AGENTS = "red_agents"
    BLUE_WIN = "blue_win"
    RED_WIN = "red_win"


class Game:
    def __init__(self, game_id):
        self.game_id = game_id
        self.client_to_name = {}
        self.lobby_state = LobbyState.WAITING
        self.play_state = None

    def num_players(self):
        return len(self.client_to_name)

    def lobby_info(self):
        return {
            'game_id': self.game_id,
            'players': self.num_players(),
            'state': self.lobby_state
        }

    def join_game(self, client, name):
        self.client_to_name[client] = name

    def leave_game(self, client):
        del self.client_to_name[client]


class GameList:
    def __init__(self):
        self.games = {}
        self.client_to_games = {}
        self.id_counter = 0

    def games_to_dict(self):
        return jsonify({'games': [g.lobby_info() for g in self.games.values()]})

    def reserve_lobby(self):
        game_id = self.id_counter
        self.id_counter += 1
        return game_id

    def create_or_join_game(self, game_id, name, client):
        if game_id >= self.id_counter:
            return False

        if game_id not in self.games:
            self.games[game_id] = Game(game_id)

        self.games[game_id].join_game(client, name)

        if client not in self.client_to_games:
            self.client_to_games[client] = set({game_id})

        self.client_to_games[client].add(game_id)

        return True

    def on_user_disconnect(self, client):
        if client not in self.client_to_games:
            return

        for game_id in self.client_to_games[client]:
            game = self.games[game_id]
            game.leave_game(client)
            if game.num_players() == 0:
                del self.games[game_id]
