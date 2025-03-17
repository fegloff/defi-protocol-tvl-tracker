"""
Formatter module for displaying TVL data in different formats.
"""

import json
import csv
import io
from typing import Dict, Any
from tabulate import tabulate

def format_tvl_output(tvl_data: Dict[str, Any], output_format: str = "table") -> str:
    """
    Format TVL data for display.
    
    Args:
        tvl_data: TVL data to format
        output_format: Output format (table, json, csv)
        
    Returns:
        Formatted output string
    """
    if output_format == "json":
        return json.dumps(tvl_data, indent=2)
    
    elif output_format == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(["Pool ID", "Protocol", "Token Pair", "TVL", "Provider"])
        
        # Write data
        for pool_id, data in tvl_data.items():
            writer.writerow([
                pool_id,
                data.get("protocol", "N/A"),
                data.get("token_pair", "N/A"),
                data.get("tvl", "N/A"),
                data.get("provider", "N/A")
            ])
        
        return output.getvalue()
    
    else:  # Default to table format
        table_data = []
        for pool_id, data in tvl_data.items():
            table_data.append([
                pool_id,
                data.get("protocol", "N/A"),
                data.get("token_pair", "N/A"),
                data.get("tvl", "N/A"),
                data.get("provider", "N/A")
            ])
        
        return tabulate(
            table_data,
            headers=["Pool ID", "Protocol", "Token Pair", "TVL", "Provider"],
            tablefmt="pretty"
        )