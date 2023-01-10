import sys
import logging

handler = logging.StreamHandler(sys.stdout)
logging.basicConfig(
    level=logging.DEBUG,
    handlers=[handler]
)
