import itertools
# test words
words = ['a', 'b', 'c', 'd', 'e', 'f']

#recursive function
def rec(words, skips, grams):
    if len(words) != skips + grams:
        print "Error, window doesnt equal skips plus grams"
        exit(0)
    else:
        if skips == 0:
            return [words]
        if grams == 0:
            return []

# return all the combinations of n size from the mid
def choose(n, mid):
    return list(itertools.combinations(mid, n))


# get a k-skip n-gram from the list of words
def getSkipGram(words, k, n):
    window = n - 2 + k
    l = len(words)
    ret = []
    for i in range(0, l - window - 1):
        beg, mid, end = words[i], words[i+1: i + window + 1], words[i + window + 1]
        opt = choose( n -2, mid)
        for l in opt:
            temp = [beg]
            temp.extend(l)
            temp.append(end)
            ret.append(temp)

    return ret

# this function gets all the skip grams
def getAllSkipGram(words, size=1024):
    l = len(words)
    ret = []
    for gram in range(2, l+1):
        for skip in range(0, l - gram + 1):
            if len(ret) >= size:
                return ret
            t = getSkipGram(words,skip,gram)
            if t != []:
               ret.extend(t)
    return ret