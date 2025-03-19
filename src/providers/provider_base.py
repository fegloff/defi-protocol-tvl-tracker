"""
Base class for all data providers in the DeFi TVL Tracker.
"""

import os
import json
import time
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Union

class ProviderBase(ABC):
    """Abstract base class for all TVL data providers."""
    
    def __init__(self, cache_ttl: int = 3600, cache_dir: Optional[str] = None):
        """
        Initialize the provider with caching functionality.
        
        Args:
            cache_ttl: Time-to-live for cached data in seconds (default: 1 hour)
            cache_dir: Directory to store cache files (default: ~/.defi-tvl-cache)
        """
        # Cache settings
        self.cache_ttl = cache_ttl
        self.cache_dir = cache_dir or os.path.expanduser("~/.defi-tvl-cache")
        
        # Ensure cache directory exists
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
    
    @abstractmethod
    def get_protocol_tvl(self, protocol_id: str, token_pair: Optional[str] = None, 
                         chain: Optional[str] = None) -> Dict[str, Any]:
        """
        Get TVL data for a specific protocol.
        
        Args:
            protocol_id: Protocol ID
            token_pair: Optional token pair to filter by
            chain: Optional chain to filter by
            
        Returns:
            TVL data for the protocol
        """
        pass
    
    @abstractmethod
    def format_output(self, tvl_data: Union[Dict[str, Any], List[Dict[str, Any]]], 
                     output_format: str = "table") -> str:
        """
        Format the TVL data for output.
        
        Args:
            tvl_data: TVL data to format
            output_format: Output format (table, json, csv)
            
        Returns:
            Formatted output string
        """
        pass
    
    def _get_cache_path(self, cache_key: str) -> str:
        """
        Get the file path for a cache item.
        
        Args:
            cache_key: Unique key for the cache item
            
        Returns:
            File path for the cache item
        """
        return os.path.join(self.cache_dir, f"{cache_key}.json")
    
    def _get_cached_data(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """
        Get data from cache if it exists and is not expired.
        
        Args:
            cache_key: Unique key for the cache item
            
        Returns:
            Cached data or None if not found or expired
        """
        cache_path = self._get_cache_path(cache_key)
        
        if not os.path.exists(cache_path):
            return None
        
        try:
            with open(cache_path, 'r') as f:
                cache_data = json.load(f)
                
            # Check if cache is expired
            if time.time() - cache_data.get("timestamp", 0) > self.cache_ttl:
                return None
                
            return cache_data.get("data")
        except (json.JSONDecodeError, KeyError, IOError):
            # If any error occurs, return None to fetch fresh data
            return None
    
    def _save_to_cache(self, cache_key: str, data: Dict[str, Any]) -> None:
        """
        Save data to cache.
        
        Args:
            cache_key: Unique key for the cache item
            data: Data to cache
        """
        cache_path = self._get_cache_path(cache_key)
        
        cache_data = {
            "timestamp": time.time(),
            "data": data
        }
        
        try:
            with open(cache_path, 'w') as f:
                json.dump(cache_data, f)
        except IOError as e:
            print(f"Warning: Failed to write to cache: {str(e)}")