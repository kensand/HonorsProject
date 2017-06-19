import math
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