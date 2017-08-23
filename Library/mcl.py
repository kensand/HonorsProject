#!/usr/bin/env python

import sys
import numpy as np
import time
from optparse import OptionParser
import logging


def normalize(A):
    column_sums = A.sum(axis=0)
    new_matrix = A / column_sums[np.newaxis, :]
    return new_matrix


def inflate(A, inflate_factor):
    return normalize(np.power(A, inflate_factor))


def expand(A, expand_factor):
    return np.linalg.matrix_power(A, expand_factor)


def add_diag(A, mult_factor):
    return A + mult_factor * np.identity(A.shape[0])


def get_clusters(A):

    print A
    clusters = []
    for i, r in enumerate((A > 0).tolist()):
        if r[i]:
            clusters.append(A[i, :] > 0)

    clust_map = {}
    for cn, c in enumerate(clusters):
        for x in [i for i, x in enumerate(c) if x]:
            clust_map[cn] = clust_map.get(cn, []) + [x]
    return clust_map


def stop(M, i):
    if i % 5 == 4:
        m = np.max(M ** 2 - M) - np.min(M ** 2 - M)
        if m == 0:
            logging.info("Stop at iteration %s" % i)
            return True

    return False


def mcl(M, expand_factor=2, inflate_factor=2, max_loop=10, mult_factor=1):
    #M = add_diag(M, mult_factor)
    M = normalize(M)

    for i in range(max_loop):
        logging.info("loop %s" % i)
        M = inflate(M, inflate_factor)
        M = expand(M, expand_factor)
        if stop(M, i): break

    clusters = get_clusters(M)
    return M, clusters