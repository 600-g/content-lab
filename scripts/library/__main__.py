"""`python -m scripts.library <build-catalog|search|stats>` 진입점."""
from __future__ import annotations

import sys

from scripts.library.catalog import main

if __name__ == "__main__":
    sys.exit(main())
