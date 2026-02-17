from __future__ import annotations

import sys

__version__ = "0.1.0"


def get_versions() -> dict[str, str | None]:
    """Get version information for tuxido, Python, and Textual."""
    result = {
        "tuxido": __version__,
        "python": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "textual": None,
    }

    try:
        import textual
        result["textual"] = textual.__version__
    except ImportError:
        pass

    return result
