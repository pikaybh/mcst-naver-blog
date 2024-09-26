import functools
import time

def retry(max_retries=3, delay=1, exceptions=(Exception,)):
    """
    Decorator that retries a function call if an exception is raised.
    
    :param max_retries: Maximum number of retries (default 3)
    :param delay: Delay between retries in seconds (default 1 second)
    :param exceptions: Tuple of exceptions to catch and retry (default Exception)
    """
    def decorator_retry(func):
        @functools.wraps(func)
        def wrapper_retry(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    retries += 1
                    if retries >= max_retries:
                        print(f"Max retries reached. Function failed: {e}")
                        raise
                    print(f"Retrying ({retries}/{max_retries}) after error: {e}")
                    time.sleep(delay)
        return wrapper_retry
    return decorator_retry
