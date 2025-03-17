"""
Configuration settings for DeFi TVL Tracker.
"""

import os
from typing import Dict, Any

# API configurations
API_CONFIG = {
    "defillama": {
        "base_url": "https://api.llama.fi/",
        "timeout": 30  # seconds
    },
    "subgraph": {
        "base_url": "https://api.thegraph.com/subgraphs/name/",
        "timeout": 30  # seconds
    }
}

# Protocol configurations and mappings
PROTOCOL_CONFIG = {
    "silo": {
        "defillama_slug": "silo-finance",
        "web_url": "https://v2.silo.finance/markets/{protocol}/{pool}",
        "subgraph_id": None,
        "contract_address": None
    },
}

# Get configuration value with fallback
def get_config(section: str, key: str, default: Any = None) -> Any:
    """
    Get configuration value with fallback.
    
    Args:
        section: Configuration section
        key: Configuration key
        default: Default value if not found
        
    Returns:
        Configuration value
    """
    if section == "api":
        return API_CONFIG.get(key, {})
    elif section == "protocol":
        return PROTOCOL_CONFIG.get(key, {})
    else:
        return default