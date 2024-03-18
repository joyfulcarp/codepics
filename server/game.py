from flask_socketio import (
    emit,
    join_room
)

from enum import Enum

import logging

log = logging.getLogger('codepics')

class Team(Enum):
    BLUE = 0
    RED = 1

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
        self.blue_team = set()
        self.red_team = set()

    def num_players(self):
        return len(self.client_to_name)

    def has_player(self, client):
        return client in self.client_to_name

    def players_in_team(self, team: Team):
        if team == Team.BLUE:
            players = self.blue_team
        else:
            players = self.red_team

        names = [self.client_to_name[c] for c in players]
        names.sort()
        return names

    def lobby_info(self):
        return {
            'game_id': self.game_id,
            'players': self.num_players(),
            'state': self.lobby_state
        }

    def team_info(self):
        return {
            'blue': {
                'members': self.players_in_team(Team.BLUE),
                'cards': '-'
            },
            'red': {
                'members': self.players_in_team(Team.RED),
                'cards': '-'
            }
        }

    def game_info(self):
        return {
            'teams': self.team_info()
        }

    def join_game(self, client, name):
        self.client_to_name[client] = name

    def leave_game(self, client):
        del self.client_to_name[client]

    def update_name(self, client, name):
        self.client_to_name[client] = name

    def join_team(self, client, team):
        if team == 'blue':
            self.red_team.discard(client)
            self.blue_team.add(client)
        elif team == 'red':
            self.blue_team.discard(client)
            self.red_team.add(client)


class GameList:
    def __init__(self):
        self.games = {}
        self.client_to_games = {}
        self.id_counter = 0

    def games_to_dict(self):
        return {'games': [g.lobby_info() for g in self.games.values()]}

    def reserve_lobby(self):
        game_id = self.id_counter
        self.id_counter += 1
        return game_id

    def create_or_join_game(self, client, data):
        game_id = data['game_id']
        name = data['name']

        # Respect lobby reservation
        if game_id >= self.id_counter:
            return

        if game_id not in self.games:
            self.games[game_id] = Game(game_id)

        self.games[game_id].join_game(client, name)

        if client not in self.client_to_games:
            self.client_to_games[client] = set({game_id})

        self.client_to_games[client].add(game_id)
        join_room(game_id)

    def on_user_disconnect(self, client):
        if client not in self.client_to_games:
            return

        for game_id in self.client_to_games[client]:
            game = self.games[game_id]
            game.leave_game(client)
            if game.num_players() == 0:
                del self.games[game_id]

    def on_switch_team(self, client, data):
        game_id = data['game_id']
        team = data['team']

        game = self.games[game_id]
        game.join_team(client, team)

        emit('update_teams', game.game_info(), to=game_id)
