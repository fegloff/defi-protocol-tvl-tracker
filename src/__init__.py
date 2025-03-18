"""
DeFi TVL Tracker package.

This package contains the implementation of a command-line tool
for tracking Total Value Locked (TVL) across multiple DeFi protocols.
"""

__version__ = "0.1.0"

# Import commonly used modules for easier access
from . import cli
from . import protocols
from . import providers
from . import utils
