"""
Command Line Interface module for DeFi TVL Tracker.
"""

import argparse
from typing import Dict, Any
from src.protocols import get_supported_protocols

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
        help="Specify protocol to track TVL (or 'all' for all supported protocols)",
        choices=list(supported_protocols.keys()) + ["all"]
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
        choices=["defillama", "subgraph", "web3", "web"],
        default=None
    )
    
    parser.add_argument(
        "--token-pair",
        help="Filter by specific token pair (e.g., 'S-USDC.e')",
        default=None
    )
    
    parser.add_argument(
        "--output", "-o",
        choices=["table", "json", "csv"],
        default="table",
        help="Output format (default: table)"
    )
    
    return parser.parse_args()