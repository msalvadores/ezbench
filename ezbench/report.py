import sys

def print_percentiles(percs,out=sys.stdout):
    ps = map(lambda perc: "%d%%: %.3f"%(perc,percs[perc]),
             sorted(percs.keys(),reverse=True))
    out.write("\n".join(ps))
    out.flush()
