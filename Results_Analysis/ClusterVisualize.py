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


schema = """"""
# get the graph
cluster_num = 2
kmeans = True

conn = Database.get_Conn()
cur = conn.cursor()
search = conn.cursor()
search_string = """SELECT index, hashtag, relationships FROM """ + schema + """hashtag_relationships"""
#print search_string
cur.execute(search_string)
graph = {}
hashtags = {}
for i in cur:
    if cur.rownumber >40000:
        break
    #print i[0]
    #print i[1]
    graph[i[0]] = i[2]
    hashtags[i[0]] = i[1]




cluster_labels = {}
if kmeans:

    km = KMeans(n_clusters=cluster_num, random_state=0)
    km.fit(graph.values())
    l = km.labels_.tolist()
    for i,j in enumerate(graph.keys()):
        cluster_labels[j] = l[i]


    cents = km.cluster_centers_
else:
    start = [[0] * len(graph)]

    print graph
    x = xmeans(data=graph.values(), initial_centers=start)
    x.process()
    c = x.get_clusters()

    cents = x.get_centers()
    print cents
    #print cluster_lables //TODO FIX the cluster_labels to use dict with key of hashtag index
    for i in range(len(c)):
        for j in c[i]:
            cluster_labels[j] = i

    cluster_num = len(c)








clusters = {}
for i,j in cluster_labels.items():
    if j in clusters:
        clusters[j].append(i)
    else:
        clusters[j] = [i]



count = 0
stddevs = []
for key, val in clusters.items():
    mem = []
    m = []
    for ind in val:
        mem.append(hashtags[ind])
        m.append(graph[ind])

    dists = [spatial.distance.euclidean(x,cents[count]) for x in m]
    #print cents[count]*len(m)
    s = numpy.std(dists)
    stddevs.append(s)
    print "Cluster " + str(count + 1) + ', size = ' + str(len(mem)) + ', stdev = ' + str(s) #+ ', within = ' + str(len(pr))
    print ", ".join(mem)
    count+=1


centavg = 0
for ind,i in enumerate(cents):
    graph[(ind +1) * -1] = i
    hashtags[(ind + 1) * -1] = "CLUSTER CENTER " + str(ind + 1)
    cluster_labels[(ind + 1) * -1] = ind
    for j in cents:
        centavg += spatial.distance.euclidean(i,j)
centavg /= len(cents)
print "Average distance between centers of clusters: " + str(centavg)


m = graph.values()
tsne = TSNE(perplexity=30,  n_components=2, init='pca', n_iter=50000)
low_dims = tsne.fit_transform(m)
color_num = cluster_num
x = numpy.arange(color_num)
ys = [i+x+(i*x)**2 for i in range(color_num)]
colors = cm.rainbow(numpy.linspace(0, 1, len(ys)))



plt.figure(figsize=(18, 18))  # in inches
lim = 200

for i, j in enumerate(graph.keys()):
    mark = 'o'
    l = ''
    if j < 0:
        mark = 's'
    plt.scatter(low_dims[i][0], low_dims[i][1], color=colors[cluster_labels[j]], marker=mark)
    if (lim > 0 and j in graph.keys()) or j < 0:
        l = hashtags[j]
        lim -= 1


    #l = ''
    plt.annotate(l,
                 xy=(low_dims[i][0], low_dims[i][1]),
                 xytext=(5, 2),
                 textcoords='offset points',
                 ha='right',
                 va='bottom')

#print cents

l = tsne.fit_transform(cents)
print schema
print len(graph)
#print l
plt.savefig('graphl.png')
plt.clf()
plt.figure(figsize=(18, 18))  # in inches
for i, j in enumerate(graph.keys()):
    mark='o'
    l = ''
    if j<0:
        mark = 's'
        l = hashtags[j]
    plt.scatter(low_dims[i][0], low_dims[i][1], color=colors[cluster_labels[j]], marker=mark)
    #l = lables[graph.keys()[i]]


    plt.annotate(l,
                 xy=(low_dims[i][0], low_dims[i][1]),
                 xytext=(5, 2),
                 textcoords='offset points',
                 ha='right',
                 va='bottom')

#print cents

l = tsne.fit_transform(cents)
#print l
plt.savefig('graphn.png')
exit(0)
