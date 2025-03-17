"""
Dummy protocol implementation for initial testing.
"""

from typing import Dict, Any, Optional
from .protocol_base import ProtocolBase

class DummyProtocol(ProtocolBase):
    """Dummy protocol implementation for testing."""
    
    def __init__(self, protocol_name: str, provider_name: Optional[str] = None):
        """
        Initialize the dummy protocol.
        
        Args:
            protocol_name: Name of the protocol to simulate
            provider_name: Optional provider name
        """
        self.protocol_name = protocol_name
        super().__init__(provider_name)
    
    def get_tvl(self, token_pair: Optional[str] = None) -> Dict[str, Any]:
        """
        Get dummy TVL data.
        
        Args:
            token_pair: Optional token pair to filter by
            
        Returns:
            Dict containing TVL data
        """
        # Generate some dummy data
        base_tvl = 1000000  # $1M base TVL
        
        # Filter by token pair if specified
        if token_pair:
            tvl_data = {
                f"{self.protocol_name}_{token_pair}": {
                    "protocol": self.protocol_name,
                    "token_pair": token_pair,
                    "tvl": f"${base_tvl:,}",
                    "tvl_usd": base_tvl,
                    "provider": self.provider_name
                }
            }
        else:
            tvl_data = {
                f"{self.protocol_name}_S-USDC.e": {
                    "protocol": self.protocol_name,
                    "token_pair": "S-USDC.e",
                    "tvl": f"${base_tvl:,}",
                    "tvl_usd": base_tvl,
                    "provider": self.provider_name
                },
                f"{self.protocol_name}_stS-USDC.e": {
                    "protocol": self.protocol_name,
                    "token_pair": "stS-USDC.e",
                    "tvl": f"${base_tvl / 2:,}",
                    "tvl_usd": base_tvl / 2,
                    "provider": self.provider_name
                }
            }
        
        return tvl_data