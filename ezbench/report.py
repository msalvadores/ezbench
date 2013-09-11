import sys
import time
import StringIO
import curses
import threading
import pdb

def subgroups(data):
    res = []
    total = data["total"]
    for k in sorted(data.keys()):
        if k == "total":
            continue
        perc = (data[k]/total)*100
        res.append("%s: %.3f (%.1f%%)"%(k,data[k],perc))
    return "    ".join(res)

def print_percentiles(percs,out=sys.stdout):
    ps = map(lambda perc: "%d%%: %.5f\t\t%s"%(perc,percs[perc]["total"],subgroups(percs[perc])),
             sorted(percs.keys(),reverse=True))
    out.write("\n".join(ps))
    out.write("\n")
    out.flush()

class ShowThread(threading.Thread):
    def __init__(self,benchmark,perc_points=None):
        super(ShowThread,self).__init__()
        self.screen = None
        self.continue_thread = True
        self.benchmark = benchmark
        self.perc_points = perc_points


    def run(self):
        self.screen = curses.initscr()
        curses.noecho()
        curses.cbreak()
        curses.start_color()
        self.screen.keypad(1)
        self.screen.border(0)
        try:
            curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
            curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)
            curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
            curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK)
            self.screen.addstr(1, 2, "Benchmark in progress...", curses.color_pair(3) | curses.A_BOLD)
            self.screen.refresh()

            while self.continue_thread:
                data = self.nshow()
                lines = data.getvalue().split("\n")
                first_line = 3
                for x in range(len(lines)):
                    c = curses.color_pair(1)
                    if lines[x].startswith("All") or lines[x].startswith("Group"):
                        c|= curses.A_BOLD
                    self.screen.addstr(x + first_line, 2 ,lines[x], c)
                self.screen.refresh()
                time.sleep(1.2)
        except Exception, exc:
            print exc
        curses.nocbreak()
        self.screen.keypad(0)
        curses.echo()
        curses.endwin()

    def end(self):
        self.continue_thread = False
        time.sleep(1.5)

    def nshow(self):
        out_str = StringIO.StringIO()
        show(self.benchmark,out=out_str,perc_points=self.perc_points)
        return out_str


def show(benchmark,out=sys.stdout,perc_points=None):
    if perc_points is None:
        perc_points = [75,85,95]
    percs = benchmark.percentiles(include=perc_points)
    out.write("All groups median (%.3f) worst (%.3f) samples (%d)\n"\
            %(benchmark.median()["total"],benchmark.maximum()["total"],
              len(benchmark.measures())))
    print_percentiles(percs,out=out)
    for g in benchmark.groups():
        out.write("Group: %s median (%.3f) worst (%.3f) samples (%d)\n"\
                %(g,benchmark.median(group=g)["total"],benchmark.maximum(group=g)["total"],
                    len(benchmark.measures(group=g))))
        percs = benchmark.percentiles(group=g,include=perc_points)
        print_percentiles(percs,out=out)
