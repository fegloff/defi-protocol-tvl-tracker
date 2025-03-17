#!/usr/bin/env python3
"""
DeFi TVL Tracker - Command-line tool to track Total Value Locked (TVL) across multiple DeFi protocols.

Usage:
    python tracker.py --protocol silo
    python tracker.py --supported
    python tracker.py --protocol all
"""

import sys
from src.cli import parse_arguments
from src.protocols import get_protocol_instance, get_supported_protocols
from src.utils.formatter import format_tvl_output

def display_supported_protocols():
    """Display the list of supported protocols."""
    protocols = get_supported_protocols()
    print("Supported DeFi Protocols:")
    for protocol, providers in protocols.items():
        print(f"  - {protocol} (Providers: {', '.join(providers)})")
    print("\nUsage: python tracker.py --protocol <protocol_name> [--provider <provider_name>]")

def main():
    """Main function to run the TVL tracker."""
    args = parse_arguments()
    
    if args.supported:
        display_supported_protocols()
        return
    
    # Get TVL data for the specified protocol(s)
    if args.protocol == "all":
        # Get data for all protocols
        tvl_data = {}
        supported_protocols = get_supported_protocols()
        for protocol_name in supported_protocols:
            try:
                protocol = get_protocol_instance(protocol_name, args.provider)
                protocol_data = protocol.get_tvl(args.token_pair)
                tvl_data.update(protocol_data)
            except Exception as e:
                print(f"Error fetching TVL data for {protocol_name}: {str(e)}")
    else:
        # Get data for a specific protocol
        try:
            protocol = get_protocol_instance(args.protocol, args.provider)
            tvl_data = protocol.get_tvl(args.token_pair)
        except Exception as e:
            print(f"Error fetching TVL data for {args.protocol}: {str(e)}")
            tvl_data = {}
    
    # Format and display the TVL data
    if tvl_data:
        # Format the output using the formatter module
        formatted_output = format_tvl_output(tvl_data, output_format=args.output)
        print(formatted_output)
    else:
        print("No TVL data available.")

if __name__ == "__main__":
    main()