"""
Euler Finance protocol implementation.
"""

from typing import Optional
from .protocol_base import ProtocolBase

class EulerProtocol(ProtocolBase):
    """Implementation for Euler Finance protocol."""
    
    # Define default and supported providers
    DEFAULT_PROVIDER = "defillama"
    SUPPORTED_PROVIDERS = ["defillama"]
    
    def __init__(self, provider_name: Optional[str] = None):
        """
        Initialize the Euler Finance protocol.
        
        Args:
            provider_name: Optional provider name
        """
        # Set protocol identifier before calling parent constructor
        self.protocol_id = "euler"
        
        # Call parent constructor
        super().__init__(provider_name)