#!/usr/bin/env python3
"""
DeFi TVL Tracker - Command-line tool to track Total Value Locked (TVL) across multiple DeFi protocols.

Usage:
    python tracker.py --protocol silo
    python tracker.py --supported
    python tracker.py --protocol all
    python tracker.py --protocol silo --chain sonic
    python tracker.py --protocol silo --token-pair USDC.E
    python tracker.py --protocol silo --pool-id <pool_id>
"""

import sys
from src.cli import parse_arguments
from src.protocols import get_protocol_instance, get_supported_protocols
from src.config import get_config

def display_supported_protocols():
    """Display the list of supported protocols."""
    protocols = get_supported_protocols()
    print("Supported DeFi Protocols:")
    for protocol, providers in protocols.items():
        # Get additional information from config if available
        # protocol_config = get_config("protocol", protocol, {})
        
        print(f"  - {protocol} (Providers: {', '.join(providers)})")
    
def merge_tvl_data(data_list):
    """
    Merge multiple TVL data responses into a single result.
    
    Args:
        data_list: List of TVL data responses
        
    Returns:
        Merged TVL data
    """
    merged_result = {
        "status": "success",
        "count": 0,
        "data": []
    }
    
    # Get all protocol configurations
    protocol_configs = get_config("protocol", "", {})
    
    for data in data_list:
        # Handle the new format with status and data fields
        if isinstance(data, dict) and "status" in data and "data" in data:
            if data["status"] == "success" and data["data"]:
                merged_result["data"].extend(data["data"])
                merged_result["count"] += len(data["data"])
        # Handle the old format (dictionary of pool data)
        elif isinstance(data, dict):
            for pool_id, pool_data in data.items():
                protocol_slug = None
                
                # Find the correct protocol config
                for proto_key, proto_config in protocol_configs.items():
                    if proto_config.get("defillama_project", "").lower() == pool_data.get("protocol", "").lower():
                        protocol_slug = proto_config.get("defillama_slug", "")
                        break
                
                merged_result["data"].append({
                    "protocol": pool_data.get("protocol", "N/A"),
                    "protocol_slug": protocol_slug,
                    "chain": pool_data.get("chain", "N/A"),
                    "pool_name": pool_data.get("token_pair", "N/A"),
                    "tvl": pool_data.get("tvl_usd", 0) / 1e6 if isinstance(pool_data.get("tvl_usd"), (int, float)) else 0,
                    "apy": pool_data.get("apy", 0),
                    "provider": pool_data.get("provider", "N/A")
                })
                merged_result["count"] += 1
    
    return merged_result

def main():
    """Main function to run the TVL tracker."""
    args = parse_arguments()
    
    if args.supported:
        display_supported_protocols()
        return 0
    
    # Get TVL data for the specified protocol(s)
    all_tvl_data = []
    
    try:
        # Get all configured protocols
        protocol_configs = get_config("protocol", "", {})
        # Check if the protocol is in our config
        if args.protocol not in protocol_configs:
            print(f"Error: Protocol '{args.protocol}' is not configured. Use --supported to see available protocols.")
            return 1
            
        # Get data for a specific protocol
        try:
            protocol = get_protocol_instance(args.protocol, args.provider)
            tvl_data = protocol.get_tvl(args.pool, args.chain)
            print('FCO::::: tvl_data', args.pool, args.chain, tvl_data)
            all_tvl_data.append(tvl_data)
        except Exception as e:
            print(f"Error fetching TVL data for {args.protocol}: {str(e)}")
        
        # Merge all results
        merged_result = merge_tvl_data(all_tvl_data)
        
        # Format and display the TVL data using the protocol's format_output method
        if merged_result["data"]:
            if protocol:
                formatted_output = protocol.format_output(merged_result, output_format=args.output)
                print(formatted_output)
            else:
                # This should never happen since we check if the protocol exists above
                print("No protocol instance available to format output.")
        else:
            print("No TVL data available.")
        
        return 0
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())