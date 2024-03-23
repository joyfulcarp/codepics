from dataclasses import dataclass
from enum import Enum

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

    def num_players(self):
        return len(self.client_to_name)

    def has_player(self, client: str):
        return client in self.client_to_name

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

def shuffle_deck(deck_size: int, first_team: Team) -> list[(Team, int)]:
    """Shuffle and draw 20 cards from deck
    Pick 20 cards and assign:
    * 8 for first team
    * 7 for second team
    * 4 innocent bystanders
    * 1 assassin
    """
    deck = [i for i in range(deck_size)]
    drawn_cards = random.sample(deck, 20)

    assigned_cards: list[(Team, int)] = []
    for i in range(0, 8):
        assigned_cards.append((first_team, drawn_cards[i]))
    second_team = Team.BLUE if first_team == Team.RED else Team.RED
    for i in range(8, 15):
        assigned_cards.append((second_team, drawn_cards[i]))
    for i in range(15, 20):
        assigned_cards.append((Team.INNOCENT, drawn_cards[i]))
    assigned_cards.append((Team.ASSASSIN, drawn_cards[19]))

    # Shuffle order for display
    random.shuffle(assigned_cards)
    return assigned_cards


def generate_cards(first_team: Team, images: list[str]) -> list[Card]:
    shuffle = shuffle_deck(len(images), first_team)
    cards = []
    for team, i in shuffle:
        cards.append(Card(team, images[i]))
    return cards
