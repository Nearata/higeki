import logging

from rich.logging import RichHandler

logger = logging.getLogger("higeki")
logger.setLevel(logging.ERROR)
logger.propagate = False

console_handler = RichHandler(show_time=False, show_path=False)
console_handler.setFormatter(logging.Formatter("%(message)s"))

logger.addHandler(console_handler)
