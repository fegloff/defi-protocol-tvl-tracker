"""
Kingdom Subgraph provider for fetching TVL data from GraphQL endpoints.
"""

import requests
from typing import Dict, Any, Optional, List, Union
from src.config import get_config
from src.providers.provider_base import ProviderBase

class KingdomSubgraphProvider(ProviderBase):
    """Provider for Kingdom Subgraph GraphQL API."""
    
    def __init__(self, cache_ttl: int = 3600, cache_dir: Optional[str] = None):
        """
        Initialize the Kingdom Subgraph provider.
        
        Args:
            cache_ttl: Time-to-live for cached data in seconds (default: 1 hour)
            cache_dir: Directory to store cache files (default: ~/.defi-tvl-cache)
        """
        # Call parent constructor
        super().__init__(cache_ttl, cache_dir)
        
        # Get API configuration
        api_config = get_config("api", "kingdom_subgraph", {})
        self.base_url = api_config.get("base_url", "https://sonic.kingdomsubgraph.com/subgraphs/name/exp")
        self.timeout = api_config.get("timeout", 30)
        self.headers = api_config.get("headers", {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "DeFi-TVL-Tracker/1.0"
        })
    
    def _execute_query(self, query: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a GraphQL query.
        
        Args:
            query: GraphQL query string
            variables: Optional query variables
            
        Returns:
            Query result
            
        Raises:
            Exception: If the query fails
        """
        payload = {
            "query": query
        }
        
        if variables:
            payload["variables"] = variables
            
        try:
            response = requests.post(
                self.base_url,
                json=payload,
                headers=self.headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"GraphQL query failed: {str(e)}")
    
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
    
    def _format_liquidity(self, liquidity: str) -> str:
        """
        Format liquidity value to be more readable.
        
        Args:
            liquidity: Raw liquidity value as string
            
        Returns:
            Formatted liquidity string
        """
        try:
            # Convert to float
            liq_float = float(liquidity)
            
            # Format based on size
            if liq_float >= 1e18:
                return f"{liq_float / 1e18:.2f}B"
            elif liq_float >= 1e15:
                return f"{liq_float / 1e15:.2f}M"
            elif liq_float >= 1e12:
                return f"{liq_float / 1e12:.2f}K"
            else:
                return f"{liq_float:.2f}"
        except (ValueError, TypeError):
            return liquidity
    
    def get_protocol_tvl(self, protocol_id: str, token_pair: Optional[str] = None, 
                       chain: Optional[str] = None) -> Dict[str, Any]:
        """
        Get TVL data for a specific protocol using GraphQL.
        
        Args:
            protocol_id: Protocol ID 
            token_pair: Optional token pair to filter by
            chain: Optional chain to filter by (not used in the GraphQL query directly)
            
        Returns:
            TVL data for the protocol
        """
        # Get protocol configuration
        protocol_config = self._get_protocol_config(protocol_id)
        
        # Get subgraph-specific configuration
        subgraph_config = protocol_config.get("kingdom_subgraph", {})
        entity_type = subgraph_config.get("entity_type", "clPools")
        field_mapping = subgraph_config.get("field_mapping", {
            "tvl": "totalValueLockedUSD",
            "volume": "volumeUSD",
            "name": "symbol"
        })
        
        # Create cache key based on protocol and filters
        cache_key = f"kingdom_subgraph_{protocol_id}"
        if token_pair:
            cache_key += f"_{token_pair}"
        if chain:
            cache_key += f"_{chain}"
        
        # Try to get data from cache
        pools_data = self._get_cached_data(cache_key) if self.cache_ttl > 0 else None
        
        # If not in cache or cache disabled, fetch from API
        if not pools_data:
            # Construct the GraphQL query
            query = self._build_query(protocol_id, entity_type, token_pair)
            
            try:
                # Execute the query
                result = self._execute_query(query)
                
                # Extract pools data from the result
                if "data" in result and entity_type in result["data"]:
                    pools_data = result["data"][entity_type]
                else:
                    pools_data = []
                
                # Save to cache
                if self.cache_ttl > 0:
                    self._save_to_cache(cache_key, pools_data)
            except Exception as e:
                print(f"Warning: Failed to fetch pools data from Kingdom Subgraph: {str(e)}")
                return {"status": "error", "count": 0, "data": []}
        
        # Format the result in a consistent structure
        result = []
        
        for pool in pools_data:
            # Get TVL value using field mapping
            tvl_field = field_mapping.get("tvl", "totalValueLockedUSD")
            try:
                tvl_value = float(pool.get(tvl_field, 0)) / 1e6  # Convert to millions USD
            except (TypeError, ValueError):
                tvl_value = 0
                
            # Process additional fields using field mapping
            liquidity = self._format_liquidity(pool.get("liquidity", "N/A"))
            
            volume_field = field_mapping.get("volume", "volumeUSD")
            try:
                volume_usd = float(pool.get(volume_field, 0)) / 1e6 if pool.get(volume_field) else 0
            except (TypeError, ValueError):
                volume_usd = 0
                
            fee_tier = pool.get("feeTier", "N/A")
                
            # Determine pool name using field mapping
            name_field = field_mapping.get("name", "symbol")
            pool_name = pool.get(name_field, pool.get("id", "Unknown"))
            
            # Add formatted pool data with raw data included
            result.append({
                "protocol": protocol_id,
                "protocol_slug": protocol_id,
                "chain": chain or "sonic",  # Default to sonic network
                "pool_name": pool_name,
                "pool_id": pool.get("id", "Unknown"),
                "tvl": tvl_value,
                "liquidity": liquidity,
                "volume_usd": volume_usd,
                "fee_tier": fee_tier,
                "provider": "KingdomSubgraph",
                "raw_data": pool  # Include the raw data from GraphQL
            })
        
        return {
            "status": "success" if result else "no_data",
            "count": len(result),
            "data": result
        }
    
    def _build_query(self, protocol_id: str, entity_type: str, token_pair: Optional[str] = None) -> str:
        """
        Build a GraphQL query for fetching pools data.
        
        Args:
            protocol_id: Protocol ID
            entity_type: Entity type to query (e.g., clPools)
            token_pair: Optional token pair to filter by
            
        Returns:
            GraphQL query string
        """
        # Get protocol configuration for default filters
        protocol_config = self._get_protocol_config(protocol_id)
        subgraph_config = protocol_config.get("kingdom_subgraph", {})
        default_filters = subgraph_config.get("default_filters", {"symbol_contains": "USD"})
        
        # Build filter criteria
        where_clause = ""
        
        if token_pair:
            where_clause = f'where: {{ symbol_contains_nocase: "{token_pair}" }}'
        else:
            # Use default filter from configuration
            filter_parts = []
            for key, value in default_filters.items():
                if isinstance(value, str):
                    filter_parts.append(f'{key}_nocase: "{value}"')
                else:
                    filter_parts.append(f'{key}: {value}')
            
            where_clause = 'where: { ' + ', '.join(filter_parts) + ' }'
        
        # Construct the GraphQL query with proper formatting
        query = f"""
        query {{
          {entity_type}(orderBy: totalValueLockedUSD, orderDirection: desc, {where_clause}) {{
            id
            liquidity
            totalValueLockedUSD
            tick
            symbol
            volumeUSD
            feeTier
          }}
        }}
        """
        
        return query
    
    def format_output(self, tvl_data: Union[Dict[str, Any], List[Dict[str, Any]]], 
                     output_format: str = "table") -> str:
        """
        Format the TVL data for output, including KingdomSubgraph-specific fields.
        
        Args:
            tvl_data: TVL data to format
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
        
        # Format based on the requested output type
        if output_format == "json":
            return json.dumps(tvl_data, indent=2)
        
        # Get the data list from the response
        data_list = []
        if isinstance(tvl_data, dict) and "data" in tvl_data:
            data_list = tvl_data["data"]
        elif isinstance(tvl_data, list):
            data_list = tvl_data
        
        # For CSV output
        if output_format == "csv":
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header with KingdomSubgraph-specific fields (removed Pool ID)
            writer.writerow([
                "Protocol", "Chain", "Pool Name", "TVL (USD)", 
                "Liquidity", "Volume (USD)", "Fee Tier", "Provider"
            ])
            
            # Write data rows
            for item in data_list:
                # Format TVL
                tvl_value = item.get('tvl', 0)
                if tvl_value >= 1000:
                    tvl_formatted = f"${tvl_value:.2f}M"
                elif tvl_value >= 1:
                    tvl_formatted = f"${tvl_value:.4f}M"
                else:
                    tvl_formatted = f"${tvl_value * 1000:.2f}K"
                
                # Format volume
                volume_usd = item.get('volume_usd', 0)
                if volume_usd >= 1000:
                    volume_formatted = f"${volume_usd:.2f}M"
                elif volume_usd >= 1:
                    volume_formatted = f"${volume_usd:.4f}M"
                else:
                    volume_formatted = f"${volume_usd * 1000:.2f}K" if volume_usd > 0 else "N/A"
                
                writer.writerow([
                    item.get("protocol", "N/A"),
                    item.get("chain", "N/A"),
                    item.get("pool_name", "N/A"),
                    tvl_formatted,
                    item.get("liquidity", "N/A"),
                    volume_formatted,
                    item.get("fee_tier", "N/A"),
                    item.get("provider", "N/A")
                ])
            
            return output.getvalue()
            
        # Default to table format
        table_data = []
        for item in data_list:
            # Format TVL
            tvl_value = item.get('tvl', 0)
            if tvl_value >= 1000:
                tvl_formatted = f"${tvl_value:.2f}M"
            elif tvl_value >= 1:
                tvl_formatted = f"${tvl_value:.4f}M"
            else:
                tvl_formatted = f"${tvl_value * 1000:.2f}K"
            
            # Format volume
            volume_usd = item.get('volume_usd', 0)
            if volume_usd >= 1000:
                volume_formatted = f"${volume_usd:.2f}M"
            elif volume_usd >= 1:
                volume_formatted = f"${volume_usd:.4f}M"
            else:
                volume_formatted = f"${volume_usd * 1000:.2f}K" if volume_usd > 0 else "N/A"
            
            table_data.append([
                item.get("protocol", "N/A"),
                item.get("chain", "N/A"),
                item.get("pool_name", "N/A"),
                tvl_formatted,
                item.get("liquidity", "N/A"),
                volume_formatted,
                item.get("fee_tier", "N/A"),
                item.get("provider", "N/A")
            ])
        
        if not table_data:
            return "No matching TVL data found."
            
        return tabulate(
            table_data,
            headers=["Protocol", "Chain", "Pool Name", "TVL (USD)", 
                    "Liquidity", "Volume (USD)", "Fee Tier", "Provider"],
            tablefmt="pretty"
        )