"""
game_logic.Game2048 的单元测试
覆盖移动/合并、克隆隔离性、游戏结束判定等核心行为
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game_logic import Game2048  # noqa: E402


class TestBoardSetup(unittest.TestCase):
    def test_init_creates_two_tiles(self):
        game = Game2048()
        non_zero = sum(1 for row in game.board for cell in row if cell != 0)
        self.assertEqual(non_zero, 2)
        self.assertEqual(game.score, 0)

    def test_custom_size(self):
        game = Game2048(size=3)
        self.assertEqual(len(game.board), 3)
        self.assertEqual(len(game.board[0]), 3)


class TestMerging(unittest.TestCase):
    def _empty_game(self, size=4):
        game = Game2048(size=size)
        game.board = [[0] * size for _ in range(size)]
        game.score = 0
        return game

    def test_merge_left_combines_equal_adjacent_tiles(self):
        game = self._empty_game()
        game.board[0] = [2, 2, 4, 4]
        moved = game.move('left')
        self.assertTrue(moved)
        self.assertEqual(game.board[0], [4, 8, 0, 0])
        self.assertEqual(game.score, 12)

    def test_merge_only_combines_once_per_move(self):
        game = self._empty_game()
        game.board[0] = [2, 2, 2, 2]
        game.move('left')
        self.assertEqual(game.board[0], [4, 4, 0, 0])

    def test_move_right_slides_without_illegal_merge(self):
        game = self._empty_game()
        game.board[0] = [2, 0, 0, 4]
        game.move('right')
        self.assertEqual(game.board[0], [0, 0, 2, 4])

    def test_no_op_move_returns_false_and_keeps_score(self):
        game = self._empty_game()
        game.board[0] = [2, 4, 8, 16]
        original_score = game.score
        moved = game.move('left')
        self.assertFalse(moved)
        self.assertEqual(game.score, original_score)

    def test_up_and_down_merge_columns(self):
        game = self._empty_game()
        for i in range(4):
            game.board[i][0] = 2
        game.move('up')
        self.assertEqual([game.board[i][0] for i in range(4)], [4, 4, 0, 0])


class TestClone(unittest.TestCase):
    def test_clone_is_independent_of_original(self):
        game = Game2048()
        clone = game.clone()
        clone.board[0][0] = 999
        clone.score = 12345
        self.assertNotEqual(game.board[0][0], 999)
        self.assertNotEqual(game.score, 12345)

    def test_clone_preserves_state(self):
        game = Game2048()
        game.score = 42
        clone = game.clone()
        self.assertEqual(clone.board, game.board)
        self.assertEqual(clone.score, 42)
        self.assertEqual(clone.size, game.size)


class TestGameOver(unittest.TestCase):
    def test_game_over_when_full_and_no_merges(self):
        game = Game2048()
        game.board = [
            [2, 4, 2, 4],
            [4, 2, 4, 2],
            [2, 4, 2, 4],
            [4, 2, 4, 2],
        ]
        self.assertTrue(game.is_game_over())

    def test_not_game_over_with_empty_cell(self):
        game = Game2048()
        game.board = [
            [2, 4, 2, 4],
            [4, 2, 4, 2],
            [2, 4, 2, 4],
            [4, 2, 4, 0],
        ]
        self.assertFalse(game.is_game_over())

    def test_not_game_over_with_adjacent_merge_available(self):
        game = Game2048()
        game.board = [
            [2, 2, 4, 2],
            [4, 8, 2, 4],
            [2, 4, 8, 2],
            [4, 2, 4, 8],
        ]
        self.assertFalse(game.is_game_over())

    def test_get_available_moves_excludes_no_op_directions(self):
        game = Game2048()
        game.board = [
            [2, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
        ]
        moves = game.get_available_moves()
        self.assertIn('down', moves)
        self.assertIn('right', moves)
        self.assertNotIn('up', moves)
        self.assertNotIn('left', moves)

    def test_get_max_tile(self):
        game = Game2048()
        game.board[0][0] = 128
        self.assertEqual(game.get_max_tile(), 128)


if __name__ == '__main__':
    unittest.main()
