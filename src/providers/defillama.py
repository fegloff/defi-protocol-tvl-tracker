"""
DefiLlama API provider for fetching TVL data with local file caching.
"""

import requests
from typing import Dict, Any, Optional, List, Union
from urllib.parse import urljoin
from src.config import get_config
from src.providers.provider_base import ProviderBase

class DefiLlamaProvider(ProviderBase):
    """Provider for DefiLlama API with local file caching for pools data."""
    
    def __init__(self, cache_ttl: int = 3600, cache_dir: Optional[str] = None):
        """
        Initialize the DefiLlama API provider.
        
        Args:
            cache_ttl: Time-to-live for cached data in seconds (default: 1 hour)
            cache_dir: Directory to store cache files (default: ~/.defi-tvl-cache)
        """
        # Call parent constructor first
        super().__init__(cache_ttl, cache_dir)
        
        # Get API configuration
        defillama_config = get_config("api", "defillama", {})
        self.base_url = defillama_config.get("base_url", "https://api.llama.fi/")
        self.yields_url = "https://yields.llama.fi/"
        self.timeout = defillama_config.get("timeout", 30)
        
        self.headers = {
            "Accept": "application/json",
            "User-Agent": "DeFi-TVL-Tracker/1.0"
        }
    
    def _make_request(self, base: str, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make a request to the DefiLlama API.
        
        Args:
            base: Base URL to use
            endpoint: API endpoint
            params: Optional query parameters
            
        Returns:
            JSON response from the API
        
        Raises:
            Exception: If the API request fails
        """
        url = urljoin(base, endpoint)
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=self.timeout)
            response.raise_for_status()  # Raise an exception for 4XX/5XX responses
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"DefiLlama API request failed: {str(e)}")
    
    def _get_protocol_config(self, protocol_id: str) -> Dict[str, Any]:
        """
        Get protocol configuration.
        
        Args:
            protocol_id: Protocol ID
            
        Returns:
            Protocol configuration
        """
        protocol_config = get_config("protocol", protocol_id, {})
        # Return empty dict if no config found
        if not protocol_config:
            print(f"Warning: No configuration found for protocol '{protocol_id}'")
            return {}
            
        return protocol_config
    
    def get_protocol_tvl(self, protocol_id: str, token_pair: Optional[str] = None, 
                        chain: Optional[str] = None) -> Dict[str, Any]:
        """
        Get TVL data for a specific protocol.
        
        Args:
            protocol_id: Protocol ID
            token_pair: Optional token pair to filter by
            chain: Optional chain to filter by
            
        Returns:
            TVL data for the protocol
        """
        # Get protocol configuration
        protocol_config = self._get_protocol_config(protocol_id)
        # Get DefiLlama specific identifiers
        defillama_slug = protocol_config.get("defillama_slug", protocol_id)
        defillama_project = protocol_config.get("defillama_project", defillama_slug)
        # Try to get pools data first
        pools_data = self.get_pools(defillama_project, chain, token_pair)
        
        # If we got pools data, return it
        if pools_data.get("status") == "success" and pools_data.get("data"):
            return pools_data
        
        # Fallback to protocol-level TVL data
        result = {
            "status": "success",
            "count": 0,
            "data": []
        }
        
        try:
            # Get protocol info
            protocol_info = self.get_protocol_info(defillama_slug)
            
            # Get chain-specific TVL if chain is specified
            tvl_value = 0
            if chain:
                chain_key = chain.capitalize()  # DefiLlama uses capitalized chain names
                tvl_value = protocol_info.get("currentChainTvls", {}).get(chain_key, 0)
            else:
                # Use total TVL if no chain specified
                tvl_value = protocol_info.get("currentChainTvls", {}).get("Sonic", 0)
            
            # Add a single entry with the overall TVL
            pool_name = token_pair or "All Pools"
            
            # If we're falling back to protocol-level data, we don't have poolMeta
            # but we should indicate this is aggregate data
            if not token_pair:
                pool_name = "All Pools (Aggregate)"
            
            result["data"].append({
                "protocol": defillama_project,
                "protocol_slug": defillama_slug,
                "chain": chain or "All",
                "pool_name": pool_name,
                "tvl": tvl_value / 1e6,  # Convert to millions USD
                "apy": 0,  # No APY data available at protocol level
                "provider": "DefiLlama"
            })
            
            result["count"] = 1
            
        except Exception as e:
            print(f"Warning: Failed to get protocol TVL data: {str(e)}")
            result["status"] = "error"
            
        return result
    
    def get_pools(self, protocol: Optional[str] = None, chain: Optional[str] = None, 
                 pool_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get TVL data for pools with optional filtering by protocol, chain, and pool name.
        
        Args:
            protocol: Optional protocol name to filter by
            chain: Optional chain name to filter by
            pool_name: Optional pool name to filter by
            
        Returns:
            Filtered pools data with consistent format
        """
        # Define cache key based on endpoint
        cache_key = "pools"
        
        # Try to get data from cache
        pools_data = self._get_cached_data(cache_key) if self.cache_ttl > 0 else None
        
        # If not in cache or cache disabled, fetch from API
        if not pools_data:
            try:
                pools_data = self._make_request(self.yields_url, "pools")
                
                # Save to cache
                if self.cache_ttl > 0:
                    self._save_to_cache(cache_key, pools_data)
            except Exception as e:
                print(f"Warning: Failed to fetch pools data: {str(e)}")
                # Return empty result on error
                return {"status": "error", "count": 0, "data": []}
        
        # Start with all pools
        filtered_data = pools_data.get("data", [])
        
        # Apply filters sequentially if provided
        if protocol:
            # Filter by project name
            filtered_data = [pool for pool in filtered_data if pool.get("project", "").lower() == protocol.lower()]
        
        if chain:
            # Filter by chain
            filtered_data = [pool for pool in filtered_data if pool.get("chain", "").lower() == chain.lower()]
        
        if pool_name:
            # Filter by pool name (substring match)
            filtered_data = [pool for pool in filtered_data if 
                           (pool_name.lower() in (pool.get("symbol", "") or "").lower()) or
                           (pool_name.lower() in (pool.get("poolMeta", "") or "").lower())]
        
        # Format the result in a consistent structure
        result = []
        for pool in filtered_data:
            try:
                tvl_value = pool.get("tvlUsd", 0) / 1e6  # Convert to millions USD
            except (TypeError, ValueError):
                tvl_value = 0
                
            try:
                apy_value = pool.get("apy", 0)
            except (TypeError, ValueError):
                apy_value = 0
                
            # Create a more descriptive pool name that includes the poolMeta if available
            pool_name = pool.get("symbol", "Unknown")
            pool_meta = pool.get("poolMeta")
            
            if pool_meta:
                pool_name = f"{pool_name}-{pool_meta}"
            
            result.append({
                "protocol": pool.get("project", "Unknown"),
                "protocol_slug": protocol,  # Use the provided protocol as slug
                "chain": pool.get("chain", "Unknown"),
                "pool_name": pool_name,
                "pool_id": pool.get("pool", "Unknown"),
                "tvl": tvl_value,
                "apy": apy_value,
                "provider": "DefiLlama"
            })
        
        return {
            "status": "success" if result else "no_data",
            "count": len(result),
            "data": result
        }
    
    def get_protocol_info(self, protocol_slug: str) -> Dict[str, Any]:
        """
        Get detailed information about a protocol.
        
        Args:
            protocol_slug: Protocol slug as used in DefiLlama
            
        Returns:
            Protocol information
        """
        cache_key = f"protocol_info_{protocol_slug}"
        
        # Try to get data from cache
        protocol_info = self._get_cached_data(cache_key) if self.cache_ttl > 0 else None
        
        # If not in cache or cache disabled, fetch from API
        if not protocol_info:
            endpoint = f"protocol/{protocol_slug}"
            protocol_info = self._make_request(self.base_url, endpoint)
            
            # Save to cache
            if self.cache_ttl > 0:
                self._save_to_cache(cache_key, protocol_info)
                
        return protocol_info
    
    def format_output(self, tvl_data: Union[Dict[str, Any], List[Dict[str, Any]]], 
                     output_format: str = "table") -> str:
        """
        Format TVL data for display.
        
        Args:
            tvl_data: TVL data to format (either a dict or list of dicts)
            output_format: Output format (table, json, csv)
            
        Returns:
            Formatted output string
        """
        import json
        import csv
        import io
        
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