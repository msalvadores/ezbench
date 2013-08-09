from __future__ import with_statement
import pdb
import threading

class BenchmarkThread:
    def __init__(self,name,benchmark):
        self.name = name
        self.measures = list()
        self.lock = threading.Lock()
        self.benchmark = benchmark
        self.id_measure = 0

    def add_measure(self,group,init,end,data=None):
        with self.lock:
            self.id_measure += 1
            measure = self.benchmark.create_measure(self.id_measure,
                                          group, init, end, data=data)
        self.measures.append(measure)
