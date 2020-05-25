from tplight import LB130
from functools import wraps
from time import sleep


def retry(exc: str = Exception, retries: int = 2, delay: int = 2):
    """
    retry decorator

    Keyword Arguments:
        exc {str} -- exception you wish to catch (default: {Exception})
        retries {int} -- num of retries (default: {2})
        delay {int} -- time is seconds beween each retry (default: {2})
    """
    def retry_dec(f: object):

        @wraps(f)
        def retry_f(*args, **kwargs):
            retry_num = retries
            while retry_num > 1:
                # attempt to connect
                try:
                    return f(*args, **kwargs)
                except exc:
                    retry_num -= 1
                    # delay time
                    sleep(delay)
            # last chance to connect
            return f(*args, **kwargs)

        return retry_f

    return retry_dec


class TPLConn:
    def __init__(self, ip: str):
        """
        Context manager for TP Link connection object
        Arguments:
            ip {str} -- ipv4 address
        """
        self.ip = ip

    @retry()
    def __enter__(self):
        self.light = LB130(self.ip)
        return self.light

    def __exit__(self, exc_type, exc_val, exc_tb):
        # explicitly deletes object on exit
        del self.light


if __name__ == "__main__":
    with TPLConn("192.168.1.141") as tpl:
        tpl.on()
