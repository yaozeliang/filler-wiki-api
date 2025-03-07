import logging
import json
import sys
from datetime import datetime
import os

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
        }
        if hasattr(record, 'request_id'):
            log_record["request_id"] = record.request_id
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_record)

# Create logs directory if it doesn't exist
if not os.path.exists("logs"):
    os.makedirs("logs")

# Configure logging based on environment
if os.getenv("ENVIRONMENT") == "production":
    # In production, use JSON logging to stdout for GCP
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())
    logging.basicConfig(
        level=logging.INFO,
        handlers=[handler]
    )
else:
    # In development, use both file and console logging
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