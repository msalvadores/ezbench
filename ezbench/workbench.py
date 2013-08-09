from __future__ import with_statement
import csv
import os
import threading
import pdb
import collections
import struct
import time
import math

class Benchmark:
    def __init__(self):
        self.measures = dict()
        self.id_measure = 0
        self.lock = threading.Lock()
        self.pack_fields = "Ifff"
        self.measure_tuple = collections.namedtuple("measure","id init end elapse data")

    def measure(self,*arg,**kw):
        group = arg[0]
        lambda_runner = arg[1]
        init = time.time()
        result = lambda_runner()
        end = time.time()
        if not self.measures.has_key(group):
            self.measures[group] = list()
        with self.lock:
            self.id_measure += 1
            elapse = float(str(end-init)) #get rid of decimal tail
            measure = self.measure_tuple(id=self.id_measure,
                                         init=init,
                                         end=end,
                                         elapse=elapse,
                                         data=None)

            self.measures[group].append(measure)
        return result

    def groups(self):
        return self.measures.keys()

    def sorted_sample(self,group=None):
        sample = list()
        if not group:
            for xgroup in self.groups():
                sample.extend(self.measures[xgroup])
        else:
            sample.extend(self.measures[group])
        return sorted(sample, key=lambda x: x.elapse)

    def maximum(self,group=None):
        sample = self.sorted_sample(group=group)
        return sample[-1].elapse

    def median(self,group=None):
        sample = self.sorted_sample(group=group)
        return sample[int(math.ceil((len(sample)-1)/2.0))].elapse

    def percentiles(self,group=None,include=[50,70,90]):
        result = dict()
        sample = self.sorted_sample(group=group)

        for perc in include:
            perc_index = int(math.ceil((perc/100.0) * (len(sample)-1)))
            result[perc] = sample[perc_index].elapse
        return result
