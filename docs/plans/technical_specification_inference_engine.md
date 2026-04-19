# Technical Specification: Inference Engine

**Status:** Draft

## Objective
To define the technical requirements, components, and operational logic for the Inference Engine, the lightweight component responsible for real-time, high-frequency mouse control.

## Overview
The Inference Engine is a standalone module designed to execute pre-trained models. It operates in a high-frequency loop, receiving high-level objectives from a Strategic Layer (LLM) and translating them into organic mouse movements via continuous delta x and delta y outputs.

## System Components

### 1. Model Loader
* **Responsibility:** Ingests and prepares the pre-trained model weights for execution.
* **Supported Formats:** (To be decided, e.g., .npy for NumPy, .onnx for ONNX Runtime, or .bin for raw weights).
* **Requirement:** Must be able to load weights without requiring the full training ecosystem.

### 2. State Processor (Input Pipeline)
* **Responsibility:** Transforms raw environmental data into the mathematical representation required by the model.
* **Inputs:** 
    * Visual Canvas (Image/Matrix).
    * Target Rectangle (rect(x, y, w, h)).
    * Current Cursor Position.
* **Process:** Normalization, resizing, and feature engineering (e.g., calculating relative distance to target) to create the input tensor/matrix.

### 3. Inference Core (The Tactical Loop)
* **Responsibility:** The high-frequency execution heart of the engine.
* **Operational Frequency:** Target >= 60Hz.
* **Logic:** 
    1. Fetch current state via State Processor.
    2. Pass state through the loaded model.
    3. Receive delta x, delta y outputs.
    4. Trigger Output Controller.

### 4. Output Controller (Actuator)
* **Responsibility:** Translates model deltas into actual system-level mouse movements.
* **Mechanism:** Uses low-level OS calls or specialized libraries (e.g., pynput, pyautogui, or direct HID emulation) to move the cursor.
* **Constraint:** Must ensure movements are smooth and respect the delta scale provided by the model.

### 5. Completion Monitor
* **Responsibility:** Evaluates if the objective has been met.
* **Logic:** Continuously checks if the cursor position is within the bounds of the target rect or if the model has signaled a terminal state.
* **Output:** A binary signal (0/1) sent back to the Strategic Layer.

## Interface Specification

### Input (from Strategic Layer)
```json
{
  "command_id": "string",
  "target_rect": [x, y, width, height],
  "canvas_resolution": [width, height]
}
```

### Output (to Strategic Layer)
```json
{
  "command_id": "string",
  "status": "success | failure | running",
  "final_position": [x, y]
}
```

## Non-Functional Requirements
* **Minimal Dependencies:** The engine should avoid heavy machine learning frameworks (like full TensorFlow/PyTorch) if possible, preferring lightweight runtimes like ONNX Runtime or NumPy to maintain low latency.
* **Low Latency:** The time from "State Input" to "Mouse Movement" must be minimized to prevent control lag.
* **Robustness:** Must handle cases where the target rect is suddenly obscured or the canvas changes unexpectedly.

## Risks & Mitigations
* **Risk:** OS-level mouse movement latency.
* **Mitigation:** Test various libraries and consider direct input injection if necessary.
* **Risk:** Model drift (weights not matching the current environment).
* **Mitigation:** Strict versioning of model weights and environment metadata.