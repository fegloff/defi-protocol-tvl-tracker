"""
Base protocol class that defines the interface for all protocol implementations.
"""

from typing import Dict, Any, Optional, List

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
        else:
            raise ValueError(f"Unknown provider: {self.provider_name}")
    
    def get_tvl(self, token_pair: Optional[str] = None) -> Dict[str, Any]:
        """
        Get TVL data for this protocol.
        
        Args:
            token_pair: Optional token pair to filter by
            
        Returns:
            Dict containing TVL data
        """
        raise NotImplementedError("Subclasses must implement get_tvl()")