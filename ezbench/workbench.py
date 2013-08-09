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

    def save(self,out_path):
        if os.path.exists(out_path):
            raise Exception("The file path %s already exists"%out_path)
        with open(out_path, 'wb') as fout:
            csvfile = csv.writer(fout)
            for group in self.measures.keys():
                for m in self.measures[group]:
                    csvfile.writerow([m.id,group,m.init,m.end,m.elapse,m.data])

    def load(self,from_path):
        if len(self.measures) > 0:
            raise Exception("Cannot load a file in a benchmark with data")
        with open(from_path, 'rb') as fin:
            csvreader = csv.reader(fin)
            for row in csvreader:
                id,group,init,end,elapse,data = \
                (row[0],row[1],float(row[2]),float(row[3]),float(row[4]),row[5])
                if not self.measures.has_key(group):
                    self.measures[group] = list()
                m= self.measure_tuple(id=id,
                                     init=init,
                                     end=end,
                                     elapse=elapse,
                                     data=data)
                self.measures[group].append(m)

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
