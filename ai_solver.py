"""
2048游戏AI求解器 - Expectimax算法
使用期望最大化算法和启发式评估函数来寻找最优移动
"""
import math
import time
from typing import Tuple, Optional
from game_logic import Game2048


class ExpectimaxAI:
    """基于Expectimax算法的2048 AI"""
    
    def __init__(self, search_depth: int = 3, weights_file: Optional[str] = None):
        """
        初始化AI
        :param search_depth: 搜索深度，越大越强但越慢，推荐3-5
        :param weights_file: 权重配置文件路径（JSON格式，可选）
        """
        self.search_depth = search_depth
        self.nodes_explored = 0
        self.last_decision_time = 0
        
        # 评估函数权重（默认值）
        self.weights = {
            'empty': 2.7,        # 空格数量权重
            'monotonicity': 1.0,  # 单调性权重
            'smoothness': -0.1,   # 平滑度权重
            'max_value': 1.0,     # 最大值权重
        }
        
        # 如果提供了权重文件，加载权重
        if weights_file:
            self.load_weights(weights_file)
    
    def load_weights(self, filename: str):
        """
        从JSON文件加载优化后的权重
        :param filename: 权重文件路径
        """
        import json
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                results = json.load(f)
                weights = results.get('best_weights', {})
                
                # 更新权重
                for key in self.weights.keys():
                    if key in weights:
                        self.weights[key] = weights[key]
                
                print(f"✅ 已加载优化权重: {filename}")
                print(f"   权重: {self.weights}")
        except FileNotFoundError:
            print(f"⚠️  权重文件未找到: {filename}，使用默认权重")
        except Exception as e:
            print(f"⚠️  加载权重失败: {e}，使用默认权重")
    
    def get_best_move(self, game: Game2048) -> Tuple[Optional[str], float]:
        """
        获取最佳移动方向
        :param game: 当前游戏状态
        :return: (最佳方向, 评估分数)
        """
        start_time = time.time()
        self.nodes_explored = 0
        
        available_moves = game.get_available_moves()
        if not available_moves:
            return None, 0
        
        best_move = None
        best_score = -math.inf
        
        # 尝试每个可能的移动
        for direction in available_moves:
            test_game = game.clone()
            test_game.move(direction)
            
            # 计算这个移动的期望得分
            score = self._expect_node(test_game, self.search_depth - 1)
            
            if score > best_score:
                best_score = score
                best_move = direction
        
        self.last_decision_time = time.time() - start_time
        return best_move, best_score
    
    def _max_node(self, game: Game2048, depth: int) -> float:
        """
        MAX节点：玩家选择最大化得分的移动
        :param game: 游戏状态
        :param depth: 剩余搜索深度
        :return: 最大期望得分
        """
        self.nodes_explored += 1
        
        if depth == 0 or game.is_game_over():
            return self._evaluate(game)
        
        max_score = -math.inf
        available_moves = game.get_available_moves()
        
        if not available_moves:
            return self._evaluate(game)
        
        for direction in available_moves:
            test_game = game.clone()
            test_game.move(direction)
            score = self._expect_node(test_game, depth - 1)
            max_score = max(max_score, score)
        
        return max_score
    
    def _expect_node(self, game: Game2048, depth: int) -> float:
        """
        EXPECT节点：计算随机放置新方块的期望得分
        :param game: 游戏状态
        :param depth: 剩余搜索深度
        :return: 期望得分
        """
        self.nodes_explored += 1
        
        if depth == 0 or game.is_game_over():
            return self._evaluate(game)
        
        empty_cells = game.get_empty_cells()
        if not empty_cells:
            return self._evaluate(game)
        
        total_score = 0
        num_empty = len(empty_cells)
        
        # 对每个空格位置，计算放置2或4的期望
        for i, j in empty_cells:
            # 放置2的情况（概率0.9）
            test_game = game.clone()
            test_game.board[i][j] = 2
            score_2 = self._max_node(test_game, depth - 1)
            
            # 放置4的情况（概率0.1）
            test_game.board[i][j] = 4
            score_4 = self._max_node(test_game, depth - 1)
            
            # 加权平均
            total_score += (0.9 * score_2 + 0.1 * score_4) / num_empty
        
        return total_score
    
    def _evaluate(self, game: Game2048) -> float:
        """
        启发式评估函数：评估当前棋盘状态的好坏
        :param game: 游戏状态
        :return: 评估分数（越高越好）
        """
        board = game.board
        size = game.size
        
        # 1. 空格数量（越多越好）
        empty_cells = len(game.get_empty_cells())
        empty_score = empty_cells ** 2
        
        # 2. 单调性（大数字应该在边角）
        monotonicity_score = self._calculate_monotonicity(board, size)
        
        # 3. 平滑度（相邻格子数值差异应该小）
        smoothness_score = self._calculate_smoothness(board, size)
        
        # 4. 最大值位置（最大值应该在角落）
        max_tile = game.get_max_tile()
        max_tile_score = math.log2(max_tile) if max_tile > 0 else 0
        
        # 加权求和
        total_score = (
            self.weights['empty'] * empty_score +
            self.weights['monotonicity'] * monotonicity_score +
            self.weights['smoothness'] * smoothness_score +
            self.weights['max_value'] * max_tile_score
        )
        
        return total_score
    
    def _calculate_monotonicity(self, board, size) -> float:
        """
        计算单调性：检查行和列是否单调递增或递减
        单调性越好，得分越高
        """
        totals = [0, 0, 0, 0]  # 上、下、左、右
        
        # 检查每一行
        for i in range(size):
            current = 0
            next_pos = 1
            while next_pos < size:
                while next_pos < size and board[i][next_pos] == 0:
                    next_pos += 1
                if next_pos >= size:
                    next_pos -= 1
                
                current_value = math.log2(board[i][current]) if board[i][current] > 0 else 0
                next_value = math.log2(board[i][next_pos]) if board[i][next_pos] > 0 else 0
                
                if current_value > next_value:
                    totals[0] += next_value - current_value
                elif next_value > current_value:
                    totals[1] += current_value - next_value
                
                current = next_pos
                next_pos += 1
        
        # 检查每一列
        for j in range(size):
            current = 0
            next_pos = 1
            while next_pos < size:
                while next_pos < size and board[next_pos][j] == 0:
                    next_pos += 1
                if next_pos >= size:
                    next_pos -= 1
                
                current_value = math.log2(board[current][j]) if board[current][j] > 0 else 0
                next_value = math.log2(board[next_pos][j]) if board[next_pos][j] > 0 else 0
                
                if current_value > next_value:
                    totals[2] += next_value - current_value
                elif next_value > current_value:
                    totals[3] += current_value - next_value
                
                current = next_pos
                next_pos += 1
        
        return max(totals[0], totals[1]) + max(totals[2], totals[3])
    
    def _calculate_smoothness(self, board, size) -> float:
        """
        计算平滑度：相邻格子的数值差异
        差异越小，得分越高（但我们取负值，所以差异大会扣分）
        """
        smoothness = 0
        
        for i in range(size):
            for j in range(size):
                if board[i][j] != 0:
                    value = math.log2(board[i][j])
                    
                    # 检查右边
                    if j + 1 < size and board[i][j + 1] != 0:
                        target_value = math.log2(board[i][j + 1])
                        smoothness -= abs(value - target_value)
                    
                    # 检查下边
                    if i + 1 < size and board[i + 1][j] != 0:
                        target_value = math.log2(board[i + 1][j])
                        smoothness -= abs(value - target_value)
        
        return smoothness
    
    def get_stats(self) -> dict:
        """获取AI统计信息"""
        return {
            'nodes_explored': self.nodes_explored,
            'decision_time': self.last_decision_time,
            'search_depth': self.search_depth
        }
