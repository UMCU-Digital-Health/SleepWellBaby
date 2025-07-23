import logging

from pathlib import Path

logger = logging.getLogger(__name__)
version = '0.1.0'

# FIXME: maybe better to move the model files to the templates directory within the package
# https://stackoverflow.com/questions/6028000/how-to-read-a-static-file-from-inside-a-python-package/58941536#58941536
package_root = Path(__file__).resolve().parents[2]
