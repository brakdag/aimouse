"""
Optimization Engine for the Neural Mouse Interface.
Implements an Evolutionary Algorithm with a 2-5-5-3 MLP architecture.
Supports batch simulation with a relative angle compass.
"""
import numpy as np
import threading
import time
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
                 input_size: int = 2, 
                 hidden_layers: list = [5, 5], 
                 output_size: int = 3,
                 env: MouseEnvironment = None, 
                 evaluator: FitnessEvaluator = None, 
                 pop_size: int = 50, 
                 spawning: int = 10,
                 mutation_rate: float = 0.1, 
                 mutation_strength: float = 0.2,
                 fps: int = 0,
                 elitism: float = 0.2):
        
        self.input_size = input_size
        self.hidden_layers = hidden_layers
        self.output_size = output_size
        
        self.genome_size = 0
        prev_size = input_size
        for h_size in hidden_layers:
            self.genome_size += (prev_size * h_size) + h_size
            prev_size = h_size
        self.genome_size += (prev_size * output_size) + output_size
        
        self.env = env
        self.evaluator = evaluator
        self.pop_size = pop_size
        self.spawning = spawning
        self.mutation_rate = mutation_rate
        self.mutation_strength = mutation_strength
        self.fps = fps
        self.elitism = elitism
        self.population = [Individual(self.genome_size) for _ in range(pop_size)]

        self.stop_event = threading.Event()
        self.pause_event = threading.Event()
        self.pause_event.set()

        self.shared_agent_data = [] 
        self._data_lock = threading.Lock()

    def _forward_pass(self, weights: np.ndarray, input_vec: np.ndarray) -> ActionOutput:
        idx = 0
        current_vec = input_vec
        for h_size in self.hidden_layers:
            w_end = idx + (current_vec.shape[0] * h_size)
            w = weights[idx:w_end].reshape((current_vec.shape[0], h_size))
            idx = w_end
            b_end = idx + h_size
            b = weights[idx:b_end]
            idx = b_end
            current_vec = np.tanh(np.dot(current_vec, w) + b)
        
        w_end = idx + (current_vec.shape[0] * self.output_size)
        w_out = weights[idx:w_end].reshape((current_vec.shape[0], self.output_size))
        idx = w_end
        b_end = idx + self.output_size
        b_out = weights[idx:b_end]
        out = 1.0 / (1.0 + np.exp(-np.dot(current_vec, w_out) + b_out))
        
        return ActionOutput(
            move=float(out[0]),
            rotate=float(out[1]),
            arrived=float(out[2])
        )

    def _run_batch_trial(self, processor, max_steps: int) -> list[float]:
        target_rect = self.env.reset_target()
        start_state = self.env.reset_agent()
        agent_states = [start_state for _ in range(self.pop_size)]
        
        trajectories = [[] for _ in range(self.pop_size)]
        dones = [False] * self.pop_size

        for step in range(max_steps):
            self.pause_event.wait()
            if self.stop_event.is_set():
                break

            current_batch_data = []

            for i in range(self.pop_size):
                if dones[i]:
                    # Use a dummy action to keep the 'arrived' signal for visualization
                    # We'll store the last action taken
                    current_batch_data.append((agent_states[i], 0.5, 0.0))
                    continue

                input_state = processor.process(target_rect, agent_states[i])
                
                action = self._forward_pass(self.population[i].weights, input_state.to_array())
                
                new_state, reward, done = self.env.step(agent_states[i], action)
                
                agent_states[i] = new_state
                trajectories[i].append(new_state)
                dones[i] = done
                # Store state, alpha, and the 'arrived' signal
                current_batch_data.append((new_state, 0.5, action.arrived))

            with self._data_lock:
                self.shared_agent_data = current_batch_data
            
            if self.fps > 0:
                time.sleep(1.0 / self.fps)

        fitnesses = []
        for i in range(self.pop_size):
            steps_taken = len(trajectories[i])
            if not dones[i]:
                steps_taken = max_steps
            f = self.evaluator.evaluate(trajectories[i], target_rect, steps_taken).total
            fitnesses.append(f)
            
        return fitnesses

    def evolve(self, processor, num_generations: int, progress_callback=None) -> Individual:
        self.stop_event.clear()
        self.pause_event.set()
        max_steps = getattr(self.evaluator, 'max_steps', 50)

        for gen in range(num_generations):
            if self.stop_event.is_set():
                break

            total_fitnesses = np.zeros(self.pop_size)
            for _ in range(self.spawning):
                batch_fitnesses = self._run_batch_trial(processor, max_steps)
                total_fitnesses += np.array(batch_fitnesses)
            
            for i in range(self.pop_size):
                self.population[i].fitness = total_fitnesses[i] / self.spawning
            
            self.population.sort(key=lambda x: x.fitness, reverse=True)
            
            elite_count = max(1, int(self.pop_size * self.elitism))
            new_population = self.population[:elite_count]

            while len(new_population) < self.pop_size:
                p1 = self._tournament_selection()
                p2 = self._tournament_selection()
                child_w = self._crossover(p1.weights, p2.weights)
                child_w = self._mutate(child_w)
                new_population.append(Individual(self.genome_size, child_w))
            
            self.population = new_population
            
            if progress_callback:
                progress_callback(gen + 1, self.population[0].fitness)

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

    def get_best_weights(self) -> np.ndarray:
        if not self.population:
            return None
        best = max(self.population, key=lambda x: x.fitness)
        return best.weights

    def inject_elite_weights(self, weights: np.ndarray):
        if len(weights) != self.genome_size:
            raise ValueError(f"Weight size mismatch. Expected {self.genome_size}, got {len(weights)}")
        self.population[0] = Individual(self.genome_size, weights)
