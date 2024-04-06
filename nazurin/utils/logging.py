import logging
import sys

from loguru import logger


class InterceptHandler(logging.Handler):
    """Intercept Python logging and forward to Loguru."""

    def emit(self, record):
        # Get corresponding Loguru level if it exists.
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message.
        frame, depth = sys._getframe(6), 6
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level,
            record.getMessage(),
        )


def configure_logging():
    # Remove default handler
    logger.remove()
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss,SSSZZ}</green> - "
        "<level>{level: <8}</level> - "
        "<cyan>{name}</cyan>:<cyan>{line}</cyan> - "
        "{extra[request]} - {message}",
        level="DEBUG",
    )
    logger.configure(extra={"request": ""})
    logging.basicConfig(handlers=[InterceptHandler()], level=logging.INFO, force=True)
