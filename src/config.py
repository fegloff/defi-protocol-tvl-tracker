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
    },
    "kingdom_subgraph": {
        "base_url": "https://sonic.kingdomsubgraph.com/subgraphs/name/exp",
        "timeout": 30,  # seconds
        "headers": {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "DeFi-TVL-Tracker/1.0"
        }
    }
}

# Protocol configurations and mappings
PROTOCOL_CONFIG = {
    "silo": {
        "defillama_slug": "silo-finance",
        "defillama_project": "silo-v2",
        "web_url": "https://v2.silo.finance",
    },
    "aave": {
        "defillama_slug": "morpho-aavev3",
        "defillama_project": "aave-v3",
        "web_url": "https://aavev3.morpho.org/",
    },
    "beets": {
        "defillama_slug": "beets-lst",
        "defillama_project": "beets-dex",
        "web_url": "https://beets.fi",
    },
    "curve": {
        "defillama_slug": "curve-dex",
        "defillama_project": "curve-dex",
        "web_url": "https://curve.fi",
    },
    "pendle": {
        "defillama_slug": "pendle",
        "defillama_project": "pendle",
        "web_url": "https://curve.fi",
    },
    "shadow": {
        "defillama_slug": None,
        "defillama_project": None,
        "web_url": "https://www.shadow.so",
        "kingdom_subgraph": {
            "entity_type": "clPools",
            "default_filters": {
                "symbol_contains": "USD"
            },
            "field_mapping": {
                "tvl": "totalValueLockedUSD",
                "volume": "volumeUSD",
                "name": "symbol"
            }
        },
        "supported_providers": ["kingdom_subgraph"],
        "default_provider": "kingdom_subgraph"
    }
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
        if not key:
            return PROTOCOL_CONFIG
        else:
            return PROTOCOL_CONFIG.get(key, {})
    else:
        return default