from game import (
    Card,
    Game,
    Matchmaking,
    Team,
    TeamData,

    random_first_team,
    generate_cards,
)
from images import find_images

from flask_socketio import (emit, join_room, leave_room)

from typing import TypeAlias

import builtins

def lobby_info(game: Game):
    return {
        'game_id': game.game_id,
        'players': game.num_players(),
        'state': 'waiting' if game.play_state == Matchmaking() else 'playing'
    }


def team_info(data: TeamData, game: Game):
    agents = [game.client_to_name[a] for a in data.members]
    agents.sort()
    spymaster = game.client_to_name[data.spymaster] if data.spymaster else None
    return {
        'agents': agents,
        'spymaster': spymaster
    }


def all_team_info(game: Game):
    return {
        'blue': team_info(game.teams[Team.BLUE], game),
        'red': team_info(game.teams[Team.RED], game)
    }


def card_info(card: Card):
    return {
        'team': card.team,
        'asset': card.asset,
        'hidden': card.hidden
    }


def game_info(game: Game):
    return {
        'id': game.game_id,
        'play_state': str(game.play_state),
        'teams': all_team_info(game),
        'cards': [card_info(c) for c in game.cards]
    }


Schema: TypeAlias = dict[str: int | str | bool]


def check_schema(schema: Schema):
    def decorator(func):
        def wrapper(self, client: str, data):
            parsed = validate(schema, data)
            if parsed is None:
                return lambda *args: None
            else:
                return func(self, client, parsed)
        return wrapper
    return decorator


class Cafe:
    def __init__(self, debug = False):
        self.games: dict[int: Game] = {}
        self.client_to_games: dict[str: list[int]] = {}
        self.id_counter = 0
        self.images = find_images('./static/cards')

        if debug:
            self.id_counter += 1
            game = Game(0)
            game.join_game('test_client_0', 'fake_user_0')
            game.join_game('test_client_1', 'fake_user_1')
            game.join_game('test_client_2', 'fake_user_2')
            game.join_game('test_client_3', 'fake_user_3')
            game.join_team('test_client_0', 'blue', True)
            game.join_team('test_client_1', 'blue', False)
            game.join_team('test_client_2', 'red', True)
            game.join_team('test_client_3', 'red', False)
            self.games[0] = game

    def list_games(self):
        return {'games': [lobby_info(g) for g in self.games.values()]}

    def reserve_lobby(self):
        game_id = self.id_counter
        self.id_counter += 1
        return game_id

    def build_update_template(self, game: Game):
        return {'game': game_info(game)}

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

        join_room(room(game_id))

        response = self.build_update_template(game)
        emit('update_game', response, to=room(game_id))

    def on_user_disconnect(self, client: str):
        if client not in self.client_to_games:
            return

        for game_id in self.client_to_games[client]:
            game = self.games[game_id]
            game.leave_game(client)
            leave_room(room(game_id))

            response = self.build_update_template(game)
            emit('update_game', response, to=room(game_id))

            if game.num_players() == 0:
                del self.games[game_id]
        del self.client_to_games[client]

    @check_schema({'game_id': int, 'team': str, 'as_spymaster': bool})
    def on_switch_team(self, client: str, data):
        game_id = data['game_id']
        team = data['team']
        as_spymaster = data.get('as_spymaster', False)

        game = self.games[game_id]
        game.join_team(client, team, as_spymaster)

        response = self.build_update_template(game)
        emit('update_teams', response, to=room(game_id))

    @check_schema({'game_id': int, 'collection': str})
    def on_switch_collection(self, client: str, data):
        game_id = data['game_id']
        game = self.games[game_id]
        collection = data['collection']
        game.card_collection = collection

    @check_schema({'game_id': int})
    def on_start_game(self, client: str, data):
        game_id = data['game_id']
        game = self.games[game_id]

        images = self.images[game.card_collection]
        first_team = random_first_team()
        cards = generate_cards(first_team, images)

        game.start_game(first_team, cards)

        response = self.build_update_template(game)
        emit('new_turn', response, to=room(game_id))

    @check_schema({'game_id': int})
    def on_reset_game(self, client: str, data):
        game_id = data['game_id']
        game = self.games[game_id]

        game.reset()

        response = self.build_update_template(game)
        emit('update_game', response, to=room(game_id))

    @check_schema({'game_id': int, 'hint': str, 'count': int})
    def on_give_hint(self, client: str, data):
        game_id = data['game_id']
        game = self.games[game_id]

        game.give_hint(client, data['hint'], data['count'])

        response = self.build_update_template(game)
        emit('new_turn', response, to=room(game_id))

    @check_schema({'game_id': int, 'card': int})
    def on_vote(self, client: str, data):
        game_id = data['game_id']
        game = self.games[game_id]

        game.vote(client, data['card'])

        response = self.build_update_template(game)
        emit('update_vote', response, to=room(game_id))

    @check_schema({'game_id': int, 'card': int})
    def on_reveal_card(self, client: str, data):
        game_id = data['game_id']
        game = self.games[game_id]

        game.reveal_card(client, data['card'])

        response = self.build_update_template(game)
        emit('update_card', response, to=room(game_id))


def room(game_id: int):
    return f'game_{game_id}'


def validate(schema: Schema, data) -> Schema:
    parsed = {}
    errors = {}
    for key, expected_type in schema.items():
        if key not in data:
            errors[key] = 'Missing field'
            return

        val = data[key]
        match expected_type:
            case builtins.str:
                if val:
                    parsed[key] = data[key]
                else:
                    errors[key] = 'Empty string'
            case builtins.int:
                try:
                    parsed[key] = int(val)
                except ValueError:
                    errors[key] = 'Not an integer'
            case builtins.bool:
                if isinstance(val, bool):
                    parsed[key] = val
                else:
                    errors[key] = 'Not a boolean'
            case _:
                raise AssertionError('Unexpected type in schema')

    if len(errors) != 0:
        emit('schema_error', errors)
        return None
    else:
        return parsed
