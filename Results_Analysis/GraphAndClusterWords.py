from pyclustering.cluster.xmeans import xmeans
from sklearn.cluster import KMeans
from Library import Database, Util
from scipy import spatial
import numpy
try:
    from sklearn.manifold import TSNE
    import matplotlib.pyplot as plt
    import matplotlib.cm as cm
except ImportError:
    print("Please install sklearn, matplotlib, and scipy to visualize embeddings.")


# get the graph
cluster_num = 2
kmeans = True

conn = Database.get_Conn()
cur = conn.cursor()
search = conn.cursor()
cur.execute("""SELECT word_id, word_embedding FROM word_embeddings""")
graph = {}
for i in cur:
    if cur.rownumber > 1000:
        break
    graph[i[0]] = i[1]

sims = {}
indicies = {}
index = 0
l = str(len(graph))
for axiskey, axisemb in graph.items():
    arr = []
    for key, emb in graph.items():
        arr.append(Util.cosine_similarity(emb, axisemb))
    sims[axiskey] = arr
    indicies[index] = axiskey
    index+=1
    print str(index) + '/' + l

del graph
graph = sims


if kmeans:

    km = KMeans(n_clusters=cluster_num, random_state=0)
    km.fit(graph.values())
    cluster_lables = km.labels_.tolist()



    cents = km.cluster_centers_
else:
    cluster_lables = [0] * len(graph)
    start = [[0] * len(graph)]

    print graph
    x = xmeans(data=graph.values(), initial_centers=start)
    x.process()
    c = x.get_clusters()

    cents = x.get_centers()
    print cents
    #print cluster_lables
    for i in range(len(c)):
        for j in c[i]:
            cluster_lables[j] = i

    cluster_num = len(c)



clusters = {}
k = graph.keys()
for i in range(len(cluster_lables)):
    if cluster_lables[i] in clusters:
        clusters[cluster_lables[i]].append(k[i])
    else:
        clusters[cluster_lables[i]] = [k[i]]

lables = {}

for i in k:
    search.execute("""SELECT word from dictionary WHERE word_id = %s""", [int(i)])
    s = search.fetchone()[0]
    lables[i] = s.decode('UTF-8', 'replace').encode('ascii', 'replace')
    #lables[i]= ''



for i,j in enumerate(cents):
    cluster_lables.append(i)
    graph[i * -1] = j
    lables[i * -1] = 'Cluster Center ' + str(i+1)

plt.figure(figsize=(18, 18))  # in inches
m = graph.values()
tsne = TSNE(perplexity=30,  n_components=2, init='pca', n_iter=50000)
low_dims = tsne.fit_transform(m)
color_num = cluster_num
x = numpy.arange(color_num)
ys = [i+x+(i*x)**2 for i in range(color_num)]
colors = cm.rainbow(numpy.linspace(0, 1, len(ys)))
totalcents = 0
count = 0
for i,j in enumerate(cents):
    for k, l in enumerate(cents):
        if k != i:
            totalcents += spatial.distance.euclidean(j,l)
            count += 1

if count == 0:
    count = 1
centavg = totalcents / count


count = 1
for key, val in clusters.items():
    mem = []
    for ind in val:
        mem.append(lables[ind])
    print "Cluster " + str(count) + ', size = ' + str(len(mem))
    print ", ".join(mem)
    count+=1
print "Average distance between centers of clusters: " + str(centavg)





#if len(cents) > 1:
    #print spatial.distance.euclidean(cents[0], cents[1])


for i, j in enumerate(graph.keys()):
    plt.scatter(low_dims[i][0], low_dims[i][1], color=colors[cluster_lables[i]])
    l = lables[graph.keys()[i]]
    #l = ''
    plt.annotate(l,
                 xy=(low_dims[i][0], low_dims[i][1]),
                 xytext=(5, 2),
                 textcoords='offset points',
                 ha='right',
                 va='bottom')

#print cents

l = tsne.fit_transform(cents)
#print l
plt.savefig('graph_words.png')
exit(0)
for i,j in enumerate(l):


    plt.scatter(j[0], j[1], color=colors[i])
    plt.annotate('Cluster Center ' + str(i),
                 xy=(j[0], j[1]),
                 xytext=(5, 2),
                 textcoords='offset points',
                 ha='right',
                 va='bottom')



