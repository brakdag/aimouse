# System Architecture: Bifurcation of Inference and Training

**Status:** Draft

## Objective
To define a modular architecture that separates the real-time execution tool (Inference) from the model development ecosystem (Training).

## Overview
The project is divided into two distinct, decoupled components. This separation ensures that the production tool remains lightweight and optimized for low latency, while the training environment can be as computationally intensive as necessary.

---

## Part 1: The Inference Engine (The Tool)
**Goal:** Real-time, high-frequency mouse control using pre-trained weights.

### Core Responsibilities
* **Weight Loading:** Ingesting trained model parameters (weights) from the Training Ecosystem.
* **Real-time Loop:** Executing the high-frequency control loop (e.g., 60Hz+).
* **Visual Processing:** Processing the current canvas/image state.
* **Delta Generation:** Calculating and outputting $\Delta x$ and $\Delta y$ based on the loaded model.
* **Objective Monitoring:** Signaling completion or failure based on the target rect.

### Key Requirements
* **Minimal Latency:** Optimized for immediate response.
* **Portability:** Should be able to run in various environments with minimal dependencies.
* **Stability:** Robust error handling for unexpected visual inputs.

---

## Part 2: The Training Ecosystem (The Laboratory)
**Goal:** To create, train, and validate the neural/evolutionary models.

### Core Responsibilities
* **Environment Simulation:** A virtualized environment that simulates the canvas, the mouse, and the target movement (the "Gym").
* **Training Loop:** Implementing the optimization algorithm (Evolutionary Algorithms or Reinforcement Learning).
* **Reward Function Design:** Defining the mathematical criteria for success (speed, smoothness, accuracy, anti-detection).
* **Model Generation:** Exporting the optimized weights into a format compatible with the Inference Engine.

### Key Requirements
* **Scalability:** Ability to run multiple training instances in parallel.
* **Complexity:** Capable of simulating diverse and challenging scenarios (moving targets, noise, obstacles).
* **Data Logging:** Detailed tracking of training progress and performance metrics.

---

## Relationship Diagram

`[Training Ecosystem]` --(Generates Weights)--> `[Model Weights File]` --(Loaded by)--> `[Inference Engine]`

`[Inference Engine]` <--(Receives Objectives)-- `[Strategic Layer (LLM)]`

## Success Criteria for Separation
* The Inference Engine can run successfully without any training-related code or dependencies.
* The Training Ecosystem can generate new weights without needing the real-time mouse interface.
