"""
2048游戏核心逻辑
实现棋盘状态管理、移动、合并等基本操作
"""
import random
import copy
from typing import List, Tuple


class Game2048:
    """2048游戏核心类"""
    
    def __init__(self, size: int = 4):
        """
        初始化游戏
        :param size: 棋盘大小，默认4x4
        """
        self.size = size
        self.board = [[0] * size for _ in range(size)]
        self.score = 0
        self.moved = False
        self.init_game()
    
    def init_game(self):
        """初始化游戏，添加两个初始方块"""
        self.board = [[0] * self.size for _ in range(self.size)]
        self.score = 0
        self.add_random_tile()
        self.add_random_tile()
    
    def add_random_tile(self) -> bool:
        """
        在随机空位置添加一个新方块（90% 概率是2，10% 概率是4）
        :return: 是否成功添加
        """
        empty_cells = [(i, j) for i in range(self.size) 
                       for j in range(self.size) if self.board[i][j] == 0]
        
        if not empty_cells:
            return False
        
        i, j = random.choice(empty_cells)
        self.board[i][j] = 2 if random.random() < 0.9 else 4
        return True
    
    def get_empty_cells(self) -> List[Tuple[int, int]]:
        """获取所有空格子的位置"""
        return [(i, j) for i in range(self.size) 
                for j in range(self.size) if self.board[i][j] == 0]
    
    def clone(self) -> 'Game2048':
        """
        克隆当前游戏状态
        使用 __new__ 跳过 __init__（避免多余的随机方块生成），
        因为 clone() 在AI搜索树中被大量调用，是性能热点
        """
        new_game = Game2048.__new__(Game2048)
        new_game.size = self.size
        new_game.board = copy.deepcopy(self.board)
        new_game.score = self.score
        new_game.moved = self.moved
        return new_game
    
    def move(self, direction: str) -> bool:
        """
        执行移动操作
        :param direction: 移动方向 'up', 'down', 'left', 'right'
        :return: 是否成功移动（棋盘是否发生变化）
        """
        original_board = copy.deepcopy(self.board)
        original_score = self.score
        
        if direction == 'left':
            self._move_left()
        elif direction == 'right':
            self._move_right()
        elif direction == 'up':
            self._move_up()
        elif direction == 'down':
            self._move_down()
        else:
            return False
        
        # 检查棋盘是否发生变化
        moved = self.board != original_board
        
        if not moved:
            self.score = original_score  # 恢复分数
        
        return moved
    
    def _move_left(self):
        """向左移动"""
        for i in range(self.size):
            self.board[i] = self._merge_line(self.board[i])
    
    def _move_right(self):
        """向右移动"""
        for i in range(self.size):
            self.board[i] = self._merge_line(self.board[i][::-1])[::-1]
    
    def _move_up(self):
        """向上移动"""
        for j in range(self.size):
            column = [self.board[i][j] for i in range(self.size)]
            merged_column = self._merge_line(column)
            for i in range(self.size):
                self.board[i][j] = merged_column[i]
    
    def _move_down(self):
        """向下移动"""
        for j in range(self.size):
            column = [self.board[i][j] for i in range(self.size)]
            merged_column = self._merge_line(column[::-1])[::-1]
            for i in range(self.size):
                self.board[i][j] = merged_column[i]
    
    def _merge_line(self, line: List[int]) -> List[int]:
        """
        合并一行的逻辑
        :param line: 待合并的一行
        :return: 合并后的行
        """
        # 移除0，得到非零元素
        non_zero = [num for num in line if num != 0]
        
        # 合并相同的相邻元素
        merged = []
        i = 0
        while i < len(non_zero):
            if i + 1 < len(non_zero) and non_zero[i] == non_zero[i + 1]:
                merged_value = non_zero[i] * 2
                merged.append(merged_value)
                self.score += merged_value
                i += 2
            else:
                merged.append(non_zero[i])
                i += 1
        
        # 填充0到原始长度
        merged.extend([0] * (self.size - len(merged)))
        return merged
    
    def is_game_over(self) -> bool:
        """
        判断游戏是否结束
        :return: 游戏是否结束
        """
        # 有空格，游戏未结束
        if any(0 in row for row in self.board):
            return False
        
        # 检查是否有相邻相同的方块（可以合并）
        for i in range(self.size):
            for j in range(self.size):
                current = self.board[i][j]
                # 检查右边
                if j + 1 < self.size and self.board[i][j + 1] == current:
                    return False
                # 检查下边
                if i + 1 < self.size and self.board[i + 1][j] == current:
                    return False
        
        return True
    
    def get_max_tile(self) -> int:
        """获取棋盘上的最大方块值"""
        return max(max(row) for row in self.board)
    
    def get_available_moves(self) -> List[str]:
        """获取所有可用的移动方向"""
        moves = []
        for direction in ['up', 'down', 'left', 'right']:
            test_game = self.clone()
            if test_game.move(direction):
                moves.append(direction)
        return moves
    
    def print_board(self):
        """打印棋盘（用于调试）"""
        print(f"Score: {self.score}")
        print("-" * (self.size * 6 + 1))
        for row in self.board:
            print("|" + "|".join(f"{num:5}" for num in row) + "|")
            print("-" * (self.size * 6 + 1))
        print()
