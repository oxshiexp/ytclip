from app.core.cleanup import cleanup_outputs
from app.utils.logging import setup_logging

logger = setup_logging("cleanup")


if __name__ == "__main__":
    removed = cleanup_outputs()
    logger.info("cleanup_complete", extra={"removed": removed})
