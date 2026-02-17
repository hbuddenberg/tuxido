from __future__ import annotations

from tuxido.core.validators.l1_syntax import validate_syntax
from tuxido.core.validators.l2_static import validate_static
from tuxido.core.validators.l3_dom import validate_dom
from tuxido.core.validators.l4_sandbox import validate_sandbox

__all__ = ["validate_dom", "validate_sandbox", "validate_static", "validate_syntax"]
