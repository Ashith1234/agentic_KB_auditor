import yaml
import os
from typing import Any, Dict

def load_config(config_path: str = "configs/config.yaml") -> Dict[str, Any]:
    """
    Loads configuration from a YAML file.
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found at {config_path}")
    
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    return config

# Singleton access to config
_config = None

def get_config() -> Dict[str, Any]:
    global _config
    if _config is None:
        _config = load_config()
    return _config
