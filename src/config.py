"""
Configuration settings for DeFi TVL Tracker.
"""

import os
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

print('FCO::::  "api_key": os.environ.get("GRAPH_API_KEY") ', os.environ.get("GRAPH_API_KEY") )
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
    },
    "swapx_subgraph": {
        "base_url": "https://gateway.thegraph.com/api/subgraphs/id/Gw1DrPbd1pBNorCWEfyb9i8txJ962qYqqPtuyX6iEH8u",
        "timeout": 30,  # seconds
        "headers": {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "DeFi-TVL-Tracker/1.0"
        },
        "api_key": os.environ.get("GRAPH_API_KEY")  # Name of environment variable for API key
    }
}

# Protocol configurations and mappings
PROTOCOL_CONFIG = {
    "swapx": {
        "defillama_slug": None,
        "defillama_project": None,
        "web_url": "https://swapx.fi",
        "swapx_subgraph": {
            "entity_type": "ichiVaults",
            "default_filters": {
                "totalValue_gt": 0
            },
            "field_mapping": {
                "tvl": "totalValue",
                "name": "name"
            }
        },
        "supported_providers": ["swapx_subgraph"],
        "default_provider": "swapx_subgraph"
    },
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
        "web_url": "https://pendle.finance/",
    },
    "euler": {
        "defillama_slug": "euler-v2",
        "defillama_project": "euler-v2",
        "web_url": "https://www.euler.finance",
    },
   "swapx": {
        "defillama_slug": "swapx",
        "defillama_project": "swapx",
        "web_url": "https://swapx.fi",
        "swapx_subgraph": {
            "entity_type": "ichiVaults",
            "default_filters": {},
            "field_mapping": {
                "tvl": "value",
                "tokenA": "tokenA.symbol",
                "tokenB": "tokenB.symbol"
            }
        },
        "supported_providers": ["swapx_subgraph", "defillama"],
        "default_provider": "swapx_subgraph"
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