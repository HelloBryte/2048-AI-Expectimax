"""
2048 AI游戏 - 主程序入口
支持命令行模式和GUI模式
"""
import argparse
from game_logic import Game2048
from ai_solver import ExpectimaxAI
from visualizer import GameVisualizer


def run_cli_mode(depth: int = 3, verbose: bool = True, weights_file: str = None):
    """
    命令行模式：纯文本显示，用于测试和调试
    :param depth: AI搜索深度
    :param verbose: 是否显示详细信息
    :param weights_file: 权重文件路径
    """
    game = Game2048()
    ai = ExpectimaxAI(search_depth=depth, weights_file=weights_file)
    
    move_count = 0
    print("=" * 50)
    print("2048 AI - Command Line Mode")
    print("=" * 50)
    print()
    
    while not game.is_game_over():
        if verbose:
            game.print_board()
        
        # AI决策
        best_move, eval_score = ai.get_best_move(game)
        
        if best_move is None:
            break
        
        # 执行移动
        moved = game.move(best_move)
        if moved:
            game.add_random_tile()
            move_count += 1
            
            if verbose:
                stats = ai.get_stats()
                print(f"Move #{move_count}: {best_move.upper()}")
                print(f"Eval Score: {eval_score:.2f}")
                print(f"Decision Time: {stats['decision_time']:.3f}s")
                print(f"Nodes Explored: {stats['nodes_explored']}")
                print()
    
    # 游戏结束
    print("=" * 50)
    print("GAME OVER!")
    print("=" * 50)
    game.print_board()
    print(f"Final Score: {game.score}")
    print(f"Max Tile: {game.get_max_tile()}")
    print(f"Total Moves: {move_count}")
    print()


def run_gui_mode(depth: int = 3, cell_size: int = 100, weights_file: str = None):
    """
    图形界面模式：使用Pygame显示
    :param depth: AI搜索深度
    :param cell_size: 单元格大小（像素）
    :param weights_file: 权重文件路径
    """
    game = Game2048()
    ai = ExpectimaxAI(search_depth=depth, weights_file=weights_file)
    visualizer = GameVisualizer(game, ai, cell_size=cell_size)
    visualizer.run()


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='2048 AI Game - Expectimax Algorithm',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python main.py                    # GUI模式（默认）
  python main.py --cli              # 命令行模式
  python main.py --depth 4          # GUI模式，搜索深度4
  python main.py --cli --depth 5    # 命令行模式，搜索深度5
  python main.py --size 120         # GUI模式，更大的单元格

控制说明（GUI模式）:
  SPACE    - 开始/暂停自动运行
  S        - 单步执行
  R        - 重新开始
  +/-      - 加速/减速
  Q        - 退出
        """
    )
    
    parser.add_argument(
        '--mode',
        choices=['gui', 'cli'],
        default='gui',
        help='运行模式：gui（图形界面）或 cli（命令行）'
    )
    
    parser.add_argument(
        '--cli',
        action='store_true',
        help='使用命令行模式（等同于 --mode cli）'
    )
    
    parser.add_argument(
        '--depth',
        type=int,
        default=3,
        help='AI搜索深度（1-6，默认3）。深度越大AI越强但速度越慢'
    )
    
    parser.add_argument(
        '--size',
        type=int,
        default=100,
        help='GUI模式：单元格大小（像素，默认100）'
    )
    
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='CLI模式：减少输出信息'
    )
    
    parser.add_argument(
        '--weights',
        type=str,
        default=None,
        help='权重配置文件路径（使用优化后的权重）'
    )
    
    args = parser.parse_args()
    
    # 验证参数
    if args.depth < 1 or args.depth > 6:
        print("警告：搜索深度建议在1-6之间")
        if args.depth < 1:
            args.depth = 1
        elif args.depth > 6:
            args.depth = 6
    
    # 确定运行模式
    mode = 'cli' if args.cli else args.mode
    
    print("=" * 50)
    print("🎮 2048 AI - Expectimax Algorithm")
    print("=" * 50)
    print(f"运行模式: {'命令行' if mode == 'cli' else '图形界面'}")
    print(f"搜索深度: {args.depth}")
    if args.weights:
        print(f"权重文件: {args.weights}")
    print("=" * 50)
    print()
    
    try:
        if mode == 'cli':
            run_cli_mode(depth=args.depth, verbose=not args.quiet, weights_file=args.weights)
        else:
            run_gui_mode(depth=args.depth, cell_size=args.size, weights_file=args.weights)
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
