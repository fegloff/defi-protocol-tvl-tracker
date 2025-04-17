"""
Base protocol class that defines the interface for all protocol implementations.
"""

from typing import Dict, Any, Optional, List
from src.config import get_config
from src.providers import get_provider

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
        # Set the protocol identifier (overridden by subclasses if needed)
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
        
        # Initialize the provider using the registry
        self.provider = get_provider(self.provider_name)
    
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
    
    def format_output(self, tvl_data: Dict[str, Any], output_format: str = "table") -> str:
        """
        Format the TVL data for output.
        
        Args:
            tvl_data: TVL data to format
            output_format: Output format (table, json, csv)
            
        Returns:
            Formatted output string
        """
        # Use the provider's format_output method if available
        if hasattr(self.provider, 'format_output'):
            return self.provider.format_output(tvl_data, output_format)
        
        # Fallback to the formatter utility
        from src.utils.formatter import format_tvl_output
        return format_tvl_output(tvl_data, output_format)