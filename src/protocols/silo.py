"""
Silo Finance protocol implementation.
"""

from typing import Dict, Any, Optional
from .protocol_base import ProtocolBase

class SiloProtocol(ProtocolBase):
    """Implementation for Silo Finance protocol."""
    
    # Define default and supported providers
    DEFAULT_PROVIDER = "defillama"
    SUPPORTED_PROVIDERS = ["defillama", "web"]
    
    def __init__(self, provider_name: Optional[str] = None):
        """
        Initialize the Silo Finance protocol.
        
        Args:
            provider_name: Optional provider name
        """
        super().__init__(provider_name)
        
        # Protocol-specific configuration
        self.protocol_slug = "silo-finance"  # DefiLlama slug
        self.web_url = "https://v2.silo.finance"
        
    def get_tvl(self, token_pair: Optional[str] = None) -> Dict[str, Any]:
        """
        Get TVL data for Silo Finance.
        
        Args:
            token_pair: Optional token pair to filter by (e.g., "S-USDC.e")
            
        Returns:
            Dict containing TVL data
        """
        result = {}
        
        if self.provider_name == "defillama":
            # Fetch detailed protocol data from DefiLlama
            protocol_data = self.provider.get_protocol_info(self.protocol_slug)
            
            # Check if we have specific Sonic chain TVL
            sonic_tvl = protocol_data.get("currentChainTvls", {}).get("Sonic", 0)
            
            # Try to get more specific data for pool
            # For now, this is focused on the S-USDC.e pool on Sonic chain
            
            if not token_pair or "s-usdc" in token_pair.lower():
                
                result["silo_S-USDC.e"] = {
                    "protocol": "silo",
                    "token_pair": "S-USDC.e", # mock pool name
                    "tvl": f"${sonic_tvl:,.2f}",  # This is the entire Sonic chain TVL, not just the pool
                    "tvl_usd": sonic_tvl,
                    "provider": self.provider_name,
                    "url": "https://v2.silo.finance/markets/sonic/s-usdc-20",
                    "note": "This is the entire Sonic chain TVL. For specific pool TVL, consider using the subgraph or web scraping."
                }
                        
        return result