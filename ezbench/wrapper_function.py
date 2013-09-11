import time
import pdb
import threading
import json

def ezbench_wrapper(func,benchmark,group,data=None,subgroups=None,entry_point=None):
    def wrapped(*args, **kw):
        self = args[0]
        init = time.time()
        exception = None
        serialize_args = None
        try:
            serialize_args = json.dumps({"args":args[1:], "kw": kw})
            wrapped_result = func(*args, **kw)
        except Exception, e:
            exception = e
        end = time.time()
        thread = threading.currentThread()
        if not thread.__dict__.has_key('ezbench'):
            benchmark.add_thread(thread)
        subgroup_data = None
        if subgroups:
            subgroup_data = subgroups(self)
        else:
            pdb.set_trace()

        data_call = None
        if data:
            data_call = data(self)
        else:
            pdb.set_trace()

        thread.ezbench.add_measure(group,init,end,data=data_call,
                                   subgroups=subgroup_data,
                                   entry_point=entry_point,
                                   serialize_args=serialize_args)
        if exception:
            raise exception
        return wrapped_result
    return wrapped
