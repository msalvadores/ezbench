import sys

def print_percentiles(percs,out=sys.stdout):
    ps = map(lambda perc: "%d%%: %.5f"%(perc,percs[perc]),
             sorted(percs.keys(),reverse=True))
    out.write("\n".join(ps))
    out.write("\n")
    out.flush()
