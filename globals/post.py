from functools import wraps
from re import search as r_search
from time import sleep
from requests import post


def retry(resp_code: str = "500", retries: int = 3, delay: int = 2):
    """
    retry decorator

    Keyword Arguments:
        resp_code {str} -- http response code from operation
        retries {int} -- num of retries (default: {2})
        delay {int} -- time is seconds beween each retry (default: {5})
    """
    def retry_dec(f: object):

        @wraps(f)
        def retry_f(*args, **kwargs):
            retry_num = retries
            while retry_num > 1:
                # attempt to call func
                func_call = f(*args, **kwargs)
                response = r_search(f"\[(.*)\]", str(func_call)).group(1)
                if response == resp_code:  # we didn't want to see that code
                    retry_num -= 1
                    # wait delay before try
                    sleep(delay)
                else:  # response code is acceptable
                    return func_call
            # last chance to connect
            return f(*args, **kwargs)

        return retry_f

    return retry_dec

@retry()
def poster(url: str, json: dict) -> dict:
    return post(url, json=json)