from flask_socketio import (
    emit,
    join_room
)

from enum import Enum

import logging
import random

log = logging.getLogger('codepics')

class Team(str, Enum):
    BLUE = 'blue'
    RED = 'red'
    INNOCENT = 'innocent'
    ASSASSIN = 'assassin'


class LobbyState(str, Enum):
    WAITING = 'waiting'
    PLAYING = 'playing'


class PlayState(str, Enum):
    BLUE_SPYMASTER = 'blue_spymaster'
    BLUE_AGENTS = 'blue_agents'
    RED_SPYMASTER = 'red_spymaster'
    RED_AGENTS = 'red_agents'
    BLUE_WIN = 'blue_win'
    RED_WIN = 'red_win'


class TeamData:
    def __init__(self):
        self.team: set[str] = set()
        self.spymaster: str = None

    def __eq__(self, other):
        return (self.team, self.spymaster) == (other.team, other.spymaster)

    def ready(self):
        return self.spymaster is not None and len(self.team) >= 2


class Card:
    def __init__(self, team: Team, asset: str):
        self.team = team
        self.asset = asset
        self.hidden = True

    def __eq__(self, other):
        return (self.team, self.asset) == (other.team, other.asset)


class Game:
    def __init__(self, game_id: int):
        self.game_id = game_id
        self.client_to_name: dict[str: str] = {}
        self.host: str = None
        self.lobby_state = LobbyState.WAITING
        self.play_state: PlayState = None
        self.teams: dict[Team: TeamData] = {
            Team.BLUE: TeamData(),
            Team.RED: TeamData()
        }
        self.cards: list[Card] = None


    # For unit testing only
    def __eq__(self, other):
        return (
            self.game_id,
            self.client_to_name,
            self.host,
            self.lobby_state,
            self.play_state,
            self.teams,
            self.cards
        ) == (
            other.game_id,
            other.client_to_name,
            other.host,
            other.lobby_state,
            other.play_state,
            other.teams,
            other.cards
        )

    def num_players(self):
        return len(self.client_to_name)

    def has_player(self, client: str):
        return client in self.client_to_name

    def join_game(self, client: str, name: str):
        log.info(type(client))
        self.client_to_name[client] = name
        if self.host is None:
            self.host = client

    def leave_game(self, client: str):
        self.leave_teams(client)

        if client in self.client_to_name:
            del self.client_to_name[client]
        if client == self.host:
            if len(self.client_to_name) == 0:
                self.host = None
            else:
                self.host = next(iter(self.client_to_name))

    def update_name(self, client: str, name: str):
        self.client_to_name[client] = name

    def join_team(self, client: str, team: str, as_spymaster: bool):
        if client not in self.client_to_name:
            return

        if team == 'blue':
            join_team = self.teams[Team.BLUE]
            leave_team = self.teams[Team.RED]
        elif team == 'red':
            join_team = self.teams[Team.RED]
            leave_team = self.teams[Team.BLUE]
        else:
            return

        self.leave_teams(client)

        join_team.team.add(client)
        if as_spymaster:
            join_team.spymaster = client

    def leave_teams(self, client: str):
        def leave(team: TeamData):
            team.team.discard(client)
            if team.spymaster == client:
                team.spymaster = None

        leave(self.teams[Team.BLUE])
        leave(self.teams[Team.RED])

    def start_game(self) -> str:
        if not self.teams[Team.BLUE].ready() or not self.teams[Team.RED].ready():
            return 'Both teams need a spymaster and at least one agent.'

        self.lobby_state = LobbyState.PLAYING
        first_team = Team.BLUE if random.randint(0, 1) == 0 else Team.RED
        self.generate_cards(first_team)
        if first_team == Team.BLUE:
            self.play_state = PlayState.BLUE_SPYMASTER
        else:
            self.play_state = PlayState.RED_SPYMASTER
        return None

    def generate_cards(self, first_team: Team):
        # TODO: Replace with actual assets
        deck = [str(i) for i in range(0, 100)]

        # Pick 20 cards and assign:
        # * 8 for first team
        # * 7 for second team
        # * 4 innocent bystanders
        # * 1 assassin
        drawn_cards = random.sample(deck, 20)
        self.cards = []
        for i in range(0, 8):
            self.cards.append(Card(first_team, drawn_cards[i]))
        second_team = Team.BLUE if first_team == Team.RED else Team.RED
        for i in range(8, 15):
            self.cards.append(Card(second_team, drawn_cards[i]))
        for i in range(15, 20):
            self.cards.append(Card(Team.INNOCENT, drawn_cards[i]))
        self.cards.append(Card(Team.ASSASSIN, drawn_cards[19]))

        # Shuffle order for display
        random.shuffle(self.cards)

    def lobby_info(self):
        return {
            'game_id': self.game_id,
            'players': self.num_players(),
            'state': self.lobby_state
        }

    def team_info(self, team: Team):
        if team not in {Team.BLUE, Team.RED}:
            raise ValueError('Only blue/red teams can have players')
        data = self.teams[team]

        agents = [self.client_to_name[a] for a in data.team if a != data.spymaster]
        agents.sort()
        spymaster = self.client_to_name[data.spymaster] if data.spymaster else None

        return {
            'agents': agents,
            'spymaster': spymaster
        }

    def all_team_info(self):
        return {
            'blue': self.team_info(Team.BLUE),
            'red': self.team_info(Team.RED)
        }

    def game_info(self):
        return {
            'id': self.game_id,
            'lobby_state': self.lobby_state,
            'teams': self.all_team_info()
        }


class GameList:
    def __init__(self):
        self.games: dict[int: Game] = {}
        self.client_to_games: dict[str: list[int]] = {}
        self.id_counter = 0

    def games_to_dict(self):
        return {'games': [g.lobby_info() for g in self.games.values()]}

    def reserve_lobby(self):
        game_id = self.id_counter
        self.id_counter += 1
        return game_id

    def build_update_template(self, game: Game):
        return {'game': game.game_info()}

    def create_or_join_game(self, client: str, data):
        game_id = data['game_id']
        name = data['name']

        # Respect lobby reservation
        if game_id >= self.id_counter:
            return

        if game_id not in self.games:
            self.games[game_id] = Game(game_id)

        game = self.games[game_id]
        game.join_game(client, name)

        if client not in self.client_to_games:
            self.client_to_games[client] = set({game_id})
        else:
            self.client_to_games[client].add(game_id)

        join_room(game_id)

        response = self.build_update_template(game)
        emit('update_game', response)

    def on_user_disconnect(self, client: str):
        if client not in self.client_to_games:
            return

        for game_id in self.client_to_games[client]:
            game = self.games[game_id]
            game.leave_game(client)
            if game.num_players() == 0:
                del self.games[game_id]
        del self.client_to_games[client]

    def on_switch_team(self, client: str, data):
        game_id = data['game_id']
        team = data['team']
        as_spymaster = data.get('as_spymaster', False)

        game = self.games[game_id]
        game.join_team(client, team, as_spymaster)

        response = self.build_update_template(game)
        emit('update_teams', response)

    def on_start_game(self, data):
        game_id = data['game_id']
        game = self.games[game_id]
        err = game.start_game()
        if err:
            emit('error', {'msg': err})
        else:
            response = self.build_update_template(game_id)
            emit('update_game', response)
