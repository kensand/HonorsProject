from Library import Visualize, Database, Dictionary
from scipy import spatial
import pylab
import numpy
import time


size = 10000
ratio = 0

hashtags = [
    #'trumptrain',
    #'trump2016',
    #"hillary2016",
    'zika'
]

axis1 = Database.get_Cur()
axis2 = Database.get_Cur()
cur = Database.get_Cur()
search = Database.get_Cur()



axis1.execute("""SELECT hashtag_id, hashtag_embedding FROM hashtag_embeddings""")
embeddings = axis1.fetchall()
labeled_embeddings = []
for r in embeddings:
    search.execute("SELECT hashtag FROM hashtags WHERE id = %s", [r[0]])
    s = search.fetchone()[0]
    labeled_embeddings.append([s, r[1]])
del embeddings
axis_embeddings = []
if len(hashtags) > 0:
    for i in hashtags:
        found = False
        for r in labeled_embeddings:
            if i == r[0]:
                axis_embeddings.append(r)
                found = True
                break
        if not found:
            print "Error, do not have embedding for #'" + i + "'"
else:
    axis_embeddings






labeled_embeddings = labeled_embeddings


axis2.execute("""SELECT hashtag_id, hashtag_embedding FROM hashtag_embeddings""")

def getHashRel(h1_emb, h2_emb, labeled_embedding_list):

    x = []
    y = []
    for r in labeled_embedding_list:
        d1 = 1 - spatial.distance.cosine(h1_emb, r[1])
        d2 = 1 - spatial.distance.cosine(h2_emb, r[1])
        x.append(d1)
        y.append(d2)



    return x,y
graph = {}
print 'Started'
count1 = 0
k = len(axis_embeddings)
l = len(labeled_embeddings[:50])
unlabeled = [x[1] for x in labeled_embeddings]
for row1 in axis_embeddings:
    id1 = row1[0]
    emb1 = row1[1]
    tmp = {}
    count2 = 0
    #axis2.execute(axis2.query)
    for row2 in labeled_embeddings[:l]:

        id2 = row2[0]
        emb2 = row2[1]
        x,y = getHashRel(emb1, emb2, labeled_embeddings)
        # print x
        # print len(y)
        m, b = pylab.polyfit(x, y, 1)
        if m > 1.0 or m < -1.0:
            m = 1/m
        tmp[id2] = m
        count2 += 1
        print '    ' +str(count2) + '/' + str(l)

        #if count2 % 10 == 1:
            #print str(count2 + count1 * k) + '/' + str(k*l) + ', ' + id1 + '-->' + id2 + ': ' + str(m)

    graph[id1] = tmp
    del tmp
    count1 += 1
    print str(count1) + '/' + str(k)

import collections
for key in graph.keys():
    graph[key] = collections.Counter(graph[key]).most_common()

for key in graph.keys():
    print key
    print graph[key]



'''

try:
    from sklearn.manifold import TSNE
    import matplotlib.pyplot as plt
except ImportError:
    print("Please install sklearn, matplotlib, and scipy to visualize embeddings.")


def plot_with_labels(low_dim_embs, labels, xlabel, ylabel, filename='word_embeddings.png'):
    assert low_dim_embs.shape[0] >= len(labels), "More labels than embeddings"
    plt.figure(figsize=(18, 18))  # in inches
    for i, label in enumerate(labels):
        x, y = low_dim_embs[i, :]
        plt.scatter(x, y)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.annotate(label,
                     xy=(x, y),
                     xytext=(5, 2),
                     textcoords='offset points',
                     ha='right',
                     va='bottom')

    plt.savefig(filename)

#print labeled_embeddings.values()
x = [d[0] for d in labeled_embeddings.values()]
y = [d[1] for d in labeled_embeddings.values()]
#print x
#print len(y)
m,b = pylab.polyfit(x, y, 1)

print 'm = ' + str(m)
print 'b = ' + str(b)
plot_with_labels(numpy.array(labeled_embeddings.values()[:size]), numpy.array(labeled_embeddings.keys()[:size]),hashtag1, hashtag2, "hashtag_axis_embeddings.png")

print "Average difference of cosine distance from axis embeddings: " + str(avg_dist / counted)
print "Standard deviation of differences of cosine distances: " + str(numpy.std(dists))

'''