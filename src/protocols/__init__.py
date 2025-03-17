"""
Protocol-specific implementations for the DeFi TVL Tracker.
"""

from typing import Dict, List, Optional, Any
from .protocol_base import ProtocolBase

# Dictionary mapping protocol names to their classes (will be populated by imports)
_PROTOCOL_CLASSES = {}

def register_protocol(name: str, protocol_class):
    """
    Register a protocol class.
    
    Args:
        name: Protocol name
        protocol_class: Protocol class
    """
    _PROTOCOL_CLASSES[name] = protocol_class

def get_supported_protocols() -> Dict[str, List[str]]:
    """
    Get a dictionary of supported protocols and their providers.
    
    Returns:
        Dict mapping protocol names to lists of supported providers
    """
    # For now, return a static dictionary of supported protocols
    # This will be populated dynamically as protocol modules are imported
    return {
        "silo": ["defillama"],
        "shadow": ["defillama"],
        "swapx": ["defillama"],
        "beets": ["defillama"],
        "pendle": ["defillama"],
        "euler": ["defillama"],
        "aave": ["defillama"],
        "curve": ["defillama"]
    }

def get_protocol_instance(protocol_name: str, provider_name: Optional[str] = None) -> ProtocolBase:
    """
    Get an instance of a protocol.
    
    Args:
        protocol_name: Name of the protocol
        provider_name: Optional name of the provider to use
        
    Returns:
        Protocol instance
    
    Raises:
        ValueError: If the protocol is not supported
    """
    # Handle specific protocols first
    if protocol_name == "silo":
        from .silo import SiloProtocol
        return SiloProtocol(provider_name)
    
    # For other protocols, use the dummy implementation for now
    from .dummy import DummyProtocol
    return DummyProtocol(protocol_name, provider_name)
    
    # Later, this will be fully implemented using the registry:
    # if protocol_name not in _PROTOCOL_CLASSES:
    #     raise ValueError(f"Unsupported protocol: {protocol_name}")
    # return _PROTOCOL_CLASSES[protocol_name](provider_name)