"""
ai_solver.ExpectimaxAI 的单元测试
使用较小的搜索深度以保证测试运行迅速
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_solver import ExpectimaxAI  # noqa: E402
from game_logic import Game2048  # noqa: E402


class TestExpectimaxAI(unittest.TestCase):
    def test_get_best_move_returns_valid_direction(self):
        game = Game2048()
        ai = ExpectimaxAI(search_depth=2)
        move, score = ai.get_best_move(game)
        self.assertIn(move, game.get_available_moves())
        self.assertIsInstance(score, float)

    def test_get_best_move_returns_none_when_no_moves(self):
        game = Game2048()
        game.board = [
            [2, 4, 2, 4],
            [4, 2, 4, 2],
            [2, 4, 2, 4],
            [4, 2, 4, 2],
        ]
        ai = ExpectimaxAI(search_depth=2)
        move, score = ai.get_best_move(game)
        self.assertIsNone(move)
        self.assertEqual(score, 0)

    def test_evaluate_prefers_more_empty_cells(self):
        ai = ExpectimaxAI(search_depth=1)

        emptier = Game2048()
        emptier.board = [[0] * 4 for _ in range(4)]
        emptier.board[0][0] = 2

        fuller = Game2048()
        fuller.board = [[2] * 4 for _ in range(4)]
        fuller.board[0][0] = 0

        self.assertGreater(ai._evaluate(emptier), ai._evaluate(fuller))

    def test_get_stats_reports_last_run(self):
        game = Game2048()
        ai = ExpectimaxAI(search_depth=2)
        ai.get_best_move(game)
        stats = ai.get_stats()
        self.assertEqual(stats['search_depth'], 2)
        self.assertGreater(stats['nodes_explored'], 0)
        self.assertGreaterEqual(stats['decision_time'], 0)

    def test_load_weights_missing_file_keeps_defaults(self):
        ai = ExpectimaxAI(search_depth=2)
        default_weights = ai.weights.copy()
        ai.load_weights('does_not_exist.json')
        self.assertEqual(ai.weights, default_weights)


if __name__ == '__main__':
    unittest.main()
