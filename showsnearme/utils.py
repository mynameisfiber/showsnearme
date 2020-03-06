import atexit
import functools
import os
import shelve
import tempfile


def filecache(file_name):
    fname = os.path.join(tempfile.gettempdir(), "showsnearme", f"{file_name}.shelve")
    os.makedirs(os.path.dirname(fname), exist_ok=True)
    d = shelve.open(fname)
    atexit.register(d.close)

    def decorator(func):
        @functools.wraps(func)
        def new_func(param):
            if param not in d:
                d[param] = func(param)
            return d[param]

        return new_func

    return decorator
