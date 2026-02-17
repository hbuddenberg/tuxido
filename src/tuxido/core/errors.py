from __future__ import annotations


class TuxidoError(Exception):
    """Base exception for all tuxido errors."""



class SandboxError(TuxidoError):
    """Sandbox setup or execution failures."""



class ConfigError(TuxidoError):
    """Invalid configuration error."""

