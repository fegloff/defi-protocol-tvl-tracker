"""
Formatter module for displaying TVL data in different formats.
"""

import json
import csv
import io
from typing import Dict, Any, List, Union

try:
    from tabulate import tabulate
except ImportError:
    # Fallback for when tabulate is not available
    def tabulate(data, headers, tablefmt):
        output = []
        # Add headers
        output.append("  ".join(headers))
        output.append("-" * (sum(len(h) for h in headers) + 2 * (len(headers) - 1)))
        
        # Add data rows
        for row in data:
            output.append("  ".join(str(cell) for cell in row))
            
        return "\n".join(output)

def format_tvl_output(tvl_data: Union[Dict[str, Any], List[Dict[str, Any]]], output_format: str = "table") -> str:
    """
    Format TVL data for display.
    
    Args:
        tvl_data: TVL data to format (either a dict or list of dicts)
        output_format: Output format (table, json, csv)
        
    Returns:
        Formatted output string
    """
    # Convert the data into a standardized format
    formatted_data = []
    
    # Handle the new API response format with status and data fields
    if isinstance(tvl_data, dict) and "status" in tvl_data and "data" in tvl_data:
        # This is the new format from pools endpoint
        if tvl_data["status"] == "success":
            formatted_data = tvl_data["data"]
    # Handle the old format (dictionary of pool data)
    elif isinstance(tvl_data, dict):
        # This is the old format with pool_id as keys
        for pool_id, pool_data in tvl_data.items():
            pool_entry = {
                "protocol": pool_data.get("protocol", "N/A"),
                "chain": pool_data.get("chain", "N/A"),
                "pool_name": pool_data.get("token_pair", "N/A"),
                "tvl": pool_data.get("tvl_usd", 0) / 1e6 if isinstance(pool_data.get("tvl_usd"), (int, float)) else 0,
                "apy": pool_data.get("apy", 0),
                "provider": pool_data.get("provider", "N/A"),
                "url": pool_data.get("url", "")
            }
            formatted_data.append(pool_entry)
    # Handle list format
    elif isinstance(tvl_data, list):
        formatted_data = tvl_data
    
    # Generate output in the requested format
    if output_format == "json":
        return json.dumps(formatted_data, indent=2)
    
    elif output_format == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header (without Pool ID)
        writer.writerow(["Protocol", "Chain", "Pool Name", "TVL (USD)", "APY", "Provider"])
        
        # Write data
        for pool in formatted_data:
            tvl_value = pool.get('tvl', 0)
            apy_value = pool.get('apy', 0)
            
            # Format TVL with appropriate scale and precision
            if tvl_value >= 1000:
                tvl_formatted = f"${tvl_value:.2f}M"  # Millions with 2 decimal places
            elif tvl_value >= 1:
                tvl_formatted = f"${tvl_value:.4f}M"  # Millions with 4 decimal places for smaller values
            else:
                tvl_formatted = f"${tvl_value * 1000:.2f}K"  # Convert to thousands for very small values
            
            # Format APY with appropriate precision
            if apy_value is None:
                apy_formatted = "N/A"
            elif apy_value < 0.01:
                apy_formatted = f"{apy_value:.5f}%"  # 5 decimal places for very small APY
            elif apy_value < 0.1:
                apy_formatted = f"{apy_value:.4f}%"  # 4 decimal places for small APY
            elif apy_value < 1:
                apy_formatted = f"{apy_value:.3f}%"  # 3 decimal places for medium APY
            else:
                apy_formatted = f"{apy_value:.2f}%"  # 2 decimal places for large APY
            
            writer.writerow([
                pool.get("protocol", "N/A"),
                pool.get("chain", "N/A"),
                pool.get("pool_name", "N/A"),
                tvl_formatted,
                apy_formatted,
                pool.get("provider", "N/A")
            ])
        
        return output.getvalue()
    
    else:  # Default to table format
        table_data = []
        
        for pool in formatted_data:
            tvl_value = pool.get('tvl', 0)
            apy_value = pool.get('apy', 0)
            
            # Format TVL with appropriate scale and precision
            if tvl_value >= 1000:
                tvl_formatted = f"${tvl_value:.2f}M"  # Millions with 2 decimal places
            elif tvl_value >= 1:
                tvl_formatted = f"${tvl_value:.4f}M"  # Millions with 4 decimal places for smaller values
            else:
                tvl_formatted = f"${tvl_value * 1000:.2f}K"  # Convert to thousands for very small values
            
            # Format APY with appropriate precision
            if apy_value is None:
                apy_formatted = "N/A"
            elif apy_value == 0:
                apy_formatted = f"{apy_value:.2f}%"
            elif apy_value < 0.01:
                apy_formatted = f"{apy_value:.5f}%"  # 5 decimal places for very small APY
            elif apy_value < 0.1:
                apy_formatted = f"{apy_value:.4f}%"  # 4 decimal places for small APY
            elif apy_value < 1:
                apy_formatted = f"{apy_value:.3f}%"  # 3 decimal places for medium APY
            else:
                apy_formatted = f"{apy_value:.2f}%"  # 2 decimal places for large APY
            
            table_data.append([
                pool.get("protocol", "N/A"),
                pool.get("chain", "N/A"),
                pool.get("pool_name", "N/A"),
                tvl_formatted,
                apy_formatted,
                pool.get("provider", "N/A")
            ])
        
        if not table_data:
            return "No matching TVL data found."
            
        return tabulate(
            table_data,
            headers=["Protocol", "Chain", "Pool Name", "TVL (USD)", "APY", "Provider"],
            tablefmt="pretty"
        )