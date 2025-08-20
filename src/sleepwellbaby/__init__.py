import logging
from pathlib import Path

logger = logging.getLogger(__name__)
version = "1.1.0"

package_root = Path(__file__).resolve().parents[2]
