import sys

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

def show(benchmark,out=sys.stdout,perc_points=None):
    if perc_points is None:
        perc_points = [75,85,95]
    percs = benchmark.percentiles(include=perc_points)
    out.write("All groups median (%.3f) worst (%.3f)\n"\
            %(benchmark.median()["total"],benchmark.maximum()["total"]))
    print_percentiles(percs,out=out)
    for g in benchmark.groups():
        out.write("Group: %s median (%.3f) worst (%.3f)\n"\
                %(g,benchmark.median(group=g)["total"],benchmark.maximum(group=g)["total"]))
        percs = benchmark.percentiles(group=g,include=perc_points)
        print_percentiles(percs,out=out)
