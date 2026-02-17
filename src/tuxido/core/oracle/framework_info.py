from __future__ import annotations

import inspect
import sys

from pydantic import BaseModel


class FrameworkInfo(BaseModel):
    textual_version: str | None
    python_version: str
    widgets: list[str]
    deprecated: list[str]
    platform: str


def get_framework_info(detail_level: str = "minimal") -> FrameworkInfo:
    """Get framework information for the installed Textual version.

    Args:
        detail_level: "minimal" for basic info, "full" for complete details.

    Returns:
        FrameworkInfo with Textual metadata.

    """
    textual_version: str | None = None
    widgets: list[str] = []
    deprecated: list[str] = []

    try:
        import textual

        textual_version = textual.__version__
    except ImportError:
        pass

    if textual_version:
        try:
            from textual import widgets as textual_widgets

            for name in dir(textual_widgets):
                obj = getattr(textual_widgets, name, None)
                if inspect.isclass(obj) and hasattr(obj, "__bases__"):
                    if obj.__name__[0].isupper() and obj.__name__ not in (
                        "Widget",
                        "Static",
                        "Button",
                    ):
                        widgets.append(obj.__name__)
        except Exception:
            pass

    return FrameworkInfo(
        textual_version=textual_version,
        python_version=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        widgets=sorted(widgets),
        deprecated=sorted(deprecated),
        platform=sys.platform,
    )
