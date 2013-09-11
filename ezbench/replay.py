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

def call_measures(client,measures):
    while len(measures) > 0:
        to_call = measures.pop(0)
        line_args = json.loads(to_call["serialize_args"])
        args = line_args["args"]
        kw = line_args["kw"]
        replay_call(client,to_call["entry_point"],args,kw)

class Replay:

    def __init__(self,log_file,client,threads_n=1):
        self.client = client
        self.log_file = log_file
        self.threads_n = threads_n
        self.origin = Benchmark()
        self.origin.load(log_file)

    def replay(self,shuffle=True):
        measures = list(self.origin.measures())
        if shuffle:
            random.shuffle(measures)
        t=threading.Thread(target=call_measures,args=([self.client,measures]))
        t.start()
        return t

    def start(self):
        pool = []
        forked = self.origin.fork()
        for x in range(self.threads_n):
            pool.append(self.replay())
        for t in pool:
            t.join()
        return forked

if __name__ == "__main__":
    log_file = sys.argv[1]
    replay = Replay(log_file)
