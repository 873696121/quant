"""Core configuration module.

Re-exports settings from app.config for convenience.
"""

from app.config import Settings, settings

__all__ = ["Settings", "settings"]
