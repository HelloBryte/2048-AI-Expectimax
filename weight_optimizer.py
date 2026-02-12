"""
权重自动优化模块
使用遗传算法自动调优AI评估函数的权重
"""
import random
import numpy as np
from typing import List, Tuple, Dict
from ai_solver import ExpectimaxAI
from game_logic import Game2048
import json
import time


class GeneticOptimizer:
    """遗传算法优化器"""
    
    def __init__(self, 
                 population_size: int = 20,
                 generations: int = 50,
                 mutation_rate: float = 0.2,
                 crossover_rate: float = 0.7,
                 elite_size: int = 2,
                 games_per_eval: int = 5):
        """
        初始化遗传算法优化器
        :param population_size: 种群大小
        :param generations: 迭代代数
        :param mutation_rate: 变异率
        :param crossover_rate: 交叉率
        :param elite_size: 精英个体数量（直接保留到下一代）
        :param games_per_eval: 每个个体评估的游戏次数
        """
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.elite_size = elite_size
        self.games_per_eval = games_per_eval
        
        # 权重范围
        self.weight_bounds = {
            'empty': (0.1, 5.0),
            'monotonicity': (0.1, 3.0),
            'smoothness': (-1.0, 0.5),
            'max_value': (0.1, 2.0),
        }
        
        self.best_weights = None
        self.best_score = 0
        self.history = []
    
    def create_individual(self) -> Dict[str, float]:
        """创建一个随机个体（一组权重）"""
        individual = {}
        for key, (min_val, max_val) in self.weight_bounds.items():
            individual[key] = random.uniform(min_val, max_val)
        return individual
    
    def create_population(self) -> List[Dict[str, float]]:
        """创建初始种群"""
        # 包含当前默认权重作为种子
        population = [{
            'empty': 2.7,
            'monotonicity': 1.0,
            'smoothness': -0.1,
            'max_value': 1.0,
        }]
        
        # 添加随机个体
        for _ in range(self.population_size - 1):
            population.append(self.create_individual())
        
        return population
    
    def evaluate_individual(self, weights: Dict[str, float]) -> Tuple[float, Dict]:
        """
        评估个体的适应度（多次游戏的平均表现）
        :param weights: 权重配置
        :return: (适应度分数, 统计信息)
        """
        scores = []
        max_tiles = []
        moves_list = []
        
        for _ in range(self.games_per_eval):
            game = Game2048()
            ai = ExpectimaxAI(search_depth=3)
            # 设置权重
            ai.weights = weights.copy()
            
            moves = 0
            while not game.is_game_over() and moves < 3000:  # 限制最大步数
                direction, _ = ai.get_best_move(game)
                if direction:
                    if game.move(direction):
                        game.add_random_tile()
                        moves += 1
                else:
                    break
            
            scores.append(game.score)
            max_tiles.append(game.get_max_tile())
            moves_list.append(moves)
        
        # 综合评分：平均分数 + 最大方块奖励 + 移动效率
        avg_score = np.mean(scores)
        avg_max_tile = np.mean(max_tiles)
        avg_moves = np.mean(moves_list)
        
        # 适应度函数：优先考虑分数和最大方块
        fitness = avg_score + avg_max_tile * 10 + avg_moves * 0.1
        
        stats = {
            'avg_score': avg_score,
            'max_score': max(scores),
            'avg_max_tile': avg_max_tile,
            'max_tile': max(max_tiles),
            'avg_moves': avg_moves,
            'fitness': fitness
        }
        
        return fitness, stats
    
    def select_parents(self, population: List[Dict], fitness_scores: List[float]) -> List[Dict]:
        """
        选择父代（锦标赛选择）
        :param population: 当前种群
        :param fitness_scores: 适应度分数
        :return: 选中的父代
        """
        parents = []
        for _ in range(len(population) - self.elite_size):
            # 锦标赛选择（随机选3个，取最好的）
            tournament_size = min(3, len(population))
            tournament_indices = random.sample(range(len(population)), tournament_size)
            tournament_fitness = [fitness_scores[i] for i in tournament_indices]
            winner_idx = tournament_indices[np.argmax(tournament_fitness)]
            parents.append(population[winner_idx].copy())
        
        return parents
    
    def crossover(self, parent1: Dict[str, float], parent2: Dict[str, float]) -> Tuple[Dict, Dict]:
        """交叉操作"""
        if random.random() > self.crossover_rate:
            return parent1.copy(), parent2.copy()
        
        child1, child2 = {}, {}
        for key in parent1.keys():
            # 算术交叉
            alpha = random.random()
            child1[key] = alpha * parent1[key] + (1 - alpha) * parent2[key]
            child2[key] = alpha * parent2[key] + (1 - alpha) * parent1[key]
        
        return child1, child2
    
    def mutate(self, individual: Dict[str, float]) -> Dict[str, float]:
        """变异操作"""
        mutated = individual.copy()
        for key in mutated.keys():
            if random.random() < self.mutation_rate:
                min_val, max_val = self.weight_bounds[key]
                # 高斯变异
                mutation = random.gauss(0, (max_val - min_val) * 0.1)
                mutated[key] = np.clip(mutated[key] + mutation, min_val, max_val)
        
        return mutated
    
    def optimize(self, verbose: bool = True) -> Dict[str, float]:
        """
        执行遗传算法优化
        :param verbose: 是否打印详细信息
        :return: 最优权重
        """
        print("🧬 开始遗传算法优化...")
        print(f"种群大小: {self.population_size}, 代数: {self.generations}")
        print(f"每个个体测试 {self.games_per_eval} 局游戏")
        print("-" * 80)
        
        # 创建初始种群
        population = self.create_population()
        
        for generation in range(self.generations):
            print(f"\n📊 第 {generation + 1}/{self.generations} 代")
            start_time = time.time()
            
            # 评估种群
            fitness_scores = []
            all_stats = []
            
            for i, individual in enumerate(population):
                fitness, stats = self.evaluate_individual(individual)
                fitness_scores.append(fitness)
                all_stats.append(stats)
                
                if verbose:
                    print(f"  个体 {i+1:2d}: 适应度={fitness:8.1f}, "
                          f"分数={stats['avg_score']:6.0f}, "
                          f"最大块={stats['max_tile']:4.0f}")
            
            # 记录最佳个体
            best_idx = np.argmax(fitness_scores)
            best_fitness = fitness_scores[best_idx]
            best_individual = population[best_idx]
            best_stats = all_stats[best_idx]
            
            if best_fitness > self.best_score:
                self.best_score = best_fitness
                self.best_weights = best_individual.copy()
                print(f"\n✨ 发现更优权重！")
                print(f"   适应度: {best_fitness:.1f}")
                print(f"   平均分数: {best_stats['avg_score']:.0f}")
                print(f"   最大方块: {best_stats['max_tile']:.0f}")
                self._print_weights(best_individual)
            
            # 保存历史
            self.history.append({
                'generation': generation + 1,
                'best_fitness': best_fitness,
                'avg_fitness': np.mean(fitness_scores),
                'best_weights': best_individual.copy(),
                'best_stats': best_stats
            })
            
            # 选择（保留精英）
            elite_indices = np.argsort(fitness_scores)[-self.elite_size:]
            new_population = [population[i].copy() for i in elite_indices]
            
            # 选择父代
            parents = self.select_parents(population, fitness_scores)
            
            # 交叉和变异
            random.shuffle(parents)
            for i in range(0, len(parents) - 1, 2):
                child1, child2 = self.crossover(parents[i], parents[i + 1])
                child1 = self.mutate(child1)
                child2 = self.mutate(child2)
                new_population.extend([child1, child2])
            
            # 补充到种群大小
            while len(new_population) < self.population_size:
                new_population.append(self.mutate(random.choice(parents)))
            
            population = new_population[:self.population_size]
            
            elapsed = time.time() - start_time
            print(f"⏱️  本代用时: {elapsed:.1f}秒")
        
        print("\n" + "=" * 80)
        print("🎉 优化完成！")
        print(f"最佳适应度: {self.best_score:.1f}")
        print("\n最优权重配置：")
        self._print_weights(self.best_weights)
        
        return self.best_weights
    
    def _print_weights(self, weights: Dict[str, float]):
        """打印权重配置"""
        for key, value in weights.items():
            print(f"   {key:20s}: {value:.4f}")
    
    def save_results(self, filename: str = "optimization_results.json"):
        """保存优化结果"""
        results = {
            'best_weights': self.best_weights,
            'best_score': self.best_score,
            'history': self.history,
            'parameters': {
                'population_size': self.population_size,
                'generations': self.generations,
                'mutation_rate': self.mutation_rate,
                'crossover_rate': self.crossover_rate,
                'games_per_eval': self.games_per_eval
            }
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 结果已保存到: {filename}")
    
    def load_weights(self, filename: str = "optimization_results.json") -> Dict[str, float]:
        """加载优化后的权重"""
        with open(filename, 'r', encoding='utf-8') as f:
            results = json.load(f)
        return results['best_weights']


def quick_optimize():
    """快速优化（少量代数，用于测试）"""
    print("🚀 快速优化模式")
    optimizer = GeneticOptimizer(
        population_size=8,
        generations=10,
        mutation_rate=0.2,
        crossover_rate=0.7,
        elite_size=2,
        games_per_eval=3
    )
    best_weights = optimizer.optimize()
    optimizer.save_results("quick_optimization.json")
    return best_weights


def full_optimize():
    """完整优化（推荐配置）"""
    print("🎯 完整优化模式")
    optimizer = GeneticOptimizer(
        population_size=20,
        generations=50,
        mutation_rate=0.2,
        crossover_rate=0.7,
        elite_size=3,
        games_per_eval=5
    )
    best_weights = optimizer.optimize()
    optimizer.save_results("full_optimization.json")
    return best_weights


if __name__ == "__main__":
    print("=" * 80)
    print("🎯 2048 AI权重自动优化系统")
    print("=" * 80)
    print("\n选择优化模式：")
    print("1. 快速优化 (10代, 8个体, 每个3局, ~3-5分钟)")
    print("2. 完整优化 (50代, 20个体, 每个5局, ~30-60分钟)")
    print("3. 自定义")
    
    choice = input("\n请选择 (1/2/3): ").strip()
    
    try:
        if choice == "1":
            best_weights = quick_optimize()
        elif choice == "2":
            best_weights = full_optimize()
        elif choice == "3":
            pop_size = int(input("种群大小 (推荐20): ") or 20)
            gens = int(input("代数 (推荐50): ") or 50)
            mut_rate = float(input("变异率 (推荐0.2): ") or 0.2)
            games = int(input("每个体测试局数 (推荐5): ") or 5)
            
            optimizer = GeneticOptimizer(
                population_size=pop_size,
                generations=gens,
                mutation_rate=mut_rate,
                games_per_eval=games
            )
            best_weights = optimizer.optimize()
            optimizer.save_results("custom_optimization.json")
        else:
            print("❌ 无效选择")
            exit(1)
        
        print("\n✅ 优化完成！")
        print("\n使用方法：")
        print("  python main.py --weights optimization_results.json")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  优化被用户中断")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
