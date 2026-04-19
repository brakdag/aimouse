"""
Model Exporter for the Training Ecosystem.
Saves optimized weights and metadata.
"""
import numpy as np
import json
import os
from datetime import datetime
from src.common.types import FitnessScore

class ModelExporter:
    def __init__(self, base_model_dir: str = "models/"):
        self.base_model_dir = base_model_dir
        if not os.path.exists(self.base_model_dir):
            os.makedirs(self.base_model_dir)

    def export(self, weights: np.ndarray, fitness: FitnessScore, model_name: str = "mouse_model") -> str:
        """Exports weights and metadata to the models directory.
        
        Args:
            weights: The optimized weight array.
            fitness: The fitness score achieved.
            model_name: Base name for the files.
            
        Returns:
            The path to the exported weights file.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename_base = f"{model_name}_{timestamp}"
        
        weights_path = os.path.join(self.base_model_dir, f"{filename_base}.npy")
        metadata_path = os.path.join(self.base_model_dir, f"{filename_base}_metadata.json")
        
        # 1. Save Weights
        np.save(weights_path, weights)
        
        # 2. Save Metadata
        metadata = {
            "model_name": model_name,
            "timestamp": timestamp,
            "fitness": {
                "accuracy": fitness.accuracy,
                "speed": fitness.speed,
                "smoothness": fitness.smoothness,
                "anti_detection": fitness.anti_detection,
                "total": fitness.total
            },
            "genome_size": len(weights)
        }
        
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=4)
            
        print(f"Model exported successfully:")
        print(f"  Weights: {weights_path}")
        print(f"  Metadata: {metadata_path}")
        
        return weights_path
