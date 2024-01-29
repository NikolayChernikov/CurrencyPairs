"""Setup logger module."""
import logging.config

__all__ = ("setup_logger",)


def setup_logger(logging_config: dict) -> None:
    """Setup logger."""
    logging.config.dictConfig(logging_config)
