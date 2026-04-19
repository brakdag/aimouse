# Training Environment & Simulation Specification

**Status:** Draft

## Objective
To define the formal rules, simulation parameters, and scoring metrics for the evolutionary training arena, ensuring a standardized and fair environment for model optimization.

## Simulation Parameters
To simulate realistic human-like interaction speeds, the environment operates under the following constraints:

* **Frame Rate:** 15 FPS (Frames Per Second).
* **Episode Duration:** Exactly 50 cycles (approx. 3.33 seconds per episode).
* **Randomization:** 
    * **Starting Position:** The agent's initial position is randomized within the canvas boundaries at the start of every episode.
    * **Target Position:** The target rectangle is randomized within the canvas boundaries at the start of every episode.

## Input/Output Protocol

### Input Vector (4 Features)
All spatial values are normalized to the range $[-1, 1]$, where $(0,0)$ represents the center of the canvas.
1. **Target X:** Normalized X-coordinate of the target center.
2. **Target Y:** Normalized Y-coordinate of the target center.
3. **Current X:** Normalized X-coordinate of the agent's current position.
4. **Current Y:** Normalized Y-coordinate of the agent's current position.

### Output Vector (5 Features)
Outputs are normalized signals representing intent:
1. **$\Delta X^+$:** Intent to move right.
2. **$\Delta Y^+$:** Intent to move down.
3. **$\Delta X^-$:** Intent to move left.
4. **$\Delta Y^-$:** Intent to move up.
5. **Arrived:** A convergence signal (binary/probability) indicating the agent believes the target has been reached.

## Scoring & Selection

### Fitness Metric: Euclidean Distance
The primary metric for evaluating an individual's performance is the **minimum Euclidean distance** achieved between the agent and the target center during the 50-cycle episode.

$$\text{Fitness} \propto \frac{1}{\text{min}(\text{dist}) + 1}$$

* **Goal:** Minimize the hypotenuse (distance) to the target.

### Selection Strategy: Elite Percentage
We utilize an **Elite Selection** mechanism:
1. At the end of a generation, all individuals are ranked by their fitness score.
2. A predefined percentage (the **Elite Rate**) of the top-performing individuals is selected to pass their genes (weights) directly to the next generation.
3. The remaining slots in the next generation are filled via crossover and mutation of these elites.

## Visual Representation
The training arena is rendered via a real-time graphical interface (Pygame) with the following aesthetic standards:
* **Background:** Solid Black.
* **Target:** White Rectangle.
* **Agents:** Red translucent circles/rectangles (to allow visualization of multiple overlapping agents during population evaluation).
* **UI:** Real-time display of current Generation and Best Fitness.
