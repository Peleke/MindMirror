import logging
import os
from pathlib import Path

from loguru import logger

# Assuming this file is now at backend/practices/practices/monitoring/logging_config.py
# LOGS_DIR will be backend/practices/practices/logs
LOGS_DIR = Path(__file__).resolve().parent.parent / "logs"


# Intercept standard logging
class InterceptHandler(logging.Handler):
    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def setup_logging():
    """Configures Loguru for the application."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    logger.remove()

    # Configure Loguru to intercept standard logging messages
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    # Add Loguru's own handlers
    logger.add(
        os.sys.stderr,
        level="INFO",
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        colorize=True,
    )

    logger.add(
        LOGS_DIR / "practices_api.json",
        level="INFO",
        format="{time} {level} {message}",
        serialize=True,
        rotation="10 MB",
        compression="zip",
        enqueue=True,
    )

    # Configure SQLAlchemy loggers to send output at INFO level
    # These will now be intercepted by Loguru via the InterceptHandler
    logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.pool").setLevel(logging.INFO)
    # For more verbose output including result sets (careful, can be very verbose):
    # logging.getLogger("sqlalchemy.engine").setLevel(logging.DEBUG)
    # For more verbose pool checkins/checkouts:
    # logging.getLogger("sqlalchemy.pool").setLevel(logging.DEBUG)

    logger.info("Loguru logging configured to intercept standard logs. SQLAlchemy logging enabled.")


if __name__ == "__main__":
    setup_logging()
    logger.info("This is an info message from logging_config.")
    logger.debug("This is a debug message that should not appear with default INFO level for stderr.")

    # Test standard logging interception
    std_logger = logging.getLogger("my_std_lib_logger")
    std_logger.info("This is an INFO message from a standard library logger.")
    std_logger.warning("This is a WARNING message from a standard library logger.")
    std_logger.debug("This is a DEBUG message from a standard library logger (should not appear on INFO sinks).")

    # Simulate SQLAlchemy engine logs (use actual SQLAlchemy operations in your app to test properly)
    sql_engine_logger = logging.getLogger("sqlalchemy.engine")
    # These should appear as INFO level if setup_logging set the level correctly
    sql_engine_logger.info("Simulated SQL Query: SELECT * FROM users")
    sql_engine_logger.debug("Simulated SQL Query with results (debug only)")

    try:
        1 / 0
    except ZeroDivisionError:
        logger.exception("A caught exception occurred.")
