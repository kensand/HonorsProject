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


schema = """set3."""
# get the graph
cluster_num = 2
kmeans = True

conn = Database.get_Conn()
cur = conn.cursor()
search = conn.cursor()
search_string = """SELECT hashtag_id, hashtag_embedding FROM """ + schema + """hashtag_embeddings"""
#print search_string
cur.execute(search_string)
graph = {}
for i in cur:
    if cur.rownumber >400:
        break
    #print i[0]
    #print i[1]
    graph[i[0]] = i[1]


sims = {}
indicies = {}
index = 0
l = str(len(graph))
for axiskey, axisemb in graph.items():
    arr = []
    for key, emb in graph.items():
        #print emb
        #print axisemb
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
    search.execute("""SELECT hashtag from hashtags WHERE id = %s""", [int(i)])
    s = search.fetchone()[0]
    lables[i] = s.decode('UTF-8', 'replace').encode('ascii', 'replace')
    #lables[i]= ''



for i,j in enumerate(cents):
    cluster_lables.append(i)
    graph[(i + 1) * -1] = j
    lables[(i + 1) * -1] = 'Cluster Center ' + str(i+1)


m = graph.values()
tsne = TSNE(perplexity=30,  n_components=2, init='pca', n_iter=50000)
low_dims = tsne.fit_transform(m)
color_num = 2*cluster_num
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



count = 0
stddevs = []
for key, val in clusters.items():
    mem = []
    m = []
    for ind in val:
        mem.append(lables[ind])
        m.append(graph[ind])
    pr = []
    dists = [spatial.distance.euclidean(x,cents[count]) for x in m]
    #print cents[count]*len(m)
    s = numpy.std(dists)
    stddevs.append(s)
    for h, emb in zip(mem, m):
        #print str([emb, cents[count]])
        if True or spatial.distance.euclidean(emb, cents[count]) < s* 22:
            pr.append(h)
    print "Cluster " + str(count) + ', size = ' + str(len(mem)) + ', stdev = ' + str(s) #+ ', within = ' + str(len(pr))
    print ", ".join(pr)
    count+=1
print "Average distance between centers of clusters: " + str(centavg)





#if len(cents) > 1:
    #print spatial.distance.euclidean(cents[0], cents[1])

print lables

plt.figure(figsize=(18, 18))  # in inches
lim = 200
for i, j in enumerate(graph.keys()):
    mark = 'o'
    l = ''
    if j < 0:
        mark = 's'
    plt.scatter(low_dims[i][0], low_dims[i][1], color=colors[cluster_lables[i]], marker=mark)
    if (lim > 0 and i in graph.keys()) or j < 0:
        l = lables[j]
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
        l = lables[j]
    plt.scatter(low_dims[i][0], low_dims[i][1], color=colors[cluster_lables[i]], marker=mark)
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
for i,j in enumerate(l):


    plt.scatter(j[0], j[1], color=colors[i])
    plt.annotate('Cluster Center ' + str(i),
                 xy=(j[0], j[1]),
                 xytext=(5, 2),
                 textcoords='offset points',
                 ha='right',
                 va='bottom')



