def unitize(vector):
    s = sum([x*x for x in vector])
    if s== 0:
        s=1
    return [x/s for x in vector]