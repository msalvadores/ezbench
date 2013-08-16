import time
import pdb
import threading

def ezbench_wrapper(func,benchmark,group,data=None,subgroups=None):
    def wrapped(*args, **kw):
        self = args[0]
        init = time.time()
        exception = None
        try:
            wrapped_result = func(*args, **kw)
        except e:
            exception = e
        end = time.time()
        thread = threading.currentThread()
        if not thread.__dict__.has_key('ezbench'):
            benchmark.add_thread(thread)
        subgroup_data = None
        if subgroups:
            subgroup_data = subgroups(self)
        data_call = None
        if data:
            data_call = data(self)

        thread.ezbench.add_measure(group,init,end,data=data_call,subgroups=subgroup_data)
        if exception:
            raise exception
        return wrapped_result
    return wrapped
