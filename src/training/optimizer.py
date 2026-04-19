"""
Optimization Engine for the Neural Mouse Interface.
Implements an Evolutionary Algorithm with a 4-10-10-5 MLP architecture.
"""
import numpy as np
import threading
from src.common.types import Rect, ActionOutput, AgentState
from src.training.simulator import MouseEnvironment
from src.training.evaluator import FitnessEvaluator

class Individual:
    def __init__(self, genome_size: int, weights: np.ndarray = None):
        self.genome_size = genome_size
        if weights is not None:
            self.weights = weights
        else:
            self.weights = np.random.uniform(-1, 1, genome_size)
        self.fitness = 0.0

class EvolutionaryOptimizer:
    def __init__(self, 
                 input_size: int = 4, 
                 hidden_size: int = 10, 
                 output_size: int = 5,
                 env: MouseEnvironment = None, 
                 evaluator: FitnessEvaluator = None, 
                 pop_size: int = 50, 
                 spawning: int = 10,
                 mutation_rate: float = 0.1, 
                 mutation_strength: float = 0.2):
        
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size
        
        # Genome calculation: (in*h1) + h1 + (h1*h2) + h2 + (h2*out) + out
        self.genome_size = (input_size * hidden_size) + hidden_size + (hidden_size * hidden_size) + hidden_size + (hidden_size * output_size) + output_size
        
        self.env = env
        self.evaluator = evaluator
        self.pop_size = pop_size
        self.spawning = spawning
        self.mutation_rate = mutation_rate
        self.mutation_strength = mutation_strength
        self.population = [Individual(self.genome_size) for _ in range(pop_size)]

        self.stop_event = threading.Event()
        self.pause_event = threading.Event()
        self.pause_event.set()

        self.shared_agent_data = [] 
        self._data_lock = threading.Lock()

    def _forward_pass(self, weights: np.ndarray, input_vec: np.ndarray) -> ActionOutput:
        idx = 0
        
        # Layer 1: Input -> Hidden 1
        w1_end = idx + (self.input_size * self.hidden_size)
        w1 = weights[idx:w1_end].reshape((self.input_size, self.hidden_size))
        idx = w1_end
        b1_end = idx + self.hidden_size
        b1 = weights[idx:b1_end]
        idx = b1_end
        
        # Layer 2: Hidden 1 -> Hidden 2
        w2_end = idx + (self.hidden_size * self.hidden_size)
        w2 = weights[idx:w2_end].reshape((self.hidden_size, self.hidden_size))
        idx = w2_end
        b2_end = idx + self.hidden_size
        b2 = weights[idx:b2_end]
        idx = b2_end
        
        # Layer 3: Hidden 2 -> Output
        w3_end = idx + (self.hidden_size * self.output_size)
        w3 = weights[idx:w3_end].reshape((self.hidden_size, self.output_size))
        idx = w3_end
        b3_end = idx + self.output_size
        b3 = weights[idx:b3_end]

        # Computation with Tanh for hidden layers
        h1 = np.tanh(np.dot(input_vec, w1) + b1)
        h2 = np.tanh(np.dot(h1, w2) + b2)
        
        # Computation with Sigmoid for output layer
        # Sigmoid(x) = 1 / (1 + exp(-x))
        out = 1.0 / (1.0 + np.exp(-np.dot(h2, w3) + b3))
        
        return ActionOutput(
            dx_plus=float(out[0]),
            dy_plus=float(out[1]),
            dx_minus=float(out[2]),
            dy_minus=float(out[3]),
            arrived=float(out[4])
        )

    def _run_single_trial(self, individual: Individual, processor) -> tuple[float, list[AgentState]]:
        from src.common.types import Rect
        target_rect = Rect(370, 270, 60, 60) 
        self.env.target_rect = target_rect
        
        state, _ = self.env.reset()
        trajectory = [state]
        
        done = False
        while not done:
            self.pause_event.wait()
            if self.stop_event.is_set():
                break

            input_state = processor.process(target_rect, state.position)
            action = self._forward_pass(individual.weights, input_state.to_array())
            state, reward, done = self.env.step(action)
            trajectory.append(state)
            
            with self._data_lock:
                self.shared_agent_data = [(state, 0.5)]
            
        return self.evaluator.evaluate(trajectory, target_rect, self.env.steps_taken).total, trajectory

    def evolve(self, processor) -> Individual:
        self.stop_event.clear()
        self.pause_event.set()

        for gen in range(1000):
            if self.stop_event.is_set():
                break

            for ind in self.population:
                # Spawning: Average fitness over N trials
                trial_fitnesses = []
                for _ in range(self.spawning):
                    f, _ = self._run_single_trial(ind, processor)
                    trial_fitnesses.append(f)
                ind.fitness = np.mean(trial_fitnesses)
            
            self.population.sort(key=lambda x: x.fitness, reverse=True)
            
            new_population = self.population[:max(1, self.pop_size // 10)]

            while len(new_population) < self.pop_size:
                p1 = self._tournament_selection()
                p2 = self._tournament_selection()
                child_w = self._crossover(p1.weights, p2.weights)
                child_w = self._mutate(child_w)
                new_population.append(Individual(self.genome_size, child_w))
            
            self.population = new_population

        return self.population[0]

    def _tournament_selection(self, k: int = 3) -> Individual:
        candidates = np.random.choice(self.population, k)
        return max(candidates, key=lambda x: x.fitness)

    def _crossover(self, w1: np.ndarray, w2: np.ndarray) -> np.ndarray:
        alpha = np.random.rand()
        return alpha * w1 + (1 - alpha) * w2

    def _mutate(self, weights: np.ndarray) -> np.ndarray:
        mask = np.random.rand(self.genome_size) < self.mutation_rate
        noise = np.random.normal(0, self.mutation_strength, self.genome_size)
        weights[mask] += noise[mask]
        return np.clip(weights, -1, 1)

    def get_shared_data(self):
        with self._data_lock:
            return list(self.shared_agent_data)
