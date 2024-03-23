from dataclasses import dataclass
from enum import Enum

import random

class Team(str, Enum):
    BLUE = 'blue'
    RED = 'red'
    INNOCENT = 'innocent'
    ASSASSIN = 'assassin'


@dataclass
class AgentActions:
    def __init__(self, hint: (str, int)):
        self.hint = hint
        self.guesses: int = 0
        self.votes: dict[str: int] = {}


@dataclass
class Prep:
    def __str__(self):
        return 'prep'


@dataclass
class SpymasterTurn:
    team: Team

    def __str__(self):
        return f'{team}_spymaster'


@dataclass
class AgentTurn:
    team: Team
    actions: AgentActions

    def __str__(self):
        return f'{team}_agents'


@dataclass
class Win:
    team: Team

    def __str__(self):
        return f'{team}_win'


PlayState = Prep | SpymasterTurn | AgentTurn | Win


@dataclass
class TeamData:
    def __init__(self):
        self.members: set[str] = set() # Includes spymaster
        self.spymaster: str = None
        self.cards_left: int = 0

    def ready(self):
        return self.spymaster is not None and len(self.members) >= 2


@dataclass
class Card:
    team: Team
    asset: str
    hidden: bool = True


class GameSetupError(Exception):
    pass


@dataclass
class Game:
    def __init__(self, game_id: int, collection: str = 'test'):
        self.game_id = game_id
        self.card_collection = collection

        self.client_to_name: dict[str: str] = {}
        self.host: str = None

        self.play_state: PlayState = Prep()
        self.teams: dict[Team: TeamData] = {
            Team.BLUE: TeamData(),
            Team.RED: TeamData()
        }
        self.cards: list[Card] = []

    def num_players(self) -> int:
        return len(self.client_to_name)

    def has_player(self, client: str) -> bool:
        return client in self.client_to_name

    def teams_ready(self) -> bool:
        return self.teams[Team.BLUE].ready() and self.teams[Team.RED].ready()

    def update_name(self, client: str, name: str):
        if client in self.client_to_name:
            self.client_to_name[client] = name

    def join_game(self, client: str, name: str):
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

        join_team.members.add(client)
        if as_spymaster:
            join_team.spymaster = client

    def leave_teams(self, client: str):
        def leave(team: TeamData):
            team.members.discard(client)
            if team.spymaster == client:
                team.spymaster = None

        leave(self.teams[Team.BLUE])
        leave(self.teams[Team.RED])

    def start_game(self, first_team: Team, cards: list[Card]):
        assert len(cards) == 20
        assert first_team in [Team.BLUE, Team.RED]

        def count(team: Team) -> int:
            return sum(1 for c in cards if c.team == team)

        assert count(first_team) == 8
        assert count(switch_team(first_team)) == 7
        assert count(Team.INNOCENT) == 4
        assert count(Team.ASSASSIN) == 1

        if not self.teams_ready():
            raise GameSetupError('Both teams need a spymaster and at least one agent')

        match self.play_state:
            case Prep() | Win():
                self.cards = cards
                self.play_state = SpymasterTurn(first_team)
            case _:
                raise GameSetupError('Game in progress')


def switch_team(team: Team) -> Team:
    match team:
        case Team.BLUE:
            return Team.RED
        case Team.RED:
            return Team.BLUE
        case _:
            raise AssertionError('Player teams can only be blue or red')


def draw_cards(deck: list[int], first_team: Team) -> list[(Team, int)]:
    """Shuffle and draw 20 cards from deck
    Pick 20 cards and assign:
    * 8 for first team
    * 7 for second team
    * 4 innocent bystanders
    * 1 assassin
    """
    assert len(deck) >= 20
    second_team = switch_team(first_team)

    drawn_cards = random.sample(deck, 20)

    assigned_cards: list[(Team, int)] = []
    for i in range(0, 8):
        assigned_cards.append((first_team, drawn_cards[i]))
    for i in range(8, 15):
        assigned_cards.append((second_team, drawn_cards[i]))
    for i in range(15, 19):
        assigned_cards.append((Team.INNOCENT, drawn_cards[i]))
    assigned_cards.append((Team.ASSASSIN, drawn_cards[19]))

    return assigned_cards


def generate_cards(first_team: Team, images: list[str]) -> list[Card]:
    deck = [i for i in range(len(images))]
    draw = draw_cards(deck, first_team)
    # Shuffle order for display
    random.shuffle(draw)

    cards = []
    for team, i in draw:
        cards.append(Card(team, images[i]))
    return cards
