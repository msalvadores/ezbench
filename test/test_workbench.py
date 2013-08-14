import pdb
import os
import random
import time
import ezbench
import StringIO

class SingleProcess:
    def __init__(self):
        self.count = 0

    def do_it(self):
        x = random.randint(1, 10)
        if x < 7:
            time.sleep(random.random() + 0.001)
        else:
            time.sleep(random.random() + 0.4)
        self.count += 1
        return self.count

class SubGroupProcess:
    def __init__(self):
        self.count = 0
        self.last = None
        
    def sub1(self):
        pass

    def sub2(self):
        pass

    def do_it(self):
        return
        x = random.randint(1, 10)
        if x < 7:
            time.sleep(random.random() + 0.001)
        else:
            time.sleep(random.random() + 0.4)
        self.count += 1
        return self.count

def test_single_process():
    "testing a simple process benchmark no subtasks"

    benchmark = ezbench.Benchmark()
    proc = SingleProcess()
    for x in range(0,20):
        result = benchmark.measure("SingleProcess.do_it", 
                          lambda: proc.do_it())
        assert result == x+1, "Sample result does not match the original"

    top = benchmark.maximum()
    assert top < 1.5
    assert len(benchmark.threads) == 1
    assert len(benchmark.measures()) == 20

    percsA = benchmark.percentiles()
    assert len(percsA) == 3
    percsB = benchmark.percentiles(include=[70,90])
    assert len(percsB) == 2

    percs_out=StringIO.StringIO()
    ezbench.report.print_percentiles(percsB,out=percs_out)
    assert len(str(percs_out.getvalue()).split("\n")) == 2

    percs100 = benchmark.percentiles(include=[100])
    assert percs100[100] == top, "max and perc100 do not match"

    medianPerc = benchmark.percentiles(include=[50])
    assert medianPerc[50] == benchmark.median() , "median and perc 50 do not match"

def test_save_and_load():
    benchmark = ezbench.Benchmark()
    proc = SingleProcess()
    for x in range(0,12):
        result = benchmark.measure("SingleProcess.do_it", 
                          lambda: proc.do_it())
    save_here = "./test/results/test_save_and_load.csv"
    if os.path.exists(save_here):
        os.remove(save_here)
    benchmark.save(save_here)
    assert os.path.exists(save_here)

    from_log = ezbench.Benchmark()
    from_log.load(save_here)

    assert len(from_log.measures()) == len(benchmark.measures())
    assert from_log.median() == benchmark.median()
    assert from_log.maximum() == benchmark.maximum()
    assert from_log.percentiles() == benchmark.percentiles()

def test_link():
    benchmark = ezbench.Benchmark()
    benchmark.link(SingleProcess.do_it)
    proc = SingleProcess()
    for x in range(0,5):
        result = proc.do_it()
        assert result == x+1, "Sample result does not match the original"
    top = benchmark.maximum()
    assert top < 1.5
    assert len(benchmark.threads) == 1
    assert len(benchmark.measures()) == 5


if __name__ == "__main__":
    #test_single_process()
    #test_save_and_load()
    test_link()
