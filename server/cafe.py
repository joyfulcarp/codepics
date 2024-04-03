from game import (
    AgentTurn,
    Card,
    Game,
    Matchmaking,
    SpymasterTurn,
    Team,
    TeamData,

    random_first_team,
    generate_cards,
)
from images import find_images

from flask_socketio import (emit, join_room, leave_room, close_room)

from typing import TypeAlias

import builtins

def lobby_info(game: Game):
    return {
        'game_id': game.game_id,
        'players': game.num_players(),
        'state': 'waiting' if game.play_state == Matchmaking() else 'playing'
    }


def player_info(player: str, game: Game, client: str):
    return {
        'name': game.client_to_name[player],
        'is_self': player == client
    }


def team_info(data: TeamData, game: Game, client: str):
    agents = [player_info(a, game, client) for a in data.members if a != data.spymaster]
    spymaster = player_info(data.spymaster, game, client) if data.spymaster else None
    return {
        'agents': agents,
        'spymaster': spymaster
    }


def all_team_info(game: Game, client: str):
    return {
        'blue': team_info(game.teams[Team.BLUE], game, client),
        'red': team_info(game.teams[Team.RED], game, client)
    }


def card_info(card: Card, hide: bool):
    return {
        'team': None if hide and card.hidden else card.team,
        'asset': card.asset,
        'hidden': card.hidden
    }


def spymaster_card_info(game: Game):
    return {
        'cards': [card_info(c, False) for c in game.cards]
    }


def game_info(game: Game, client: str):
    return {
        'id': game.game_id,
        'play_state': str(game.play_state),
        'teams': all_team_info(game, client),
        'cards': [card_info(c, True) for c in game.cards]
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
    def __init__(self, debug: bool):
        self.games: dict[int: Game] = {}
        self.client_to_games: dict[str: list[int]] = {}
        self.id_counter = 0
        self.images = find_images('./static/cards')
        self.debug = debug
        self.debug_clients = {}
        self.debug_game_info = {}

        if debug:
            self.id_counter += 1
            self.debug_clients = {
                'test0': 'Kafka',
                'test1': 'Blade',
                'test2': 'David',
                'test3': 'Smith'
            }

    def list_games(self):
        return {'games': [lobby_info(g) for g in self.games.values()]}

    def list_card_collections(self):
        names = [c for c in self.images.keys()]
        names.sort()
        return {'collections': names }

    def reserve_lobby(self):
        game_id = self.id_counter
        self.id_counter += 1
        return game_id

    @check_schema({'game_id': int, 'name': str})
    def create_or_join_game(self, client: str, data):
        game_id = data['game_id']
        name = data['name']

        # Respect lobby reservation
        if game_id >= self.id_counter:
            return

        if game_id not in self.games:
            game = Game(game_id)
            self.games[game_id] = game

        game = self.games[game_id]
        game.join_game(client, name)

        if client not in self.client_to_games:
            self.client_to_games[client] = set({game_id})
        else:
            self.client_to_games[client].add(game_id)

        if client not in self.debug_clients:
            join_room(room(game_id))

        self.send_update(game, 'update_game', {})
        broadcast_host(game)

    def on_user_disconnect(self, client: str):
        if client not in self.client_to_games:
            return

        for game_id in self.client_to_games[client]:
            game = self.games[game_id]
            game.leave_game(client)

            if client not in self.debug_clients:
                leave_room(room(game_id))

            self.send_update(game, 'update_game', {})

            if game.num_players() == 0:
                del self.games[game_id]
                close_room(room(game_id))
        del self.client_to_games[client]

    @check_schema({'game_id': int, 'team': str, 'as_spymaster': bool})
    def on_switch_team(self, client: str, data):
        game_id = data['game_id']
        team = data['team']
        as_spymaster = data.get('as_spymaster', False)

        game = self.games[game_id]
        game.join_team(client, team, as_spymaster)

        self.send_update(game, 'update_teams', {});

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

        try:
            game.start_game(first_team, cards)

            self.send_update(game, 'update_game', {})
        except GameSetupError as e:
            emit('error', str(e))

    @check_schema({'game_id': int})
    def on_reset_game(self, client: str, data):
        game_id = data['game_id']
        game = self.games[game_id]

        game.reset()

        self.send_update(game, 'update_game', {})

    @check_schema({'game_id': int, 'hint': str, 'count': int})
    def on_give_hint(self, client: str, data):
        game_id = data['game_id']
        game = self.games[game_id]

        try:
            game.give_hint(client, data['hint'], data['count'])

            self.send_update(game, 'new_turn', {})
        except (ActionError, TurnError) as e:
            emit('error', str(e))

    @check_schema({'game_id': int, 'card': int})
    def on_vote(self, client: str, data):
        game_id = data['game_id']
        game = self.games[game_id]

        try:
            game.vote(client, data['card'])


            self.send_update(game, 'update_vote', {})
        except (ActionError, TurnError) as e:
            emit('error', str(e))

    @check_schema({'game_id': int, 'card': int})
    def on_reveal_card(self, client: str, data):
        game_id = data['game_id']
        game = self.games[game_id]

        try:
            game.reveal_card(client, data['card'])

            self.send_update(game, 'update_card', {
                'chosen_card': data['card']
            })
        except (ActionError, TurnError) as e:
            emit('error', str(e))

    def send_update(self, game: Game, event: str, payload: dict):
        for client in game.client_to_name:
            response = {'game': game_info(game, client) }
            if game.is_spymaster(client):
                response['spymaster_vision'] = spymaster_card_info(game)
            response = payload | response
            emit(event, response, to=client)

    @check_schema({'game_id': int})
    def debug_fill_game(self, _, data):
        gid = data['game_id']
        game = self.games[gid]

        if gid in self.debug_game_info:
            return

        self.debug_game_info[gid] = {}
        debug_info = self.debug_game_info[gid]
        cmds = [
            ('blue', game.teams[Team.BLUE].spymaster is None),
            ('blue', False),
            ('red', game.teams[Team.RED].spymaster is None),
            ('red', False)
        ]

        for i, (client, name) in enumerate(self.debug_clients.items()):
            self.create_or_join_game(client, {'game_id': gid, 'name': name})

            team, spymaster = cmds[i]
            self.on_switch_team(client, {'game_id': gid, 'team': team, 'as_spymaster': spymaster})

            if spymaster:
                debug_info[f'{team}_spymaster'] = client
            else:
                role = f'{team}_agents'
                if team in debug_info:
                    debug_info[role].add(client)
                else:
                    debug_info[role] = set({client})

    def debug_leave_all(self):
        for client, name in self.debug_clients.items():
            self.on_user_disconnect(client)
        self.debug_game_info = {}

    @check_schema({'game_id': int, 'hint': str, 'count': int})
    def debug_give_hint(self, _, data):
        gid = data['game_id']
        if gid not in self.debug_game_info:
            return

        client = self._debug_client(gid)
        self.on_give_hint(client, data)

    @check_schema({'game_id': int, 'card': int})
    def debug_vote(self, _, data):
        gid = data['game_id']
        if gid not in self.debug_game_info:
            return

        client = self._debug_client(gid)
        self.on_vote(client, data)

    @check_schema({'game_id': int, 'card': int})
    def debug_reveal_card(self, _, data):
        gid = data['game_id']
        if gid not in self.debug_game_info:
            return

        client = self._debug_client(gid)
        self.on_reveal_card(client, data)

    def _debug_client(self, gid: int) -> str:
        state = self.games[gid].play_state
        role = ''
        match state:
            case SpymasterTurn():
                role = str(state)
                return self.debug_game_info[gid][role]
            case AgentTurn():
                role = str(state)
                return next(iter(self.debug_game_info[gid][role]))
            case _:
                return None


def room(game_id: int):
    return f'game_{game_id}'


def broadcast_host(game: Game):
    for client in game.client_to_name.keys():
        emit('who_is_host', {'is_host': game.host == client}, to=client)


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
