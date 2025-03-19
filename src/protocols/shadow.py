"""
Shadow Finance protocol implementation.
"""

from typing import Optional
from .protocol_base import ProtocolBase

class ShadowProtocol(ProtocolBase):
    """Implementation for Shadow Finance protocol."""
    
    # Define default and supported providers
    DEFAULT_PROVIDER = "kingdom_subgraph"
    SUPPORTED_PROVIDERS = ["kingdom_subgraph"]
    
    def __init__(self, provider_name: Optional[str] = None):
        """
        Initialize the Shadow Finance protocol.
        
        Args:
            provider_name: Optional provider name
        """
        # Set protocol identifier before calling parent constructor
        self.protocol_id = "shadow"
        
        # Call parent constructor
        super().__init__(provider_name)