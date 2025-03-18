"""
Aave Finance protocol implementation.
"""

from typing import Dict, Any, Optional
from .protocol_base import ProtocolBase

class AaveProtocol(ProtocolBase):
    """Implementation for Aave Finance protocol."""
    
    # Define default and supported providers
    DEFAULT_PROVIDER = "defillama"
    SUPPORTED_PROVIDERS = ["defillama"]
    
    def __init__(self, provider_name: Optional[str] = None):
        """
        Initialize the Aave Finance protocol.
        
        Args:
            provider_name: Optional provider name
        """
        # Set protocol identifier before calling parent constructor
        self.protocol_id = "aave"
        
        # Call parent constructor
        super().__init__(provider_name)
        