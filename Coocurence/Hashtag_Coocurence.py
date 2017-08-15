import array
import gc
from collections import Counter
import numpy as np
from sklearn.cluster import KMeans

from Library import Database

try:
    from sklearn.manifold import TSNE
    import matplotlib.pyplot as plt
    import matplotlib.cm as cm
except ImportError:
    print("Please install sklearn, matplotlib, and scipy to visualize embeddings.")

# get the tweets hashtag relationships if the hashtag occurs with another hashtag in the same tweet atleast once.

cur = Database.get_Cur()
query = "SELECT tweet_id, hashtag_id, count(tweet_id) FROM tweets_hashtags WHERE tweet_id in (SELECT id from train) GROUP BY tweet_id,hashtag_id HAVING COUNT (tweet_id) > 1"
cur.execute(query)

# create a list of hashtags (given indicies) for each unique tweet id
counter = Counter()
tweetshashtags = {}
count = 0
hashtag_indicies = {}
for row in cur:
    tweet_id = row[0]
    hashtag_id = row[1]
    if hashtag_id not in hashtag_indicies and count < 35000:
        hashtag_indicies[hashtag_id] = count
        count += 1
    if hashtag_id in hashtag_indicies:
        counter[hashtag_indicies[hashtag_id]] += 1
        if tweet_id in tweetshashtags:
            tweetshashtags[tweet_id].append(hashtag_indicies[hashtag_id])
        else:
            tweetshashtags[tweet_id] = [hashtag_indicies[hashtag_id]]

# create a graph (in matrix form)  of the coocurence of each hashtag
graph = []
print count
for i in range(count):
    arr = array.array('H')
    arr.append(0)#np.int16(0))
    graph.append(arr * count)
    # print type(graph[i][0])
max = 0
for tweet_id, hashtags in tweetshashtags.items():
    if len(hashtags) > 1:
        for hashtag1 in hashtags:
            for hashtag2 in hashtags:
                if hashtag1 != hashtag2:  # actually, might be ok if they are the same - just results in coutn of times used
                    graph[hashtag1][hashtag2] += 1#np.uint16(1)
                    if max < graph[hashtag1][hashtag2]:
                        max = graph[hashtag1][hashtag2]
                        # print type(graph[hashtag1][hashtag2])

                        # for i in range(len(graph)):
                        # for j in range(len(graph[i])):
                        # graph[i][j] = max - graph[i][j]
del (tweetshashtags)
gc.collect()

# def removeUnlinked(graph):
#    for x,y in

from sklearn.cluster import AffinityPropagation

a = AffinityPropagation(affinity='precomputed')
predictions = a.fit_predict(graph)
cluster = {}
for index, i in enumerate(predictions):
    if i in cluster:
        cluster[i].append(index)
    else:
        cluster[i] = [index]
num_clusters=len(cluster)
l = [0 for x in range(len(graph))]
for cluster_ind in cluster.keys():
    for x in cluster[cluster_ind]:
        l[x] = cluster_ind


'''
cluster_num = 20
print "starting clustering"
km = KMeans(n_clusters=cluster_num, random_state=0)
# km.fit(graph.values())
print "fitting"
km.fit(graph)
print "getting labels"
l = km.labels_.tolist()
'''
'''

start = [[0] * len(graph)]


x = xmeans(data=graph, initial_centers=start)
x.process()
c = x.get_clusters()
num_clusters = len(c)
l = {}
for i in range(len(c)):
    for j in range(len(c[i])):
        l[c[i][j]] = i
'''

hashtag_clusters = {}
search = Database.get_Cur()
hashtag_ids = {}
for hashtag_id, index in hashtag_indicies.items():
    search.execute("""SELECT hashtag FROM hashtags WHERE id='%s'""", [hashtag_id])
    hashtag = search.fetchone()[0]
    hashtag_ids[hashtag_id] = hashtag
    hashtag_clusters[hashtag] = l[index]

# print hashtag_clusters


ancur = Database.get_Cur()
ancur.execute("SELECT id, hashtag, annotation FROM annotated_hashtags ORDER BY annotation DESC ")
annotated_hashtags = ancur.fetchall()
notable_hashtags = [i[1] for i in annotated_hashtags]
notable_hashtags_clusters = {}

clusters = {}
for hashtag, label in hashtag_clusters.items():
    print hashtag
    if hashtag in notable_hashtags:
        notable_hashtags_clusters[hashtag] = label
    if label in clusters:
        clusters[label].append(hashtag)
    else:
        clusters[label] = [hashtag]
print notable_hashtags
print notable_hashtags_clusters

clusterl = [0] * num_clusters
clusterc = [0] * num_clusters
outstrlist = []
for label, hashtags in clusters.items():
    outstrlist.append("Cluster " + str(label) + ", (size = " + str(len(hashtags)) + "): ")
    outstrlist.append(hashtags)

for i in annotated_hashtags:
    if i[1] in notable_hashtags_clusters:
        if str(i[2]) == 'l':
            clusterl[notable_hashtags_clusters[i[1]]] += 1
        elif str(i[2]) == 'c':
            clusterc[notable_hashtags_clusters[i[1]]] += 1
        outstrlist.append(str(i[1]) + '(' + str(i[2]) + '): ' + str(notable_hashtags_clusters[i[1]]))
    else:
        outstrlist.append(str(i[1]) + '(' + str(i[2]) + '): Not found')

outstrlist.append("Prolife annotated hashtags: " + ", ".join([str(x) for x in clusterl]))
outstrlist.append("Prochoice annotated hashtags: " + ", ".join([str(x) for x in clusterc]))

f = open('CoocurenceResultsTrain', 'w')

f.writelines('\n'.join([str(x) for x in outstrlist]))
f.close()






def affinityToAdjacency(graph):
    size = len(graph)
    ret = np.zeros((size, size))

    for x in range(size):
        vertex = graph[x]
        s = sum(vertex)
        for y in range(size):
            ret[x][y] = vertex[y] / s
    return ret



try:
    from sklearn.manifold import TSNE
    import matplotlib.pyplot as plt
    import matplotlib.cm as cm
    import matplotlib.patches as mpatches
except ImportError:
    print("Please install sklearn, matplotlib, and scipy to visualize embeddings.")

print "Graphing"

# reduce dimensionality
m = affinityToAdjacency(graph)
tsne = TSNE(perplexity=30, n_components=2, init='pca', n_iter=50000)
low_dims = tsne.fit_transform(m)

color_num = num_clusters

color_num = 2
for clusternum, hashtag_indicies in clusters.items():
    if len(hashtag_indicies) >= len(graph) / 20:
        color_num += 1



x = np.arange(color_num)
ys = [i + x + (i * x) ** 2 for i in range(color_num)]
colors = cm.rainbow(np.linspace(0, 1, len(ys)))

plt.figure(figsize=(18, 18))  # in inches
lim = 200

top = [x for x, y in counter.most_common(lim)]

legends = {}

for clusternum, hashtag_indicies in clusters.items():
    if len(hashtag_indicies) < len(graph) / 20:
        clusternum = -1
    #if clusternum < 10:
        #patch = mpatches.Patch(color=colors[clusternum], label='Cluster ' + str(clusternum))
        #plt.legend(handles=[patch], loc=clusternum + 1)
    for j in hashtag_indicies:
        mark = 'o'
        l = ''
        # print hashtag_clusters[hashtag_ids[i]]

        z = plt.scatter(low_dims[j][0], low_dims[j][1], color=colors[clusternum + 1], marker=mark)
        if clusternum + 1 not in legends:
            legends[clusternum + 1] = z
        if lim > 0 and labels[j] in top:
            l = labels[j].decode('UTF-8', 'replace').encode('ascii', 'replace')
            lim -= 1

        # l = ''
        plt.annotate(l,
                     xy=(low_dims[j][0], low_dims[j][1]),
                     xytext=(5, 2),
                     textcoords='offset points',
                     ha='right',
                     va='bottom')

legend_labels = ["Outlier Cluster"] + ['Cluster ' + str(x) for x in legends.keys()]
plt.legend(tuple(legends.values()), tuple(legend_labels), scatterpoints=1, loc='lower left', ncol=3, fontsize=8)
# print cents

plt.savefig(filename + '.png')



















exit(0)

m = graph
tsne = TSNE(perplexity=30, n_components=2, init='pca', n_iter=50000)
low_dims = tsne.fit_transform(m)
color_num = num_clusters
x = np.arange(color_num)
ys = [i + x + (i * x) ** 2 for i in range(color_num)]
colors = cm.rainbow(np.linspace(0, 1, len(ys)))

plt.figure(figsize=(18, 18))  # in inches
lim = 200

for i, j in hashtag_indicies.items():
    mark = 'o'
    l = ''
    if j < 0:
        mark = 's'
    print hashtag_clusters[hashtag_ids[i]]
    plt.scatter(low_dims[j][0], low_dims[j][1], color=colors[hashtag_clusters[hashtag_ids[i]]], marker=mark)
    if lim > 0:
        l = hashtag_ids[i]
        lim -= 1

    # l = ''
    plt.annotate(l,
                 xy=(low_dims[j][0], low_dims[j][1]),
                 xytext=(5, 2),
                 textcoords='offset points',
                 ha='right',
                 va='bottom')

# print cents

plt.savefig('CoocurenceResultsTrain.png')
