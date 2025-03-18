"""
Curve Finance protocol implementation.
"""

from typing import Dict, Any, Optional
from .protocol_base import ProtocolBase

class CurveProtocol(ProtocolBase):
    """Implementation for Curve Finance protocol."""
    
    # Define default and supported providers
    DEFAULT_PROVIDER = "defillama"
    SUPPORTED_PROVIDERS = ["defillama"]
    
    def __init__(self, provider_name: Optional[str] = None):
        """
        Initialize the Curve Finance protocol.
        
        Args:
            provider_name: Optional provider name
        """
        # Set protocol identifier before calling parent constructor
        self.protocol_id = "curve"
        
        # Call parent constructor
        super().__init__(provider_name)
        