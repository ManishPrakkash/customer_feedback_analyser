import os
import logging as logger
from dotenv import load_dotenv

load_dotenv()

logger.basicConfig(level=logger.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Redis is optional for local/dev. Import gracefully and only create a client when configured.
try:
	import redis  # type: ignore
except Exception:
	redis = None  # type: ignore

REDIS_URL = os.getenv("REDIS_URL")
if redis is not None and REDIS_URL:
	try:
		redis_client = redis.Redis.from_url(REDIS_URL)
	except Exception as e:
		logger.warning(f"Failed to initialize Redis client from REDIS_URL: {e}")
		redis_client = None
else:
	if not REDIS_URL:
		logger.info("REDIS_URL not set; Redis features will be disabled.")
	elif redis is None:
		logger.info("redis package not installed; Redis features will be disabled.")
	redis_client = None
