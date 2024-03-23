from game import (
    AgentActions,
    AgentTurn,
    Card,
    Game,
    PlayState,
    SpymasterTurn,
    Team,
    TeamData,
    Win,

    ActionError,
    GameSetupError,
    TurnError,

    draw_cards
)

import copy
import unittest

class TestGame(unittest.TestCase):
    def setUp(self):
        self.game = Game(0)
        self.first_team = Team.BLUE
        self.cards = generate_test_cards(self.first_team)

    def test_init(self):
        self.assertEqual(self.game.num_players(), 0)

    def test_join_leave_game(self):
        self.game.join_game('foo', 'bar')
        self.assertEqual(self.game.num_players(), 1)
        self.assertTrue(self.game.has_player('foo'))
        self.assertFalse(self.game.has_player('bar'))

        self.game.leave_game('bar')
        self.assertEqual(self.game.num_players(), 1)

        self.game.leave_game('foo')
        self.assertEqual(self.game.num_players(), 0)
        self.assertFalse(self.game.has_player('foo'))

    def test_join_leave_team(self):
        self.game.join_game('foo', 'bar')

        self.game.join_team('foo', 'red', False)
        self.assertEqual(self.game.teams[Team.BLUE].members, set())
        self.assertEqual(self.game.teams[Team.BLUE].spymaster, None)
        self.assertEqual(self.game.teams[Team.RED].members, set({'foo'}))
        self.assertEqual(self.game.teams[Team.RED].spymaster, None)

        self.game.join_team('foo', 'red', True)
        self.assertEqual(self.game.teams[Team.BLUE].members, set())
        self.assertEqual(self.game.teams[Team.BLUE].spymaster, None)
        self.assertEqual(self.game.teams[Team.RED].members, set({'foo'}))
        self.assertEqual(self.game.teams[Team.RED].spymaster, 'foo')

        self.game.join_team('foo', 'blue', True)
        self.assertEqual(self.game.teams[Team.BLUE].members, set({'foo'}))
        self.assertEqual(self.game.teams[Team.BLUE].spymaster, 'foo')
        self.assertEqual(self.game.teams[Team.RED].members, set())
        self.assertEqual(self.game.teams[Team.RED].spymaster, None)

        self.game.join_team('foo', 'blue', False)
        self.assertEqual(self.game.teams[Team.BLUE].members, set({'foo'}))
        self.assertEqual(self.game.teams[Team.BLUE].spymaster, None)
        self.assertEqual(self.game.teams[Team.RED].members, set())
        self.assertEqual(self.game.teams[Team.RED].spymaster, None)

        self.game.leave_game('foo')
        self.assertEqual(self.game.teams[Team.BLUE].members, set())
        self.assertEqual(self.game.teams[Team.BLUE].spymaster, None)
        self.assertEqual(self.game.teams[Team.RED].members, set())
        self.assertEqual(self.game.teams[Team.RED].spymaster, None)

        orig = copy.deepcopy(self.game)
        self.game.join_team('asdf', 'blue', False)
        self.assertEqual(self.game, orig)
        self.game.join_team('foo', 'innocent', False)
        self.assertEqual(self.game, orig)
        self.game.join_team('foo', 'assassin', False)
        self.assertEqual(self.game, orig)
        self.game.join_team('foo', 'what', False)
        self.assertEqual(self.game, orig)

    def test_start_game(self):
        self.game.join_game('b', 'b')
        self.game.join_game('a', 'a')
        self.game.join_game('c', 'c')
        self.game.join_game('d', 'd')

        self.game.join_team('a', 'blue', True)
        self.game.join_team('b', 'red', False)
        self.game.join_team('c', 'red', True)
        with self.assertRaises(GameSetupError):
            self.game.start_game(self.first_team, self.cards)

        self.game.join_team('a', 'blue', False)
        with self.assertRaises(GameSetupError):
            self.game.start_game(self.first_team, self.cards)

        self.game.join_team('d', 'blue', False)
        with self.assertRaises(GameSetupError):
            self.game.start_game(self.first_team, self.cards)

        self.game.join_team('a', 'blue', True)
        self.game.start_game(self.first_team, self.cards)
        self.assertEqual(self.game.play_state, SpymasterTurn(self.first_team))

    def test_give_hint(self):
        self.add_members()
        # Not a spymaster turn
        with self.assertRaises(TurnError):
            self.game.give_hint('a', 'hint', 1)

        self.game.start_game(self.first_team, self.cards)
        # Not current spymaster
        with self.assertRaises(ActionError):
            self.game.give_hint('b', 'hint', 1)
        with self.assertRaises(ActionError):
            self.game.give_hint('c', 'hint', 1)

        self.game.give_hint('a', 'hint', 1)
        self.assertEqual(self.game.play_state.actions.hint, 'hint')
        self.assertEqual(self.game.play_state.actions.max_guesses, 2)

    def test_vote(self):
        self.add_members()
        self.game.join_game('z', 'Blade')
        self.game.join_team('z', 'blue', False)

        # Not a voting turn
        with self.assertRaises(TurnError):
            self.game.vote('b', 0)

        self.cards[1].hidden = False
        self.game.start_game(self.first_team, self.cards)
        # Not a voting turn
        with self.assertRaises(TurnError):
            self.game.vote('b', 0)

        self.game.give_hint('a', 'hint', 1)
        # Bad card indices
        with self.assertRaises(ActionError):
            self.game.vote('b', -1)
        with self.assertRaises(ActionError):
            self.game.vote('b', 20)
        # Card already revealed
        with self.assertRaises(ActionError):
            self.game.vote('b', 1)
        # Player not in voting team
        with self.assertRaises(TurnError):
            self.game.vote('c', 0)
        # Spymaster cannot vote
        with self.assertRaises(ActionError):
            self.game.vote('a', 0)

        self.game.vote('b', 0)
        self.assertEqual(self.game.play_state.actions.votes, {0: {'b'}})
        self.game.vote('b', 0)
        self.assertEqual(self.game.play_state.actions.votes, {0: {'b'}})
        self.game.vote('b', 2)
        self.assertEqual(self.game.play_state.actions.votes, {0: {'b'}, 2: {'b'}})
        self.game.vote('z', 0)
        self.assertEqual(self.game.play_state.actions.votes, {0: {'b', 'z'}, 2: {'b'}})

    def test_reveal_card(self):
        self.add_members()
        # Not an agent turn
        with self.assertRaises(TurnError):
            self.game.reveal_card('b', 0)

        self.cards[1].hidden = False
        self.game.start_game(Team.BLUE, self.cards)
        # Not an agent turn
        with self.assertRaises(TurnError):
            self.game.reveal_card('b', 0)

        self.game.give_hint('a', 'hint', 0)
        # Bad card indices
        with self.assertRaises(ActionError):
            self.game.reveal_card('b', -1)
        with self.assertRaises(ActionError):
            self.game.reveal_card('b', 20)
        # Card already revealed
        with self.assertRaises(ActionError):
            self.game.reveal_card('b', 1)
        # Player not in voting team
        with self.assertRaises(TurnError):
            self.game.reveal_card('c', 0)
        # Spymaster cannot reveal_card
        with self.assertRaises(ActionError):
            self.game.reveal_card('a', 0)

        self.game.vote('b', 0)
        self.assertEqual(self.game.play_state.actions.votes, {0: {'b'}})
        self.game.reveal_card('b', 0)
        self.assertEqual(self.game.play_state.actions.votes, {})
        self.assertEqual(self.game.play_state.actions.guesses, 1)

        # Card already revealed
        with self.assertRaises(ActionError):
            self.game.reveal_card('b', 0)

        # Switch turns when out of guesses
        self.game.reveal_card('b', 2)
        self.assertEqual(self.game.play_state, SpymasterTurn(Team.RED))

        # Switch turns when selecting other team's card
        self.game.next_state(AgentTurn(Team.BLUE, AgentActions('hint', 0)))
        self.game.reveal_card('b', 8);
        self.assertEqual(self.game.play_state, SpymasterTurn(Team.RED))

        # Switch turns when selecting innocent card
        self.game.next_state(AgentTurn(Team.BLUE, AgentActions('hint', 0)))
        self.game.reveal_card('b', 15);
        self.assertEqual(self.game.play_state, SpymasterTurn(Team.RED))

        # Lose when selecting assassin card
        self.game.next_state(AgentTurn(Team.BLUE, AgentActions('hint', 0)))
        self.game.reveal_card('b', 19);
        self.assertEqual(self.game.play_state, Win(Team.RED))

    def add_members(self):
        self.game.join_game('a', 'Daniel')
        self.game.join_game('b', 'Kafka')
        self.game.join_game('c', 'Alan')
        self.game.join_game('d', 'Mario')

        self.game.join_team('a', 'blue', True)
        self.game.join_team('b', 'blue', False)
        self.game.join_team('c', 'red', True)
        self.game.join_team('d', 'red', False)


def generate_test_cards(first_team: Team) -> list[Card]:
    deck = [i for i in range(20)]
    draw = draw_cards(deck, first_team)

    cards = []
    for team, i in draw:
        cards.append(Card(team, str(i)))
    return cards


if __name__ == '__main__':
    unittest.main()
