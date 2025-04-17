"""
SwapX protocol implementation.
"""

from typing import Optional
from .protocol_base import ProtocolBase

class SwapxProtocol(ProtocolBase):
    """Implementation for SwapX protocol."""
    
    # Define default and supported providers
    DEFAULT_PROVIDER = "swapx_subgraph"
    SUPPORTED_PROVIDERS = ["swapx_subgraph"]
    
    def __init__(self, provider_name: Optional[str] = None):
        """
        Initialize the SwapX protocol.
        
        Args:
            provider_name: Optional provider name
        """
        # Set protocol identifier before calling parent constructor
        self.protocol_id = "swapx"
        
        # Call parent constructor
        super().__init__(provider_name)