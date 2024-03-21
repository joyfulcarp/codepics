from game import (
    Game,
    Team,
    TeamData,
    LobbyState,
    PlayState
)

import copy
import unittest

class TestGame(unittest.TestCase):
    def setUp(self):
        self.game = Game(0)

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

    def test_join_team(self):
        self.game.join_game('foo', 'bar')

        self.game.join_team('foo', 'red', False)
        self.assertEqual(self.game.teams[Team.BLUE].team, set())
        self.assertEqual(self.game.teams[Team.BLUE].spymaster, None)
        self.assertEqual(self.game.teams[Team.RED].team, set({'foo'}))
        self.assertEqual(self.game.teams[Team.RED].spymaster, None)

        self.game.join_team('foo', 'red', True)
        self.assertEqual(self.game.teams[Team.BLUE].team, set())
        self.assertEqual(self.game.teams[Team.BLUE].spymaster, None)
        self.assertEqual(self.game.teams[Team.RED].team, set({'foo'}))
        self.assertEqual(self.game.teams[Team.RED].spymaster, 'foo')

        self.game.join_team('foo', 'blue', False)
        self.assertEqual(self.game.teams[Team.BLUE].team, set({'foo'}))
        self.assertEqual(self.game.teams[Team.BLUE].spymaster, None)
        self.assertEqual(self.game.teams[Team.RED].team, set())
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


if __name__ == '__main__':
    unittest.main()