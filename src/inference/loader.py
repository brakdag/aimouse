import numpy as np
import json
import os

class ModelLoader:
    def __init__(self, model_dir='models/'):
        self.model_dir = model_dir

    def load(self, weights_path):
        if not os.path.exists(weights_path):
            raise FileNotFoundError(f'Weights file not found: {weights_path}')

        base_path = os.path.splitext(weights_path)[0]
        metadata_path = f'{base_path}_metadata.json'

        if not os.path.exists(metadata_path):
            raise FileNotFoundError(f'Metadata file not found: {metadata_path}')

        weights = np.load(weights_path)

        with open(metadata_path, 'r') as f:
            metadata = json.load(f)

        expected_size = metadata.get('genome_size')
        if expected_size is not None and len(weights) != expected_size:
            raise ValueError(f'Weight mismatch! Expected {expected_size}, got {len(weights)}')

        print(f'Successfully loaded model: {metadata.get("model_name", "unknown")}')
        return weights, metadata