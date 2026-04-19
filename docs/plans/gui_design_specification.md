# GUI Design Specification: Training Arena

**Status:** Draft

## Objective
To provide a centralized, user-friendly control center for the Training Ecosystem, allowing real-time configuration of simulation parameters, model management, and visual monitoring of the evolutionary process.

## Interface Structure
The GUI will consist of a main window with a top-level menu and a specialized layout for real-time monitoring.

---

## 1. Main Menus

### A. Environment Menu (Simulation Configuration)
Allows tuning the physics and logic of the training arena.

| Parameter | Default | Description |
| :--- | :--- | :--- |
| **Cycles** | 50 | Number of steps per episode. |
| **Spawning** | 10 | Number of random trials per individual to stabilize fitness estimation. |
| **Population** | 50 | Total number of individuals in each generation. |
| **Elitism** | 0.2 | Percentage of top performers passing to the next generation. |
| **Generations** | 100 | Total evolutionary iterations. |
| **Threshold** | 5 px | Radius around target center for "arrival" detection. |
| **Max Steps** | 50 | Hard limit on steps per episode. |

### B. Model Menu (Management)
Handles the lifecycle of trained neural weights.

* **Import:** Load a saved model (`.npy` + `.json`) into the simulation.
* **Export:** Save the current best-performing model.
* **Model List / Ranking:** A list of all saved models, displaying ID, timestamp, and max fitness score.

### C. Simulation Control Menu
Controls the execution state of the training process.

* **Start:** Begins the evolutionary process.
* **Stop:** Terminates the current run and returns to the main menu.
* **Pause:** Freezes the current generation/episode.
* **Reset:** Clears current state and returns to initial configuration.

---

## 2. Nerd Statistics (Real-time HUD)
An information panel (sidebar or overlay) providing deep technical insights during execution.

* **Current Generation:** The active iteration number.
* **Active Configuration:** A live readout of the current settings (Cycles, Spawning, Population, Elitism, Threshold, Max Steps).
* **Fitness Metrics:** 
    * Best Fitness (Current Gen).
    * Average Population Fitness.
    * Convergence Rate (Delta in fitness over last $N$ generations).
* **System Status:** Current FPS and simulation state (Running, Paused, Stopped).

---

## 3. Visual Rendering (The Arena)
The central area of the GUI, rendered via Pygame.

* **Background:** Solid Black.
* **Target:** White Rectangle.
* **Agents:** Red translucent circles/rectangles. Transparency (alpha) represents the agent's relative fitness or contribution to the population.
* **Layout:** 
    * **Top Bar:** Main Menus.
    * **Left/Right Sidebar:** Nerd Statistics.
    * **Center:** The Arena.
