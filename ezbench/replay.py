from ezbench import Benchmark
import sys
import pdb
import random
import threading
import json

def replay_call(client,entry_point,args,kw):
    entry_point=entry_point.split(".")
    module = sys.modules[entry_point[0]]
    traverse = module
    for n in entry_point[1:]:
        traverse = getattr(traverse, n)
    function = traverse
    args = [client] + args
    function(*args,**kw)


class ReplayThread(threading.Thread):
    def __init__(self,client,log):
        super(ReplayThread,self).__init__()
        self.client = client
        self.init_length = len(log)
        self.log = log
        self.errors = []

    def run(self):
        while len(self.log) > 0:
            to_call = self.log.pop(0)
            line_args = json.loads(to_call["serialize_args"])
            args = line_args["args"]
            kw = line_args["kw"]
            try:
                replay_call(self.client,to_call["entry_point"],args,kw)
            except Exception, exc:
                self.errors.append(exc)

class Replay:

    def __init__(self,log_file,client,threads_n=1):
        self.client = client
        self.log_file = log_file
        self.threads_n = threads_n
        self.origin = Benchmark()
        self.origin.load(log_file)
        self.forked = self.origin.fork()
        self.forked.replay = self
        self.pool = list()

    def replay(self,shuffle=True):
        measures = list(self.origin.measures())
        if shuffle:
            random.shuffle(measures)
        t = ReplayThread(self.client,measures)
        t.start()
        return t

    def start(self):
        for x in range(self.threads_n):
            self.pool.append(self.replay())
        for t in self.pool:
            t.join()
        return self.forked

if __name__ == "__main__":
    log_file = sys.argv[1]
    replay = Replay(log_file)
