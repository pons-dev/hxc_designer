import time

def fn_timer(fn):
    def wrapper(*args, **kwargs):
        t0 = time.time()
        fn_return = fn(*args, **kwargs)
        t1 = time.time()
        t_delta = t1 - t0
        return fn_return, t_delta
    
    return wrapper
