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
    def __init__(self, hint: str, count: int):
        self.hint = hint
        self.count = count
        self.max_guesses = count + 1
        self.guesses: int = 0
        self.votes: dict[int: set[str]] = {}


@dataclass
class Matchmaking:
    def __str__(self):
        return 'matchmaking'


@dataclass
class SpymasterTurn:
    team: Team

    def __str__(self):
        return f'{self.team}_spymaster'


@dataclass
class AgentTurn:
    team: Team
    actions: AgentActions

    def __str__(self):
        return f'{self.team}_agents'


@dataclass
class Win:
    team: Team

    def __str__(self):
        return f'{self.team}_win'


PlayState = Matchmaking | SpymasterTurn | AgentTurn | Win


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
class History:
    player_name: str
    player_team: Team
    description: str
    action: str
    action_team: Team


class GameSetupError(Exception):
    pass


class TurnError(Exception):
    pass


class ActionError(Exception):
    pass


@dataclass
class Game:
    def __init__(self, game_id: int, collection: str = 'test'):
        self.game_id = game_id
        self.card_collection = collection

        self.client_to_name: dict[str: str] = {}
        self.host: str = None

        self.play_state: PlayState = Matchmaking()
        self.teams: dict[Team: TeamData] = {
            Team.BLUE: TeamData(),
            Team.RED: TeamData()
        }
        self.cards: list[Card] = []
        self.history: list[History] = []

    def num_players(self) -> int:
        return len(self.client_to_name)

    def has_player(self, client: str) -> bool:
        return client in self.client_to_name

    def player_team(self, client: str) -> Team:
        if client in self.teams[Team.BLUE].members:
            return Team.BLUE
        elif  client in self.teams[Team.RED].members:
            return Team.RED
        else:
            raise GameSetupError('Player not in game')

    def is_spymaster(self, client: str) -> bool:
        if client == self.teams[Team.BLUE].spymaster:
            return True
        elif client == self.teams[Team.RED].spymaster:
            return True
        else:
            return False

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
        if as_spymaster and join_team.spymaster is None:
            join_team.spymaster = client

    def leave_teams(self, client: str):
        def leave(team: TeamData):
            team.members.discard(client)
            if team.spymaster == client:
                team.spymaster = None

        leave(self.teams[Team.BLUE])
        leave(self.teams[Team.RED])

    def next_state(self, state: PlayState):
        self.play_state = state

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
            case Matchmaking() | Win():
                self.cards = cards
                self.next_state(SpymasterTurn(first_team))
            case _:
                raise GameSetupError('Game in progress')

    def reset(self):
        self.cards = []
        self.next_state(MatchMaking())

    def give_hint(self, client: str, hint: str, count: int):
        match self.play_state:
            case SpymasterTurn(curr_team):
                if client != self.teams[curr_team].spymaster:
                    raise ActionError('Player is not spymaster of current team')

                player_name = self.client_to_name[client]
                player_team = curr_team
                description = 'gives clue'
                action = f'{hint} {count}'
                action_team = ''
                self.history.append(History(player_name, player_team, description, action, action_team))

                agent_actions = AgentActions(hint, count)
                self.next_state(AgentTurn(curr_team, agent_actions))
            case _:
                raise TurnError('Not a spymaster turn')

    def _checked_agent_action(with_card: bool):
        def decorator(func):
            def wrapper(self, client: str, card: int):
                match self.play_state:
                    case AgentTurn(curr_team, actions):
                        if with_card:
                            if card < 0 or card >= len(self.cards):
                                raise ActionError('Out-of-bounds card index')
                            if not self.cards[card].hidden:
                                raise ActionError('Card already revealed')

                        player_team = self.player_team(client)
                        if player_team != curr_team:
                            raise TurnError('Player not in agent team')
                        if client == self.teams[player_team].spymaster:
                            raise ActionError('Spymaster cannot choose a card')

                        func(self, client, card, curr_team, actions)
                    case _:
                        raise TurnError('Not an agent turn')
            return wrapper
        return decorator

    @_checked_agent_action(True)
    def vote(self, client: str, card: int, curr_team: Team, actions: AgentActions):
        """Marks a card as a possible agent for other players

        Example:
        game.vote(client, card)
        """
        if card not in actions.votes:
            actions.votes[card] = set({client})
        elif client not in actions.votes[card]:
            actions.votes[card].add(client)
        else:
            actions.votes[card].remove(client)

    @_checked_agent_action(True)
    def reveal_card(self, client: str, card_index: int, curr_team: Team, actions: AgentActions):
        """Make a guess by revealing a card

        Example:
        game.reveal_card(client, card)
        """
        other_team = switch_team(curr_team)

        player_name = self.client_to_name[client]
        player_team = curr_team
        description = 'picked card'
        action = f'{card_index}'
        action_team = card.team
        self.history.append(History(player_name, player_team, description, action, action_team))

        card = self.cards[card_index]
        card.hidden = False

        match card.team:
            case Team.ASSASSIN:
                self.next_state(Win(other_team))
            case Team.INNOCENT:
                self.next_state(SpymasterTurn(other_team))
            case _ if card.team == other_team:
                self.next_state(SpymasterTurn(other_team))
            case _:
                if card_index in actions.votes:
                    del actions.votes[card_index]

                actions.guesses += 1
                if actions.guesses > actions.max_guesses:
                    self.next_state(SpymasterTurn(other_team))

    @_checked_agent_action(False)
    def end_guessing(self, client: str, card: int, curr_team: Team, actions: AgentActions):
        player_name = self.client_to_name[client]
        player_team = curr_team
        description = 'ends guessing'
        action = ''
        action_team = ''
        self.history.append(History(player_name, player_team, description, action, action_team))

        other_team = switch_team(curr_team)
        self.next_state(SpymasterTurn(other_team));


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


def random_first_team() -> Team:
    return Team.BLUE if random.randint(0, 1) == 0 else Team.RED
