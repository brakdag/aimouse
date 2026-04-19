# Neural/Evolutionary Mouse Interface for LLMs

An advanced, high-frequency motor control interface designed to bridge the gap between high-level LLM reasoning and low-level, organic mouse movement.

## The Problem

Large Language Models (LLMs) are exceptional at visual reasoning and strategic decision-making but are fundamentally inefficient at direct, fine-grained motor control. Traditional methods of controlling a mouse via LLMs rely on sending absolute $(x, y)$ coordinates. This approach leads to:

*   **High Latency:** The slow feedback loop between reasoning and execution makes interaction feel sluggish.
*   **Robotic Movement:** Direct coordinate jumps lack the natural acceleration, deceleration, and micro-adjustments characteristic of human movement.
*   **Bot Detection:** Linear and perfectly precise movements are easily flagged by automated anti-bot systems.

## The Solution: Hierarchical Control

This project implements a hierarchical architecture that separates **Strategic Intent** from **Tactical Execution**.

1.  **Strategic Layer (LLM):** Provides high-level objectives (e.g., "Click the button" or "Move to the target area").
2.  **Tactical Layer (Neural/Evolutionary Engine):** A high-frequency controller that translates objectives into continuous, organic mouse movements.

## Technical Overview

### Input Specification
The tactical engine receives:
*   **Command:** A high-level instruction or goal.
*   **Canvas:** The visual context (e.g., a $640 \times 480$ pixel grid).
*   **Target:** A defined region of interest, typically represented as a rectangle: `rect(x, y, width, height)`.

### Processing
The input is transformed into a state representation (matrix) that the neural/evolutionary engine can process to understand the relationship between the current cursor position and the target.

### Output Specification
The engine operates in a high-frequency loop, outputting:
*   **$\Delta x$:** Horizontal movement delta (normalized between -1 and 1).
*   **$\Delta y$:** Vertical movement delta (normalized between -1 and 1).
*   **Completion Signal:** A binary flag (0 or 1) indicating whether the objective has been successfully met.

## Key Features

*   **Organic Kinematics:** Generates movements that mimic human acceleration and deceleration patterns.
*   **Anti-Detection:** Reduces the footprint of automated interactions by introducing natural jitter and non-linear trajectories.
*   **Low Latency:** Provides near-instantaneous response to visual feedback through a high-speed tactical loop.
