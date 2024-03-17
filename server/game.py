from enum import Enum
from flask import jsonify

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
        self.players = 0
        self.max_players = 12
        self.lobby_state = LobbyState.WAITING
        self.play_state = None

    def lobby_info(self):
        return {
            'game_id': self.game_id,
            'players': self.players,
            'max_players': self.max_players,
            'state': self.lobby_state,
            'requires_password': False
        }


class GameList:
    def __init__(self):
        self.games = []
        self.id_counter = 0

    def games_to_dict(self):
        return jsonify({'games': [g.lobby_info() for g in self.games]})

    def create_game(self):
        game_id = self.id_counter
        self.id_counter += 1
        self.games.append(Game(game_id))
        return game_id
