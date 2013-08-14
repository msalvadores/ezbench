from __future__ import with_statement
import csv
import os
import threading
import pdb
import collections
import struct
import time
import math
import wrapper_function
from bench_thread import BenchmarkThread

class Benchmark:
    def __init__(self):
        self.lock = threading.Lock()
        self.pack_fields = "Ifff"
        self.measure_tuple = collections.namedtuple("measure",
                "id group init end elapse data thread_name")
        self.threads = list()
        self.loaded_from_file = False

    def link(self,function,group=None):
        if group is None:
            group = ".".join([function.im_class.__name__,
                              function.im_func.__name__])
        if 'im_class' in dir(function):
            class_ref = function.im_class
            wrapped = wrapper_function.ezbench_wrapper(function,self,group)
            class_ref.__dict__[function.im_func.func_name] = wrapped 
        else:
            raise Exception("plain functions not yet supported")

    def add_thread(self,thread):
        bt = None
        #loaded from file
        if isinstance(thread,basestring):
            bt = BenchmarkThread(thread,self)
        else:
            bt = BenchmarkThread(thread.name,self)
            thread.__dict__['ezbench'] = bt
        self.threads.append(bt)
        return bt

    def create_measure(self,id,group,init,end,thread_name,data=None):
        init = float(str(init))
        end = float(str(end))
        elapse = float(str(end-init)) #get rid of decimal tail
        measure = self.measure_tuple(id=id,
                                     group=group,
                                     init=init,
                                     end=end,
                                     elapse=elapse,
                                     data=data,
                                     thread_name=thread_name)
        return measure

    def measure(self,*arg,**kw):
        group = arg[0]
        lambda_runner = arg[1]
        data = kw['data'] if kw.has_key("data") else None
        init = time.time()
        result = lambda_runner()
        end = time.time()
        thread = threading.currentThread()
        if not thread.__dict__.has_key('ezbench'):
            self.add_thread(thread)
        thread.ezbench.add_measure(group,init,end,data=data)
        return result

    def save(self,out_path):
        if os.path.exists(out_path):
            raise Exception("The file path %s already exists"%out_path)
        with open(out_path, 'wb') as fout:
            csvfile = csv.writer(fout)
            for m in self.measures():
                csvfile.writerow([m.id,m.group,m.init,m.end,
                                  m.elapse,m.data,m.thread_name])

    def load(self,from_path):
        if len(self.threads) > 0:
            raise Exception("Cannot load a file in a benchmark with data")
        with open(from_path, 'rb') as fin:
            csvreader = csv.reader(fin)
            threads_by_name = dict()
            for row in csvreader:
                id,group,init,end,elapse,data,thread_name = \
                (row[0],row[1],float(row[2]),float(row[3]),float(row[4]),row[5],row[6])
                if not threads_by_name.has_key(thread_name):
                    threads_by_name[thread_name] = self.add_thread(thread_name)
                threads_by_name[thread_name].add_measure(group,init,end,data=data)
            self.threads = threads_by_name.values()
        self.loaded_from_file = True

    def groups(self):
        return self.measures.keys()

    def measures(self,thread_name=None,group=None):
        sample = list()
        for thread in self.threads:
            if thread_name is None or thread.name == thread_name:
                for measure in thread.measures:
                    if group is None or group == measure.group:
                        sample.append(measure)
        return sample

    def sorted_sample(self,group=None,thread_name=None):
        sample = self.measures(thread_name=thread_name,group=group)
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
