"""
Data providers for DeFi TVL Tracker.
"""

from typing import Dict, Any, Optional, Type

# Dictionary of provider classes
_PROVIDER_CLASSES = {}

def register_provider(name: str, provider_class: Type):
    """
    Register a provider class.
    
    Args:
        name: Provider name
        provider_class: Provider class
    """
    _PROVIDER_CLASSES[name] = provider_class

def get_provider(provider_name: str, **kwargs) -> Any:
    """
    Get a provider instance by name.
    
    Args:
        provider_name: Name of the provider
        **kwargs: Additional arguments to pass to the provider constructor
        
    Returns:
        Provider instance
        
    Raises:
        ValueError: If the provider is not supported
    """
    if provider_name == "defillama":
        from .defillama import DefiLlamaProvider
        return DefiLlamaProvider(**kwargs)
    elif provider_name == "kingdom_subgraph":
        from .kingdom_subgraph import KingdomSubgraphProvider
        return KingdomSubgraphProvider(**kwargs)
    elif provider_name == "swapx_subgraph":
        from .swapx_subgraph import SwapxSubgraphProvider
        return SwapxSubgraphProvider(**kwargs)
    else:
        raise ValueError(f"Unsupported provider: {provider_name}")

def get_all_providers() -> Dict[str, str]:
    """
    Get a dictionary of all available providers.
    
    Returns:
        Dictionary of provider names to descriptions
    """
    return {
        "defillama": "DefiLlama API provider",
        "kingdom_subgraph": "Kingdom Subgraph GraphQL provider"
    }