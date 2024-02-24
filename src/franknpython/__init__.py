from importlib import metadata
from .log import log, CustomAccessLog  # noqa: F401
__version__ = metadata.version("franknpython")
del metadata
