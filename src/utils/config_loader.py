import yaml
import os
import json

def load_config(config_path='data/config/config.yaml'):
    """Load configuration from YAML file"""
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    
    return config

def save_config(config, config_path='data/config/config.yaml'):
    """Save configuration to YAML file"""
    # Ensure directory exists
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    
    with open(config_path, 'w') as file:
        yaml.dump(config, file, default_flow_style=False)
    
    return True

def save_regions(regions, regions_path='data/config/regions.json'):
    """Save custom regions to JSON file"""
    # Ensure directory exists
    os.makedirs(os.path.dirname(regions_path), exist_ok=True)
    
    with open(regions_path, 'w') as file:
        json.dump(regions, file)
    
    return True

def load_regions(regions_path='data/config/regions.json'):
    """Load custom regions from JSON file"""
    if not os.path.exists(regions_path):
        return None
    
    with open(regions_path, 'r') as file:
        regions = json.load(file)
    
    return regions
