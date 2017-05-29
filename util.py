def unitize(vector):
    s = sum(vector)
    return [x/s for x in vector]