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
