"""StemForge — AI remix / stem separation generator.

Top-level package. Public surface is intentionally small: the engine,
the separator registry, and the config loader. Everything else is
internal and may move between minor versions.
"""

from stemforge.core.engine import StemForgeEngine, BACKENDS
from stemforge.core.separator_base import StemSeparator, StemSet

__version__ = "0.6.3"
__all__ = ["StemForgeEngine", "BACKENDS", "StemSeparator", "StemSet", "__version__"]