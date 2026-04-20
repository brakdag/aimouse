# Installation Guide: Neural Mouse Interface (NMI)

This package provides a high-frequency organic mouse control interface for LLMs.

## Prerequisites

Ensure the following system tools are installed:
- `scrot`: For screen captures (`sudo apt install scrot`)
- `ImageMagick`: For fast image manipulation (`sudo apt install imagemagick`)

## Installation

1. Clone this repository into your project folder.
2. Install the package in editable mode:
   ```bash
   pip install -e .
   ```

## Quick Start

```python
from src.inference.api import nmi

# 1. Get the vision guide for your LLM
print(nmi.get_vision_guide())

# 2. Capture and encode the screen
vision_data = nmi.capture_and_encode()
# Send vision_data['data'] (base64) to your LLM

# 3. Move organically to a coordinate provided by the LLM
# Coordinates are normalized [0.0, 1.0]
nmi.move_to(x=0.75, y=0.22)
```

## Architecture
- **Vision Encoder**: Uses a recursive color-based Quadtree to allow LLMs to locate objects in low-res (112px) images.
- **Organic Mover**: Uses a neural network (MLP) to translate targets into human-like mouse trajectories.