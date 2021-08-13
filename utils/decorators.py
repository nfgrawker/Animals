"""Utility decorators to use throughout the application."""
from typing import Callable, Tuple, Dict, Any

from requests.exceptions import HTTPError

from utils.log import Logger


def bad_server(function: Callable) -> Callable:
    """Keep trying requests until successful, due to inconsistent server performance."""
    log = Logger()
    retry_limit = 3

    def _function(*args: Tuple[Any], **kwargs: Dict[str, Any]) -> Callable:
        current_try = 0
        while current_try < retry_limit:
            try:
                result = function(*args, **kwargs)
                return result
            except HTTPError as e:
                log.error(f"{e} happened upon {function.__name__}, try = {current_try}, retrying.")
                current_try += 1
        log.error(f"failed try {current_try} on {function.__name__} exiting this call.")

    return _function


def singleton(cls: Callable) -> Callable:
    """Override all instantiations to return one instance per class."""
    instances = dict()

    def _singleton(*args: Tuple[Any], **kwargs: Dict[str, Callable]) -> Callable:
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return _singleton
