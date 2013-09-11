from __future__ import with_statement
import csv
import os
import threading
import collections
import struct
import time
import math
import wrapper_function
from bench_thread import BenchmarkThread
import sys

class Benchmark:
    def __init__(self):
        self.lock = threading.Lock()
        self.pack_fields = "Ifff"
        self.threads = list()
        self.loaded_from_file = False
        self.links = dict()
        self.floats = ["init","end","elapse"]
        self.fields = ["id","group","init","end","elapse","data",
                        "thread_name","entry_point","serialize_args"]

    def link(self,function,group=None,subgroups=None,data=None):
        if isinstance(function,basestring):
            module = function.split(".")[0]
            if module not in sys.modules:
                __import__(module)
            module = sys.modules[module]
            traverse = module
            for n in function.split(".")[1:]:
                traverse = getattr(traverse, n)
            function = traverse
        entry_point = ".".join([function.im_class.__module__,
                          function.im_class.__name__,
                          function.im_func.__name__])
        if not group:
            group = ".".join(entry_point.split(".")[-2:])
        self.links[group] = function
        if 'im_class' in dir(function):
            class_ref = function.im_class
            wrapped = wrapper_function.ezbench_wrapper(function,
                            self,
                            group,
                            subgroups=subgroups,
                            entry_point=entry_point,
                            data=data)
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

    def create_measure(self,id,group,init,end,thread_name,**kw):
        init = float("%.5f"%init)
        end = float("%.5f"%end)
        elapse = float("%.5f"%(end-init)) #get rid of decimal tail
        if "subgroups" in kw and  len(kw["subgroups"]):
            for x in kw["subgroups"]:
                kw["subgroups"][x] = float("%.5f"%kw["subgroups"][x])
            
        measure = dict(id=id,group=group,init=init,
                       end=end,elapse=elapse,
                       thread_name=thread_name)
        measure.update(kw)
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
                row = []
                for f in self.fields:
                    if isinstance(m[f],float):
                        row.append("%.5f"%m[f])
                    else:
                        row.append(m[f])
                if m["subgroups"]:
                    for sb in sorted(m["subgroups"].keys()):
                        row.append("%s %.5f"%(sb,m["subgroups"][sb]))
                csvfile.writerow(row)

    def load(self,from_path):
        if len(self.threads) > 0:
            raise Exception("Cannot load a file in a benchmark with data")
        with open(from_path, 'rb') as fin:
            csvreader = csv.reader(fin)
            threads_by_name = dict()
            for row in csvreader:
                entry = {}
                for f in range(len(self.fields)):
                    if self.fields[f] in self.floats:
                        entry[self.fields[f]] = float(row[f])
                    else:
                        entry[self.fields[f]] = row[f]
                subgroups = dict()
                for s in row[len(self.fields):]:
                    (sname,svalue) = s.split(" ")
                    svalue = float(svalue)
                    subgroups[sname] = svalue
                if len(subgroups) == 0:
                    subgroups = None

                thread_name = entry["thread_name"]
                if not threads_by_name.has_key(thread_name):
                    threads_by_name[thread_name] = self.add_thread(thread_name)
                group,init,end = entry["group"],entry["init"],entry["end"]
                del entry["group"]
                del entry["init"]
                del entry["end"]
                del entry["id"]
                del entry["thread_name"]
                threads_by_name[thread_name]\
                .add_measure(group,init,end,**entry)
            self.threads = threads_by_name.values()
        self.loaded_from_file = True

    def fork(self):
        forked = Benchmark()
        groups = dict()
        for m in self.measures():
            group = m["group"]
            if group not in groups:
                groups[group]=m["entry_point"]
        for (group,entry_point) in groups.items():
            forked.link(entry_point,group=group)
        return forked

    def groups(self):
        return self.links.keys()

    def measures(self,thread_name=None,group=None):
        sample = list()
        for thread in self.threads:
            if thread_name is None or thread.name == thread_name:
                for measure in thread.measures:
                    if group is None or group == measure["group"]:
                        sample.append(measure)
        return sample

    def sorted_sample(self,group=None,thread_name=None):
        sample = self.measures(thread_name=thread_name,group=group)
        return sorted(sample, key=lambda x: x["elapse"])

    def maximum(self,group=None):
        sample = self.sorted_sample(group=group)
        if len(sample) == 0:
            return {"total" : 0.0 }
        res =  { "total" : sample[-1]["elapse"] }
        if sample[-1]["subgroups"]:
            res.update(sample[-1]["subgroups"])
        return res

    def median(self,group=None):
        sample = self.sorted_sample(group=group)
        if len(sample) == 0:
            return {"total" : 0.0 }
        s = sample[int(math.ceil((len(sample)-1)/2.0))]
        res =  { "total" : s["elapse"] }
        if "subgroups" in s and len(s["subgroups"]) > 0:
            res.update(s["subgroups"])
        return res

    def percentiles(self,group=None,include=None):
        if include is None:
            include = [70,80,90]
        result = dict()
        sample = self.sorted_sample(group=group)
        if len(sample) == 0:
            for x in include:
                result[x] = {"total" : 0.0 }
            return result

        for perc in include:
            perc_index = int(math.ceil((perc/100.0) * (len(sample)-1)))
            result[perc] = { "total": sample[perc_index]["elapse"] }
            if sample[perc_index]["subgroups"]:
                result[perc].update(sample[perc_index]["subgroups"])
        return result

