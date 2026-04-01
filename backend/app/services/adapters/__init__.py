"""Market data source adapters.

Adapters provide a unified interface for different data sources.
Each adapter implements the DataSourceAdapter interface.

Usage:
    from app.services.adapters import AkshareAdapter, TushareAdapter

    # Get adapter by name
    adapter = get_adapter("akshare")

    # Use adapter
    quote = await adapter.get_quote("000001.SZ")
"""

from typing import Dict

from .base import DataSourceAdapter, RawQuoteData, RawKlineData, RawSearchResult
from .akshare_adapter import AkshareAdapter
from .tushare_adapter import TushareAdapter


# Registry of available adapters
_ADAPTERS: Dict[str, DataSourceAdapter] = {}


def register_adapter(name: str, adapter: DataSourceAdapter):
    """Register an adapter by name."""
    _ADAPTERS[name] = adapter


def get_adapter(name: str) -> DataSourceAdapter:
    """Get an adapter by name.

    Args:
        name: Adapter name ('akshare', 'tushare')

    Returns:
        DataSourceAdapter instance

    Raises:
        ValueError: If adapter name is not registered
    """
    if name not in _ADAPTERS:
        available = list(_ADAPTERS.keys())
        raise ValueError(f"Unknown adapter: {name}. Available: {available}")
    return _ADAPTERS[name]


def list_adapters() -> list:
    """List all registered adapter names."""
    return list(_ADAPTERS.keys())


# Register default adapters
register_adapter("akshare", AkshareAdapter())
register_adapter("tushare", TushareAdapter())


__all__ = [
    "DataSourceAdapter",
    "RawQuoteData",
    "RawKlineData",
    "RawSearchResult",
    "AkshareAdapter",
    "TushareAdapter",
    "get_adapter",
    "list_adapters",
    "register_adapter",
]
