"""
Model management for WhisperX and Pyannote models
Handles downloading, caching, and version management
"""
from pathlib import Path
from typing import Optional, Dict, Any
import json

from transcription_app.utils.logger import get_logger

logger = get_logger(__name__)


class ModelManager:
    """Manages ML model downloads and caching"""

    # Available Whisper models with approximate sizes
    WHISPER_MODELS = {
        'tiny': {'size_mb': 39, 'params': '39M'},
        'base': {'size_mb': 74, 'params': '74M'},
        'small': {'size_mb': 244, 'params': '244M'},
        'medium': {'size_mb': 769, 'params': '769M'},
        'large-v2': {'size_mb': 1550, 'params': '1550M'},
        'large-v3': {'size_mb': 1550, 'params': '1550M'},
    }

    def __init__(self, config):
        self.config = config
        self.models_dir = config.models_dir
        self.cache_file = self.models_dir / 'model_cache.json'

        # Ensure models directory exists
        self.models_dir.mkdir(parents=True, exist_ok=True)

    def get_model_info(self, model_name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a Whisper model

        Args:
            model_name: Name of the model

        Returns:
            Dictionary with model information or None if not found
        """
        return self.WHISPER_MODELS.get(model_name)

    def is_model_downloaded(self, model_name: str) -> bool:
        """
        Check if a model is already downloaded

        Args:
            model_name: Name of the model to check

        Returns:
            True if model exists locally
        """
        # Check cache file
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r') as f:
                    cache = json.load(f)
                    if model_name in cache.get('whisper_models', []):
                        logger.info(f"Model {model_name} found in cache")
                        return True
            except Exception as e:
                logger.warning(f"Error reading cache file: {e}")

        # Check if model directory exists
        model_path = self.models_dir / model_name
        exists = model_path.exists()
        logger.info(f"Model {model_name} exists: {exists}")
        return exists

    def mark_model_downloaded(self, model_name: str):
        """
        Mark a model as downloaded in the cache

        Args:
            model_name: Name of the downloaded model
        """
        try:
            cache = {}
            if self.cache_file.exists():
                with open(self.cache_file, 'r') as f:
                    cache = json.load(f)

            if 'whisper_models' not in cache:
                cache['whisper_models'] = []

            if model_name not in cache['whisper_models']:
                cache['whisper_models'].append(model_name)

            with open(self.cache_file, 'w') as f:
                json.dump(cache, f, indent=2)

            logger.info(f"Marked model {model_name} as downloaded")
        except Exception as e:
            logger.error(f"Error updating cache: {e}")

    def get_download_size(self, model_name: str) -> int:
        """
        Get approximate download size in MB

        Args:
            model_name: Name of the model

        Returns:
            Size in MB or 0 if unknown
        """
        info = self.get_model_info(model_name)
        return info.get('size_mb', 0) if info else 0

    def list_downloaded_models(self) -> list:
        """
        List all downloaded models

        Returns:
            List of model names
        """
        models = []

        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'r') as f:
                    cache = json.load(f)
                    models = cache.get('whisper_models', [])
        except Exception as e:
            logger.warning(f"Error reading cache: {e}")

        logger.info(f"Downloaded models: {models}")
        return models

    def clear_cache(self):
        """Clear the model cache file"""
        try:
            if self.cache_file.exists():
                self.cache_file.unlink()
                logger.info("Model cache cleared")
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")

    def get_storage_info(self) -> Dict[str, Any]:
        """
        Get storage information about models

        Returns:
            Dictionary with storage statistics
        """
        total_size = 0
        model_count = 0

        if self.models_dir.exists():
            for item in self.models_dir.iterdir():
                if item.is_dir():
                    model_count += 1
                    # Calculate directory size
                    for file in item.rglob('*'):
                        if file.is_file():
                            total_size += file.stat().st_size

        return {
            'models_dir': str(self.models_dir),
            'model_count': model_count,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'total_size_gb': round(total_size / (1024 * 1024 * 1024), 2)
        }
