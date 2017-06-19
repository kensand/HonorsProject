from Library import Visualize, Database, Dictionary
from scipy import spatial
import pylab
import numpy


size = 100
ratio = 0

hashtag1 = "hillary2016"
hashtag2 = 'trump2016'


cur = Database.get_Cur()
search = Database.get_Cur()

cur.execute("""SELECT id FROM hashtags WHERE hashtag=%s""", [hashtag1])

h1_id = cur.fetchone()[0]
cur.execute("""SELECT id FROM hashtags WHERE hashtag=%s""", [hashtag2])

h2_id = cur.fetchone()[0]


cur.execute("""SELECT hashtag_embedding FROM hashtag_embeddings WHERE hashtag_id = %s""", [h1_id])
h1_emb = cur.fetchone()[0]
cur.execute("""SELECT hashtag_embedding FROM hashtag_embeddings WHERE hashtag_id = %s""", [h2_id])
h2_emb = cur.fetchone()[0]

cur.execute("""SELECT hashtag_id, hashtag_embedding FROM hashtag_embeddings ORDER BY use DESC""")
labeled_embeddings = {}
i=0
counted =0
avg_dist = 0.
dists = []
for r in cur:

    #r = cur.fetchone()
    #print r

    if r is not None and r[0] != h2_id and r[0] != h1_id:
        search.execute("SELECT hashtag FROM hashtags WHERE id = %s", [r[0]])
        s = search.fetchone()[0]
        d1 = 1 - spatial.distance.cosine(h1_emb, r[1])
        d2 = 1 - spatial.distance.cosine(h2_emb, r[1])

        if d1 < 1.0 and d2 < 1.0 and (abs(d1/d2) < ratio or abs(d2/d1) > ratio):# and abs(d2 - d1) > 0.25:
            labeled_embeddings[s.decode('utf-8').encode('ascii', 'replace')] = [d1, d2]
            i+=1
            counted += 1
            avg_dist += abs(d2 - d1)
            dists.append(abs(d2 - d1))
    elif r is None:
        i+=1

print labeled_embeddings



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
plot_with_labels(numpy.array(labeled_embeddings.values()[:size]), numpy.array(labeled_embeddings.keys()[:size]),hashtag1, hashtag2, "images/hashtag_axis_embeddings.png")

print "Average difference of cosine distance from axis embeddings: " + str(avg_dist / counted)
print "Standard deviation of differences of cosine distances: " + str(numpy.std(dists))