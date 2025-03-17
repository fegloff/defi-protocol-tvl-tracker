"""
DefiLlama API provider for fetching TVL data.
"""

import requests
from typing import Dict, Any, Optional
from urllib.parse import urljoin

class DefiLlamaProvider:
    """Provider for DefiLlama API."""
    
    def __init__(self):
        """Initialize the DefiLlama API provider."""
        self.base_url = "https://api.llama.fi/"
        self.headers = {
            "Accept": "application/json",
            "User-Agent": "DeFi-TVL-Tracker/1.0"
        }
    
    def _make_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make a request to the DefiLlama API.
        
        Args:
            endpoint: API endpoint
            params: Optional query parameters
            
        Returns:
            JSON response from the API
        
        Raises:
            Exception: If the API request fails
        """
        url = urljoin(self.base_url, endpoint)
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()  # Raise an exception for 4XX/5XX responses
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"DefiLlama API request failed: {str(e)}")
    
    def get_protocol_tvl(self, protocol_slug: str) -> Dict[str, Any]:
        """
        Get TVL data for a specific protocol.
        
        Args:
            protocol_slug: Protocol slug as used in DefiLlama
            
        Returns:
            TVL data for the protocol
        """
        endpoint = f"tvl/{protocol_slug}"
        return self._make_request(endpoint)
    
    def get_protocol_info(self, protocol_slug: str) -> Dict[str, Any]:
        """
        Get detailed information about a protocol.
        
        Args:
            protocol_slug: Protocol slug as used in DefiLlama
            
        Returns:
            Protocol information
        """
        endpoint = f"protocol/{protocol_slug}"
        return self._make_request(endpoint)
    
    def get_all_protocols(self) -> Dict[str, Any]:
        """
        Get list of all protocols tracked by DefiLlama.
        
        Returns:
            All protocols tracked by DefiLlama
        """
        endpoint = "protocols"
        return self._make_request(endpoint)