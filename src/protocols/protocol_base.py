"""
Base protocol class that defines the interface for all protocol implementations.
"""

from typing import Dict, Any, Optional, List
from src.config import get_config

class ProtocolBase:
    """Base class for all protocol implementations."""
    
    # Default provider for this protocol
    DEFAULT_PROVIDER = "defillama"
    
    # List of supported providers for this protocol
    SUPPORTED_PROVIDERS = ["defillama"]
    
    def __init__(self, provider_name: Optional[str] = None):
        """
        Initialize the protocol with a specific provider.
        
        Args:
            provider_name: Name of the provider to use (defaults to DEFAULT_PROVIDER)
        """
        # Set the protocol identifier (overridden by subclasses)
        self.protocol_id = self.__class__.__name__.lower().replace('protocol', '')
        
        # Get protocol configuration
        self.config = get_config("protocol", self.protocol_id, {})
        
        # Use the specified provider or fall back to the default
        self.provider_name = provider_name or self.DEFAULT_PROVIDER
        
        # Validate that the provider is supported
        if self.provider_name not in self.SUPPORTED_PROVIDERS:
            raise ValueError(
                f"Provider '{self.provider_name}' is not supported for {self.__class__.__name__}. "
                f"Supported providers: {', '.join(self.SUPPORTED_PROVIDERS)}"
            )
        
        # Initialize the provider
        self.provider = self._get_provider()
    
    def _get_provider(self):
        """
        Get the provider instance.
        
        Returns:
            Provider instance
        """
        if self.provider_name == "defillama":
            from src.providers.defillama import DefiLlamaProvider
            return DefiLlamaProvider()
        # TO DO
        # elif self.provider_name == "subgraph":
        #     from src.providers.subgraph import SubgraphProvider
        #     return SubgraphProvider()
        # elif self.provider_name == "web":
        #     from src.providers.web import WebProvider
        #     return WebProvider()
        else:
            raise ValueError(f"Unknown provider: {self.provider_name}")
    
    def get_tvl(self, token_pair: Optional[str] = None, chain: Optional[str] = None) -> Dict[str, Any]:
        """
        Get TVL data for this protocol.
        
        Args:
            token_pair: Optional token pair to filter by
            chain: Optional chain to filter by
            
        Returns:
            Dict containing TVL data
        """
        # Let the provider handle the data fetching logic
        if hasattr(self.provider, 'get_protocol_tvl'):
            return self.provider.get_protocol_tvl(self.protocol_id, token_pair, chain)
        
        # Fallback implementation
        raise NotImplementedError(f"Provider {self.provider_name} does not implement get_protocol_tvl method")
    
    def get_specific_pool_tvl(self, pool_id: str) -> Dict[str, Any]:
        """
        Get TVL data for a specific pool.
        
        Args:
            pool_id: Pool ID to get TVL for
            
        Returns:
            Dict containing TVL data for the specific pool
        """
        # Let the provider handle the data fetching logic
        if hasattr(self.provider, 'get_pool_tvl'):
            return self.provider.get_pool_tvl(self.protocol_id, pool_id)
        
        # Fallback implementation
        raise NotImplementedError(f"Provider {self.provider_name} does not implement get_pool_tvl method")