import logging
from typing import Any

from click import secho, style

CONFIG_LOCATION = "base.log"

logging.basicConfig(filename=CONFIG_LOCATION, level=logging.INFO, filemode="a")


class Logger:

    def __init__(self):
        pass

    def info(self, content: Any) -> None:
        """Use this for messages we want the end-user to see."""
        secho(
            f"{style('## info', fg='cyan'):{' '}{'<'}{12}} "
            f" - "
            f"{content}"
        )
        logging.info(content)

    def error(self, content: Any) -> None:
        """Use this for error messages."""
        secho(
            f"{style('.: error', fg='red'):{' '}{'<'}{12}}"
            f" - "
            f"{content}"
        )
        logging.error(content)

    def warn(self, content: Any) -> None:
        """Use this for warning messages."""
        secho(
            f"{style('** warn ', fg='yellow'):{' '}{'<'}{12}}"
            f" - "
            f"{content}"
        )
        logging.warning(content)

    def debug(self, content: Any) -> None:
        """Use this for debug messages."""
        secho(
            f"{style('?? debug', fg='green'):{' '}{'<'}{12}}"
            f" - "
            f"{content}"
        )
        logging.debug(content)
