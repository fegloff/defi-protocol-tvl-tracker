"""
Protocol-specific implementations for the DeFi TVL Tracker.
"""

from typing import Dict, List, Optional, Any
import importlib
import sys
import os
from .protocol_base import ProtocolBase
from ..config import get_config

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
    # Get all protocols from config
    protocol_config = get_config("protocol", None)
    result = {}
    # Loop through protocol modules and import them to get their supported providers
    for protocol_name in protocol_config.keys():
        try:
            # Dynamically import the protocol module
            module_name = f".{protocol_name}"
            module = importlib.import_module(module_name, package=__package__)
            
            # Try to get the class name by convention (protocol name + Protocol)
            class_name = f"{protocol_name.capitalize()}Protocol"
            if hasattr(module, class_name):
                protocol_class = getattr(module, class_name)
                # Get supported providers from the class
                if hasattr(protocol_class, "SUPPORTED_PROVIDERS"):
                    result[protocol_name] = protocol_class.SUPPORTED_PROVIDERS
                else:
                    # Default to defillama if not specified
                    result[protocol_name] = ["defillama"]
        except (ImportError, AttributeError) as e:
            # Skip protocols that don't have a module yet
            # Could log this for debugging
            pass
    
    return result

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
    try:
        # Dynamically import the protocol module
        module_name = f".{protocol_name}"
        module = importlib.import_module(module_name, package=__package__)
        
        # Try to get the class by convention
        class_name = f"{protocol_name.capitalize()}Protocol"
        if hasattr(module, class_name):
            protocol_class = getattr(module, class_name)
            return protocol_class(provider_name)
        else:
            raise ValueError(f"Protocol class {class_name} not found in module {module_name}")
    except ImportError:
        raise ValueError(f"Protocol '{protocol_name}' is not supported")