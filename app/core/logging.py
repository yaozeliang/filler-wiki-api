import logging
from datetime import datetime
import os

# Create logs directory if it doesn't exist
if not os.path.exists("logs"):
    os.makedirs("logs")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        # Console handler
        logging.StreamHandler(),
        # File handler with daily rotation
        logging.FileHandler(f"logs/api_{datetime.now().strftime('%Y-%m-%d')}.log")
    ]
)

# Create logger
logger = logging.getLogger("filler-api")

def log_auth_attempt(username: str, success: bool, ip: str = None):
    """Log authentication attempts"""
    status = "successful" if success else "failed"
    logger.info(f"Authentication {status} for user {username} from IP {ip}") 