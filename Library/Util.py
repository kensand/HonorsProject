import math
import numpy
from scipy import spatial


def unitize(vector):
    s = math.sqrt(sum([x*x for x in vector]))
    if s == 0.:
        s = 1
    return [x/s for x in vector]


def normalize(vector):
    t = sum(vector)
    s = math.sqrt(abs(t))
    if s == 0.:
        return [0]*len(vector)
    return [x/s for x in vector]


def scalar_vec_mult(scalar, vec):
    return [x * scalar for x in vec]


def sum_vec(v1, v2):
    return [x + y for x, y in zip(v1,v2)]


def scale(vector, Min=-1, Max=1):
    l = min(vector)
    h = max(vector)
    r = h - l
    s = (Max - Min) / r
    o = Min - (s*l)
    return [x * s + o for x in vector]


import math
def cosine_similarity(x,y):
    assert len(x) == len(y)
    dot = 0
    magx = 0
    magy = 0
    for i in range(len(x)):
        #print x[i]
        #print y[i]
        dot += x[i] * y[i]
        magx += x[i] ** 2
        magy += y[i] ** 2
    return (dot/ (math.sqrt(magx) * math.sqrt(magy)))
# assumes that it is given a dictionary of points in N dimensions.
# calculates average and std dev for each dim, removes points that have
# atleast one dimension greater than the standard dev mult times the std dev

def remove_outliers(labeled_points, stddevmult=2):
    d = dict()

    for point in labeled_points.values():
        for i in range(len(point)):
            if i in d:
                d[i].append(point[i])
            else:
                d[i] = [point[i]]
    avgs = dict()
    devs = dict()

    for k, l in d.items():
        avgs[k] = numpy.mean(l)
        devs[k] = numpy.std(l)

    ret = {}
    for label,point in labeled_points.items():
        add = True
        for i in range(len(point)):
            if abs(avgs[i] - point[i]) > stddevmult * devs[i]:
                add = False
                break
        if add:
            ret[label] = point

    return ret


def mean(arr):
    return sum(arr) / len(arr)


