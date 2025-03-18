"""
Command Line Interface module for DeFi TVL Tracker.
"""

import argparse
from typing import Dict, Any
from src.protocols import get_supported_protocols
from src.config import get_config

def parse_arguments() -> Dict[str, Any]:
    """
    Parse command line arguments for DeFi TVL Tracker.
    
    Returns:
        Dict[str, Any]: Parsed command line arguments
    """
    # Get supported protocols for CLI choices
    supported_protocols = get_supported_protocols()
    
    parser = argparse.ArgumentParser(
        description="Track Total Value Locked (TVL) across multiple DeFi protocols."
    )
    
    # Create a mutually exclusive group for --protocol and --supported
    group = parser.add_mutually_exclusive_group(required=True)
    
    group.add_argument(
        "--protocol", "-p",
        help="Specify protocol to track TVL",
        choices=list(supported_protocols.keys())
    )
    
    group.add_argument(
        "--supported", "-s",
        action="store_true",
        help="List all supported protocols"
    )
    
    # Additional optional arguments
    parser.add_argument(
        "--provider",
        help="Specify data provider (defaults to protocol's preferred provider)",
        choices=["defillama"],
        # choices=["defillama", "subgraph", "web3", "web"],
        default=None
    )
    
    parser.add_argument(
        "--pool", "-pl",
        help="Filter by specific pool name (e.g., 'S-USDC.e')",
        default=None
    )
    
    parser.add_argument(
        "--chain",
        help="Filter by specific blockchain (e.g., 'sonic', 'ethereum')",
        default=None
    )
    
    parser.add_argument(
        "--output", "-o",
        choices=["table", "json", "csv"],
        default="table",
        help="Output format (default: table)"
    )
    
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Disable caching and fetch fresh data"
    )
    
    return parser.parse_args()