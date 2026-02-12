"""
2048游戏可视化界面
使用Pygame实现图形界面，展示AI自动运行过程
"""
import pygame
import sys
from typing import Optional
from game_logic import Game2048
from ai_solver import ExpectimaxAI


class GameVisualizer:
    """游戏可视化类"""
    
    # 颜色定义
    COLORS = {
        'background': (187, 173, 160),
        'empty': (205, 193, 180),
        'text_dark': (119, 110, 101),
        'text_light': (249, 246, 242),
        0: (205, 193, 180),
        2: (238, 228, 218),
        4: (237, 224, 200),
        8: (242, 177, 121),
        16: (245, 149, 99),
        32: (246, 124, 95),
        64: (246, 94, 59),
        128: (237, 207, 114),
        256: (237, 204, 97),
        512: (237, 200, 80),
        1024: (237, 197, 63),
        2048: (237, 194, 46),
        4096: (60, 58, 50),
    }
    
    def __init__(self, game: Game2048, ai: ExpectimaxAI, cell_size: int = 100):
        """
        初始化可视化界面
        :param game: 游戏实例
        :param ai: AI实例
        :param cell_size: 单元格大小
        """
        self.game = game
        self.ai = ai
        self.cell_size = cell_size
        self.padding = 10
        self.board_size = game.size * cell_size + (game.size + 1) * self.padding
        
        # 面板高度
        self.info_panel_height = 150
        self.control_panel_height = 60
        
        # 窗口大小
        self.width = self.board_size
        self.height = self.info_panel_height + self.board_size + self.control_panel_height
        
        # 初始化Pygame
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("2048 AI - Expectimax Algorithm")
        
        # 字体
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
        
        # 运行状态
        self.running = True
        self.auto_play = False
        self.game_over = False
        self.moves_count = 0
        self.last_move = None
        self.last_eval_score = 0
        
        # FPS控制
        self.clock = pygame.time.Clock()
        self.fps = 10  # 每秒移动次数
    
    def draw_board(self):
        """绘制游戏棋盘"""
        y_offset = self.info_panel_height
        
        # 绘制背景
        board_rect = pygame.Rect(0, y_offset, self.board_size, self.board_size)
        pygame.draw.rect(self.screen, self.COLORS['background'], board_rect)
        
        # 绘制每个单元格
        for i in range(self.game.size):
            for j in range(self.game.size):
                value = self.game.board[i][j]
                x = j * self.cell_size + (j + 1) * self.padding
                y = i * self.cell_size + (i + 1) * self.padding + y_offset
                
                # 绘制单元格背景
                rect = pygame.Rect(x, y, self.cell_size, self.cell_size)
                color = self.COLORS.get(value, self.COLORS[4096])
                pygame.draw.rect(self.screen, color, rect, border_radius=5)
                
                # 绘制数字
                if value != 0:
                    text_color = self.COLORS['text_light'] if value > 4 else self.COLORS['text_dark']
                    font_size = self.font_medium if value < 1000 else self.font_small
                    text = font_size.render(str(value), True, text_color)
                    text_rect = text.get_rect(center=rect.center)
                    self.screen.blit(text, text_rect)
    
    def draw_info_panel(self):
        """绘制信息面板"""
        panel_rect = pygame.Rect(0, 0, self.width, self.info_panel_height)
        pygame.draw.rect(self.screen, (250, 248, 239), panel_rect)
        
        # 标题
        title = self.font_large.render("2048 AI", True, self.COLORS['text_dark'])
        self.screen.blit(title, (20, 10))
        
        # 分数信息
        score_text = self.font_medium.render(f"Score: {self.game.score}", True, self.COLORS['text_dark'])
        self.screen.blit(score_text, (20, 60))
        
        max_tile = self.game.get_max_tile()
        max_text = self.font_medium.render(f"Max: {max_tile}", True, self.COLORS['text_dark'])
        self.screen.blit(max_text, (200, 60))
        
        # AI信息
        moves_text = self.font_small.render(f"Moves: {self.moves_count}", True, self.COLORS['text_dark'])
        self.screen.blit(moves_text, (20, 100))
        
        if self.last_move:
            move_text = self.font_small.render(f"Last: {self.last_move.upper()}", True, self.COLORS['text_dark'])
            self.screen.blit(move_text, (150, 100))
        
        time_text = self.font_small.render(f"Time: {self.ai.last_decision_time:.3f}s", True, self.COLORS['text_dark'])
        self.screen.blit(time_text, (270, 100))
        
        eval_text = self.font_small.render(f"Eval: {self.last_eval_score:.1f}", True, self.COLORS['text_dark'])
        self.screen.blit(eval_text, (20, 125))
        
        nodes_text = self.font_small.render(f"Nodes: {self.ai.nodes_explored}", True, self.COLORS['text_dark'])
        self.screen.blit(nodes_text, (150, 125))
    
    def draw_control_panel(self):
        """绘制控制面板"""
        y_offset = self.info_panel_height + self.board_size
        panel_rect = pygame.Rect(0, y_offset, self.width, self.control_panel_height)
        pygame.draw.rect(self.screen, (250, 248, 239), panel_rect)
        
        # 状态显示
        if self.game_over:
            status_text = "GAME OVER"
            color = (255, 0, 0)
        elif self.auto_play:
            status_text = "AUTO PLAYING... (Press SPACE to pause)"
            color = (0, 150, 0)
        else:
            status_text = "PAUSED (Press SPACE to start)"
            color = self.COLORS['text_dark']
        
        status = self.font_small.render(status_text, True, color)
        status_rect = status.get_rect(center=(self.width // 2, y_offset + 20))
        self.screen.blit(status, status_rect)
        
        # 控制提示
        hint_text = "R: Restart | +/-: Speed | Q: Quit"
        hint = self.font_small.render(hint_text, True, self.COLORS['text_dark'])
        hint_rect = hint.get_rect(center=(self.width // 2, y_offset + 45))
        self.screen.blit(hint, hint_rect)
    
    def draw(self):
        """绘制整个界面"""
        self.screen.fill((255, 255, 255))
        self.draw_info_panel()
        self.draw_board()
        self.draw_control_panel()
        pygame.display.flip()
    
    def handle_events(self):
        """处理用户输入事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # 切换自动运行
                    if not self.game_over:
                        self.auto_play = not self.auto_play
                
                elif event.key == pygame.K_r:
                    # 重新开始
                    self.game.init_game()
                    self.moves_count = 0
                    self.game_over = False
                    self.last_move = None
                    self.last_eval_score = 0
                
                elif event.key == pygame.K_q:
                    # 退出
                    self.running = False
                
                elif event.key == pygame.K_EQUALS or event.key == pygame.K_PLUS:
                    # 加速
                    self.fps = min(60, self.fps + 5)
                
                elif event.key == pygame.K_MINUS:
                    # 减速
                    self.fps = max(1, self.fps - 5)
                
                elif event.key == pygame.K_s:
                    # 单步执行
                    if not self.game_over:
                        self.make_ai_move()
    
    def make_ai_move(self):
        """让AI执行一步移动"""
        if self.game.is_game_over():
            self.game_over = True
            self.auto_play = False
            return
        
        # 获取AI的最佳移动
        best_move, eval_score = self.ai.get_best_move(self.game)
        
        if best_move:
            # 执行移动
            moved = self.game.move(best_move)
            if moved:
                self.game.add_random_tile()
                self.moves_count += 1
                self.last_move = best_move
                self.last_eval_score = eval_score
        else:
            self.game_over = True
            self.auto_play = False
    
    def run(self):
        """运行游戏主循环"""
        while self.running:
            self.handle_events()
            
            # 自动运行模式
            if self.auto_play and not self.game_over:
                self.make_ai_move()
            
            self.draw()
            self.clock.tick(self.fps)
        
        pygame.quit()
        sys.exit()


def main():
    """主函数"""
    # 创建游戏实例
    game = Game2048(size=4)
    
    # 创建AI实例（搜索深度3）
    ai = ExpectimaxAI(search_depth=3)
    
    # 创建可视化界面
    visualizer = GameVisualizer(game, ai, cell_size=100)
    
    # 运行游戏
    visualizer.run()


if __name__ == "__main__":
    main()
