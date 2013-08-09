import time
import pdb
import threading

def ezbench_wrapper(func,benchmark,data=None):
    def wrapped(*args, **kw):
        init = time.time()
        wrapped_result = func(*args, **kw)
        end = time.time()
        thread = threading.currentThread()
        if not thread.__dict__.has_key('ezbench'):
            benchmark.add_thread(thread)
        thread.ezbench.add_measure(init,end,data=data)
        return wrapped_result
    return wrapped
