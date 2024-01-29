"""Main entrypoint for application."""
# isort: skip_file
from src.lib.setup_logger import setup_logger
from src.currency_pairs.logging_config import LOGGING_CONFIG

setup_logger(logging_config=LOGGING_CONFIG)

from src.currency_pairs.app import (  # noqa: E402, E501 pylint: disable=[wrong-import-position]
    Application,
)


def run() -> None:
    """
    Run application.

    Returns:
        None
    """
    app = Application()
    app.run()


if __name__ == "__main__":  # pragma: no cover
    run()
