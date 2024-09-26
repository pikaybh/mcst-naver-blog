from typing import Any, Callable, Optional, Union
from logging import Logger
import functools
import asyncio
import time

def retry(max_retries: Optional[int] = 3, delay: Optional[int] = 1, exceptions: Optional = (Exception,), logger: Optional[Logger] = None) -> Any:
    """
    A decorator that retries a function call if an exception is raised.

    This decorator can handle both synchronous and asynchronous functions.
    If the function raises one of the specified exceptions, the function will
    be retried up to `max_retries` times, with an optional delay between retries.

    Args:
        max_retries (Optional[int]): The maximum number of retries. Defaults to 3.
        delay (Optional[int]): Delay between retries in seconds. Defaults to 1 second.
        exceptions (Optional[tuple]): A tuple of exceptions to catch and retry. Defaults to (Exception,).
        logger (Optional[Logger]): An optional logger to log retry attempts. Defaults to None.

    Returns:
        Callable: The wrapped function, which will be retried upon encountering exceptions.

    Example:
        @retry(max_retries=5, delay=2, exceptions=(TimeoutError,))
        async def some_async_function():
            await some_async_code()

        @retry(max_retries=3, delay=1, exceptions=(ValueError,))
        def some_sync_function():
            return some_sync_code()
    """
    def decorator_retry(func: Callable):
        @functools.wraps(func)
        async def async_wrapper_retry(*args, **kwargs):
            """
            Wrapper function for async functions, which handles retries.

            Args:
                *args: Positional arguments passed to the wrapped function.
                **kwargs: Keyword arguments passed to the wrapped function.

            Returns:
                Any: The result of the wrapped function if successful.

            Raises:
                Exception: If the function raises exceptions beyond the allowed retry count.
            """
            retries: int = 0
            while retries < max_retries:
                try:
                    return await func(*args, **kwargs)  # Handle async function with await
                except exceptions as e:
                    retries += 1
                    if retries >= max_retries:
                        if logger:
                            logger.debug(f"Max retries reached. Function failed: {e}")
                        raise
                    if logger:
                        logger.debug(f"Retrying ({retries}/{max_retries}) after error: {e}")
                    await asyncio.sleep(delay)  # Use asyncio.sleep for async delay

        @functools.wraps(func)
        def sync_wrapper_retry(*args, **kwargs):
            """
            Wrapper function for sync functions, which handles retries.

            Args:
                *args: Positional arguments passed to the wrapped function.
                **kwargs: Keyword arguments passed to the wrapped function.

            Returns:
                Any: The result of the wrapped function if successful.

            Raises:
                Exception: If the function raises exceptions beyond the allowed retry count.
            """
            retries: int = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)  # Handle sync function normally
                except exceptions as e:
                    retries += 1
                    if retries >= max_retries:
                        if logger:
                            logger.debug(f"Max retries reached. Function failed: {e}")
                        raise
                    if logger:
                        logger.debug(f"Retrying ({retries}/{max_retries}) after error: {e}")
                    time.sleep(delay)  # Regular sleep for sync functions

        # Check if the function is async or sync, and wrap accordingly
        if asyncio.iscoroutinefunction(func):
            return async_wrapper_retry
        else:
            return sync_wrapper_retry

    return decorator_retry
