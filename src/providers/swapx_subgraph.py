"""
SwapX Subgraph provider for fetching TVL data from GraphQL endpoints.
This provider is specialized for the ichiVaults used by SwapX.
"""

import requests
from typing import Dict, Any, Optional, List, Union
from src.config import get_config
from src.providers.provider_base import ProviderBase

class SwapxSubgraphProvider(ProviderBase):
    """Provider for SwapX Subgraph GraphQL API."""
    
    def __init__(self, cache_ttl: int = 3600, cache_dir: Optional[str] = None):
        """
        Initialize the SwapX Subgraph provider.
        
        Args:
            cache_ttl: Time-to-live for cached data in seconds (default: 1 hour)
            cache_dir: Directory to store cache files (default: ~/.defi-tvl-cache)
        """
        # Call parent constructor
        super().__init__(cache_ttl, cache_dir)
        
        # Get API configuration
        api_config = get_config("api", "swapx_subgraph", {})
        self.base_url = api_config.get("base_url", "https://gateway.thegraph.com/api/subgraphs/id/Gw1DrPbd1pBNorCWEfyb9i8txJ962qYqqPtuyX6iEH8u")
        self.timeout = api_config.get("timeout", 30)
        
        # Get headers without auth first
        self.headers = api_config.get("headers", {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "DeFi-TVL-Tracker/1.0"
        })
        
        # Get API key from environment variable
        api_key = api_config.get("api_key", "")
        
        
        # Add authorization header if API key exists
        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"
        else:
            print(f"Warning: No API key found in environment variable {api_key}")
            print("Set this variable in your .env file or environment to access the SwapX subgraph")
    
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
        print('FCO:::: query', query)
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
            result = response.json()
            
            # Check for GraphQL errors
            if "errors" in result:
                error_messages = [error.get("message", "Unknown error") for error in result.get("errors", [])]
                if any("auth error" in msg.lower() for msg in error_messages):
                    raise Exception(f"Authentication error: {error_messages[0]}. Make sure to set the GRAPH_API_KEY environment variable.")
                else:
                    raise Exception(f"GraphQL errors: {', '.join(error_messages)}")
                    
            return result
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
    
    def _format_liquidity(self, vault_data: Dict[str, Any]) -> str:
        """
        Format liquidity value to be more readable based on vault data.
        
        Args:
            vault_data: Raw vault data from GraphQL
            
        Returns:
            Formatted liquidity string
        """
        try:
            # Try to find any value that might represent liquidity
            liq_value = None
            for field in ["value", "totalDeposits", "totalSupply"]:
                if field in vault_data and vault_data[field]:
                    liq_value = vault_data[field]
                    break
                    
            # Check shares if available
            if liq_value is None and "vaultShares" in vault_data:
                shares = vault_data["vaultShares"]
                if shares and isinstance(shares, list) and len(shares) > 0:
                    total_value = sum(float(share.get("value", 0)) for share in shares)
                    liq_value = total_value
            
            # If we couldn't find a value, return N/A
            if liq_value is None:
                return "N/A"
                
            liq_float = float(liq_value)
            
            # Format based on size
            if liq_float >= 1e9:
                return f"{liq_float / 1e9:.2f}B"
            elif liq_float >= 1e6:
                return f"{liq_float / 1e6:.2f}M"
            elif liq_float >= 1e3:
                return f"{liq_float / 1e3:.2f}K"
            else:
                return f"{liq_float:.2f}"
        except (ValueError, TypeError):
            return "N/A"
    
    def _calculate_tvl_estimate(self, vault_data: Dict[str, Any]) -> float:
        """
        Calculate a TVL estimate based on available vault data.
        
        Args:
            vault_data: Vault data from GraphQL
            
        Returns:
            TVL estimate in millions USD
        """
        try:
            # Try to use totalSupply as a TVL indicator
            if "totalSupply" in vault_data and vault_data["totalSupply"]:
                total_supply = float(vault_data["totalSupply"])
                
                # Typically totalSupply is in smaller units, convert to millions
                tvl_estimate = total_supply / 1e12  # Adjust divisor as needed
                return tvl_estimate
            
            # Alternative approach: use vaultCount as a very rough proxy
            # This is not ideal but at least provides some data
            if "vaultCount" in vault_data and vault_data["vaultCount"]:
                vault_count = int(vault_data["vaultCount"])
                # Very rough estimate: assume each vault has ~$100K
                return vault_count * 0.1  # 0.1 million = $100K
                
            return 0.0  # Default if no data available
            
        except (ValueError, TypeError):
            return 0.0
    
    def get_protocol_tvl(self, protocol_id: str, token_pair: Optional[str] = None, 
                       chain: Optional[str] = None) -> Dict[str, Any]:
        """
        Get TVL data for SwapX protocol using GraphQL.
        
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
        subgraph_config = protocol_config.get("swapx_subgraph", {})
        entity_type = subgraph_config.get("entity_type", "ichiVaults")
        
        # Create cache key based on protocol and filters
        cache_key = f"swapx_subgraph_{protocol_id}"
        if token_pair:
            cache_key += f"_{token_pair}"
        if chain:
            cache_key += f"_{chain}"
        
        # Try to get data from cache
        vaults_data = self._get_cached_data(cache_key) if self.cache_ttl > 0 else None
        
        # If not in cache or cache disabled, fetch from API
        if not vaults_data:
            # Construct the GraphQL query
            query = self._build_query(protocol_id, entity_type, token_pair)
            
            try:
                # Execute the query
                result = self._execute_query(query)
                
                # Extract vaults data from the result
                if "data" in result and entity_type in result["data"]:
                    vaults_data = result["data"][entity_type]
                else:
                    vaults_data = []
                
                # Save to cache
                if self.cache_ttl > 0:
                    self._save_to_cache(cache_key, vaults_data)
            except Exception as e:
                print(f"Warning: Failed to fetch vaults data from SwapX Subgraph: {str(e)}")
                return {"status": "error", "count": 0, "data": []}
        
        # Format the result in a consistent structure
        result = []
        
        for vault in vaults_data:
            # Get token addresses
            token_a_address = vault.get("tokenA", "")
            token_b_address = vault.get("tokenB", "")
            
            # Create a shortened address representation for the token names
            # Since we don't have symbol information in the schema
            token_a_short = token_a_address[-6:] if token_a_address else "Unknown"
            token_b_short = token_b_address[-6:] if token_b_address else "Unknown"
            
            # Create pool name from shortened addresses
            pool_name = f"Token-{token_a_short}/Token-{token_b_short}"
            
            # Calculate TVL estimate
            tvl_value = self._calculate_tvl_estimate(vault)
            
            # Create a liquidity display value
            if "totalSupply" in vault and vault["totalSupply"]:
                try:
                    supply = float(vault["totalSupply"])
                    if supply >= 1e9:
                        liquidity = f"{supply / 1e9:.2f}B"
                    elif supply >= 1e6:
                        liquidity = f"{supply / 1e6:.2f}M"
                    elif supply >= 1e3:
                        liquidity = f"{supply / 1e3:.2f}K"
                    else:
                        liquidity = f"{supply:.2f}"
                except (ValueError, TypeError):
                    liquidity = "N/A"
            else:
                liquidity = "N/A"
            
            # Filter by token pair if specified
            if token_pair:
                # Skip if doesn't match the token pair pattern
                tokens = token_pair.split("/") if "/" in token_pair else [token_pair]
                
                # Simple string matching on token addresses
                # This is a basic approach since we don't have symbol info
                matched = False
                if len(tokens) == 2:
                    # Check if both tokens match
                    if (tokens[0].lower() in token_a_address.lower() and 
                        tokens[1].lower() in token_b_address.lower()):
                        matched = True
                else:
                    # Check if single token matches either address
                    if (token_pair.lower() in token_a_address.lower() or 
                        token_pair.lower() in token_b_address.lower()):
                        matched = True
                        
                if not matched:
                    continue
            
            # Add formatted vault data
            result.append({
                "protocol": protocol_id,
                "protocol_slug": protocol_id,
                "chain": chain or "sonic",  # Default to sonic network
                "pool_name": pool_name,
                "pool_id": vault.get("id", "Unknown"),
                "tvl": tvl_value,
                "liquidity": liquidity,
                "fee_tier": f"Amp: {vault.get('ampFactor', 'N/A')}",  # Use ampFactor as fee info
                "provider": "SwapxSubgraph",
                "raw_data": vault  # Include the raw data from GraphQL
            })
        
        return {
            "status": "success" if result else "no_data",
            "count": len(result),
            "data": result
        }
    
    def _build_query(self, protocol_id: str, entity_type: str, token_pair: Optional[str] = None) -> str:
        """
        Build a GraphQL query for fetching vaults data.
        
        Args:
            protocol_id: Protocol ID
            entity_type: Entity type to query (e.g., ichiVaults)
            token_pair: Optional token pair to filter by
            
        Returns:
            GraphQL query string
        """
        # Get protocol configuration for default filters
        protocol_config = self._get_protocol_config(protocol_id)
        subgraph_config = protocol_config.get("swapx_subgraph", {})
        
        default_filters = subgraph_config.get("default_filters", {})
        
        # Build filter criteria
        where_clause = ""
        
        # Since the schema uses addresses instead of symbols, we can't filter by token names
        # We'll need to fetch all and filter client-side
        where_clause = ""
        
        # Build some default filters if specified in config
        protocol_config = self._get_protocol_config(protocol_id)
        subgraph_config = protocol_config.get("swapx_subgraph", {})
        default_filters = subgraph_config.get("default_filters", {})
        
        if default_filters:
            filter_parts = []
            for key, value in default_filters.items():
                if isinstance(value, str):
                    filter_parts.append(f'{key}: "{value}"')
                else:
                    filter_parts.append(f'{key}: {value}')
            
            if filter_parts:
                where_clause = 'where: { ' + ', '.join(filter_parts) + ' }'
        else:
            # Use default filter from configuration if available
            if default_filters:
                filter_parts = []
                for key, value in default_filters.items():
                    if isinstance(value, str):
                        filter_parts.append(f'{key}: "{value}"')
                    else:
                        filter_parts.append(f'{key}: {value}')
                
                where_clause = 'where: { ' + ', '.join(filter_parts) + ' }'
            else:
                # Use an empty where clause to get all vaults, but limit to a reasonable number
                where_clause = ""
        
        # Construct a more comprehensive GraphQL query to get TVL-related data
        query = f"""
        query {{
          {entity_type}(first: 100, orderDirection: desc {where_clause}) {{
            id
            tokenA
            tokenB
            deployer
            vaultCount
            totalSupply
            ampFactor
            twapPeriod
          }}
        }}
        """
        
        return query
    
    def format_output(self, tvl_data: Union[Dict[str, Any], List[Dict[str, Any]]], 
                     output_format: str = "table") -> str:
        """
        Format the TVL data for output, including SwapX-specific fields.
        
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
            
            # Write header
            writer.writerow([
                "Protocol", "Chain", "Pool Name", "TVL (USD)", 
                "Liquidity", "Fee Tier", "Provider"
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
                
                writer.writerow([
                    item.get("protocol", "N/A"),
                    item.get("chain", "N/A"),
                    item.get("pool_name", "N/A"),
                    tvl_formatted,
                    item.get("liquidity", "N/A"),
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
            
            table_data.append([
                item.get("protocol", "N/A"),
                item.get("chain", "N/A"),
                item.get("pool_name", "N/A"),
                tvl_formatted,
                item.get("liquidity", "N/A"),
                item.get("fee_tier", "N/A"),
                item.get("provider", "N/A")
            ])
        
        if not table_data:
            return "No matching TVL data found."
            
        return tabulate(
            table_data,
            headers=["Protocol", "Chain", "Pool Name", "TVL (USD)", 
                    "Liquidity", "Fee Tier", "Provider"],
            tablefmt="pretty"
        )