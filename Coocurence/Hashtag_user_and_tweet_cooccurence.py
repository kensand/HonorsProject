import networkx
import numpy as np
from Library import mcl

from Library import Database

try:
    from sklearn.manifold import TSNE
    import matplotlib.pyplot as plt
    import matplotlib.cm as cm
except ImportError:
    print("Please install sklearn, matplotlib, and scipy to visualize embeddings.")


test=True



if test:
    filename = 'UserTweetCooccurenceTest'
    output = 'TestUserTweetCoocurence'

else:
    filename = 'UserTweetCooccurenceTrain'
    output = 'TrainUserTweetCoocurence'

min_cluster_percent = .02
user_weight = 1
tweet_weight = 2
graph_size = 500
min_user_hashtags = 2
create_new_graph = False  #create_new_graph = True




#


def loadGraph(input):
    cur = Database.get_Cur()

    cur.execute("""SELECT index, count, hashtag, edges FROM """ + input + """ ORDER BY index ASC""")
    labels = {}
    from collections import Counter
    counter = Counter()
    graph = []
    for i in cur:
        index = i[0]
        count = i[1]
        hashtag = i[2]
        edges = i[3]
        edges[index] = count #includes affinity to itself
        graph.append(edges)
        counter[hashtag] = count
        labels[index] = hashtag
    return labels, counter, graph


import time


def saveGraph(graph, labels, counter, output):
    start = time.localtime()
    count = 0
    commit = True
    print 'Started at: ' + time.strftime("%b %d %Y %H:%M:%S", start)
    size = len(graph)

    cur = Database.get_Cur()
    cur.execute("""DROP TABLE IF EXISTS """ + output)
    cur.execute(
        """CREATE TABLE IF NOT EXISTS """ + output + """ (index int, count int, hashtag varchar(255), edges FLOAT[])""")
    buff = []
    for rownum, row in enumerate(graph):
        buff.append([rownum, counter[labels[rownum]], labels[rownum], row])
        if len(buff) > 1000:
            insert = 'INSERT INTO ' + output + ' (index, count, hashtag, edges) VALUES ' + ','.join(
                cur.mogrify('(%s, %s, %s, %s)', x) for x in buff)
            cur.execute(insert)
            del buff
            buff = []
        count += 1
        if count % 10000 == 1:  # int(incur.rowcount / 100) == 0:
            fin = ((time.mktime(time.localtime()) - time.mktime(start)) / size) * size
            fin += time.mktime(start)
            print str(count) + '/' + str(size) + " Est. completion time: " + time.strftime(
                "%b %d %Y %H:%M:%S", time.localtime(fin))
            if commit:
                cur.execute("""COMMIT""")
    insert = 'INSERT INTO ' + output + ' (index, count, hashtag, edges) VALUES ' + ','.join(
        cur.mogrify('(%s, %s, %s, %s)', x) for x in buff)
    cur.execute(insert)
    cur.execute("""COMMIT""")


def getGraph(graph_size, min_user_hashtags):
    userToTweets = {}
    tweetToHashtagIds = {}
    hashtagIdToHashtag = {}

    cur = Database.get_Cur()

    q1 = """SELECT user_id, id from tweets WHERE (issue='abortion')"""
    q2 = """SELECT tweet_id, hashtag_id from tweets_hashtags WHERE tweet_id in (SELECT id from tweets WHERE issue='abortion')"""
    q3 = """SELECT id, hashtag from hashtags"""


    '''
    if test:
        q1 = """SELECT user_id, id from test"""
        q2 = """SELECT tweet_id, hashtag_id from tweets_hashtags WHERE tweet_id in (SELECT id from test)"""
        q3 = """SELECT id, hashtag from hashtags"""
    else:
        q1 = """SELECT user_id, id from train"""
        q2 = """SELECT tweet_id, hashtag_id from tweets_hashtags WHERE tweet_id in (SELECT id from train)"""
        q3 = """SELECT id, hashtag from hashtags"""
    '''
    # get the tweets made by each user in abortion topic
    cur.execute(q1)

    for i in cur:
        if i[0] in userToTweets:
            userToTweets[i[0]].append(i[1])
        else:
            userToTweets[i[0]] = [i[1]]

    # get the hashtags used in each tweet in the abortion topic
    cur.execute(q2)

    for i in cur:
        if i[0] in tweetToHashtagIds:
            tweetToHashtagIds[i[0]].append(i[1])
        else:
            tweetToHashtagIds[i[0]] = [i[1]]

    # get the dictionary of hashtag ids to hashtags
    cur.execute(q3)

    for i in cur:
        hashtagIdToHashtag[i[0]] = i[1]

    # create a dictionary listing each use of a hashtag by a user

    userHashtags = {}

    from collections import Counter

    hashtag_counter = Counter()
    # for each user
    for user in userToTweets.keys():
        # start a list of each hashtag occurence from that user
        hashtags = []
        # for each tweet by that user
        for tweet in userToTweets[user]:
            # for each hashtag in that tweet
            if tweet in tweetToHashtagIds:
                for hashtag_id in tweetToHashtagIds[tweet]:
                    if hashtagIdToHashtag[hashtag_id] not in hashtags:
                        # add it to the list of hashtags for the user
                        hashtags.append(hashtagIdToHashtag[hashtag_id])

        # check that there are more than the minimum number of hashtags per user -
        # if there is only 1 hashtag, there are no coocurences with other hashtags
        # also count the number of occurences of each hashtag
        if len(hashtags) >= min_user_hashtags:
            for hashtag in hashtags:
                hashtag_counter[hashtag] += 1
            userHashtags[user] = hashtags

    counts = hashtag_counter.values()

    standard_dev = np.std(counts)
    avg = np.average(counts)
    d = np.floor(avg / standard_dev)
    graph_size = len([x for x in hashtag_counter.values() if x > (avg - (d) * standard_dev) ]) #x > 3 or
    # graph_size = len(hashtag_counter.keys())

    # give each hashtag a index
    # and the reverse
    indicies_hashtags = {}
    hashtag_indicies = {}
    for i, j in enumerate(hashtag_counter.most_common(graph_size)):
        hashtag_indicies[j[0]] = i
        indicies_hashtags[i] = j[0]

    # create a graph full of 0s

    graph = np.zeros((graph_size, graph_size))

    # increase the edge values for each coocurence of a hashtag by a user
    count = 0
    total = len(userHashtags.items())
    for i in userHashtags.items():
        print str(count) + '/' + str(total)
        count += 1
        user = i[0]
        hashtags = i[1]
        for hashtag1 in hashtags:
            if hashtag1 in hashtag_indicies:
                for hashtag2 in hashtags:
                    if hashtag2 in hashtag_indicies:  # and hashtag2 != hashtag1:
                        graph[hashtag_indicies[hashtag1]][hashtag_indicies[hashtag2]] += user_weight

    for tweet, hashtag_ids in tweetToHashtagIds.items():
        for hashtag_id1 in hashtag_ids:
            if hashtag_id1 in hashtagIdToHashtag:
                hashtag1 = hashtagIdToHashtag[hashtag_id1]
                if hashtag1 in hashtag_indicies:
                    for hashtag_id2 in hashtag_ids:
                        if hashtag_id2 in hashtagIdToHashtag:
                            hashtag2 = hashtagIdToHashtag[hashtag_id2]
                            if hashtag2 in hashtag_indicies and hashtag2 != hashtag1:
                                graph[hashtag_indicies[hashtag1]][
                                    hashtag_indicies[hashtag2]] += tweet_weight

    # print graph.tolist()

    print 'graph constructed'

    return indicies_hashtags, hashtag_counter, graph


def removeOverlap(clusters):
    cluster_labels = {}
    for i in clusters.items():
        clusternum = i[0]
        hash_list = i[1]
        for hash in hash_list:
            if hash in cluster_labels and clusternum not in cluster_labels[hash]:
                cluster_labels[hash].append(clusternum)
            else:
                cluster_labels[hash] = [clusternum]
    for hash, clusters in cluster_labels.items():
        cluster_labels[hash] = clusters.sort()

    out = {}
    cluster_count = len(cluster_labels)
    for clusternum, hash_list in clusters.items():
        for hash1 in hash_list:
            if len(cluster_labels[hash1]) > 1:
                matchinghashes = []
                for hash2 in hash_list:
                    if hash2 != hash1 and cluster_labels[hash1] == cluster_labels[hash2]:
                        if hash1 not in matchinghashes:
                            matchinghashes.append(hash1)
                        if hash2 not in matchinghashes:
                            matchinghashes.append(hash2)
                if len(matchinghashes) > 1:
                    # not sure how this will work
                    exit(0)

def affinityToAdjacency(graph):
    size = len(graph)
    ret = np.zeros((size, size))

    for x in range(size):
        vertex = graph[x]
        s = sum(vertex)
        for y in range(size):
            ret[x][y] = vertex[y] / s
    return ret



def getClusters(graph):

    print np.matrix(graph).shape

    m, cluster = mcl.mcl(M=np.array(graph) , expand_factor=2, inflate_factor=2.5, max_loop=1000,
                                             mult_factor=1)  # (G=inm, expand_factor = 2, inflate_factor = 2, max_loop = 10 , mult_factor = 1 )

    '''
    adj = affinityToAdjacency(graph)

    inm = networkx.from_numpy_matrix(np.matrix(adj))

    m, cluster = mcl.networkx_mcl(G=inm, expand_factor=2, inflate_factor=1.9, max_loop=10,
                                             mult_factor=1)  # (G=inm, expand_factor = 2, inflate_factor = 2, max_loop = 10 , mult_factor = 1 )
    #inf=1.78?
    '''

    '''
    from pyclustering.cluster.xmeans import xmeans
    start = [[0] * len(graph)]

    x = xmeans(data=graph, initial_centers=start)
    x.process()
    c = x.get_clusters()
    print c
    num_clusters = len(c)
    l = {}
    for i in range(len(c)):
        l[i] = []
        for j in range(len(c[i])):
            l[i].append(c[i][j])
    cluster = l
    '''
    '''
    from sklearn.cluster import KMeans
    k = KMeans(precompute_distances=)
    '''
    '''
    from sklearn.cluster import AffinityPropagation
    a = AffinityPropagation(affinity='precomputed', damping=0.5)
    predictions = a.fit_predict(graph)
    cluster = {}
    for index, i in enumerate(predictions):
        if i in cluster:
            cluster[i].append(index)
        else:
            cluster[i] = [index]
    '''



    '''
    from sklearn.cluster import SpectralClustering

    s = SpectralClustering(n_clusters=100, affinity='precomputed')

    delta = 0.1

    adj_graph = affinityToAdjacency(graph)

    predictions = s.fit_predict(graph)
    cluster = {}
    for index, i in enumerate(predictions):
        if i in cluster:
            cluster[i].append(index)
        else:
            cluster[i] = [index]


    '''
    '''


    from sklearn.cluster import DBSCAN

    dbscan = DBSCAN(metric='precomputed', n_jobs=-1, eps = 10, min_samples=10, leaf_size=100)

    predictions = dbscan.fit_predict(graph)
    cluster = {}
    for index, i in enumerate(predictions):
        if i in cluster:
            cluster[i].append(index)
        else:
            cluster[i] = [index]
    '''

    print cluster
    return cluster

from Library import Util

# main
if create_new_graph:
    labels, counter, graph = getGraph(graph_size, min_user_hashtags)
    labels, graph = Util.removeSubGraphs(graph=graph, labels=labels)
    saveGraph(graph, labels, counter, output)
else:
    labels, counter, graph = loadGraph(input=output)
clusters = getClusters(graph)

# clusters = removeOverlap(clusters)

print 'printing'

numclusters = len(clusters.keys())
ancur = Database.get_Cur()
if test:
    anq = "SELECT id, hashtag, annotation FROM test_annotated_hashtags ORDER BY annotation DESC "
else:
    anq = "SELECT id, hashtag, annotation FROM train_annotated_hashtags ORDER BY annotation DESC "

ancur.execute(anq)
annotated_hashtags = ancur.fetchall()
notable_hashtags = [i[1] for i in annotated_hashtags]
notable_hashtags_clusters = {}

clusterl = [0] * numclusters
clusterc = [0] * numclusters
outstrlist = []
for label, hashtags in clusters.items():
    if True: #len(hashtags) > 2:
        outstrlist.append("Cluster " + str(label) + ", (size = " + str(len(hashtags)) + "): ")
        outstrlist.append([labels[hashtag] for hashtag in hashtags])
        for hashtag in hashtags:
            notable_hashtags_clusters[labels[hashtag]] = label

for i in annotated_hashtags:
    if i[1] in notable_hashtags_clusters:
        if str(i[2]) == 'l':
            print notable_hashtags_clusters[i[1]]
            clusterl[notable_hashtags_clusters[i[1]]] += 1
        elif str(i[2]) == 'c':
            clusterc[notable_hashtags_clusters[i[1]]] += 1
        outstrlist.append(str(i[1]) + '(' + str(i[2]) + '): ' + str(notable_hashtags_clusters[i[1]]))
    else:
        outstrlist.append(str(i[1]) + '(' + str(i[2]) + '): Not found')



from sklearn.metrics.cluster import entropy


outstrlist.append("Prolife annotated hashtags: " + ", ".join([str(x) for x in clusterl]))
outstrlist.append("Entropy = " + str(entropy(clusterl)))
outstrlist.append("Prochoice annotated hashtags: " + ", ".join([str(x) for x in clusterc]))
outstrlist.append("Entropy = " + str(entropy(clusterc)))
outstrlist.append("TOTAL ENTROPY = "  + str((entropy(clusterl) * sum(clusterl) + entropy(clusterc) * sum(clusterc))/(sum(clusterc) + sum(clusterl))))

#outstrlist.append(str(affinityToAdjacency(graph).tolist()))

f = open(filename, 'w')

f.writelines('\n'.join([str(x) for x in outstrlist]))
f.close()
#exit(0)

'''
import matplotlib.pyplot as plt
import networkx as nx
G2 = nx.from_numpy_matrix(np.matrix(graph))
nx.draw_circular(G2)
plt.axis('equal')
plt.show()
'''

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
#m = graph
tsne = TSNE(perplexity=30, n_components=2, init='pca', n_iter=50000)
low_dims = tsne.fit_transform(m)

color_num = numclusters
color_map = {}
color_num = 1
for clusternum, hashtag_indicies in clusters.items():
    if len(hashtag_indicies) >= int(len(graph) * min_cluster_percent):
        color_map[clusternum] = color_num
        color_num += 1
color_map[-1] = 0




x = np.arange(color_num)
ys = [i + x + (i * x) ** 2 for i in range(color_num)]
colors = cm.rainbow(np.linspace(0, 1, len(ys)))

plt.figure(figsize=(18, 18))  # in inches
lim = 200

top = [x for x, y in counter.most_common(lim)]

legends = {}

for clusternum, hashtag_indicies in clusters.items():
    if len(hashtag_indicies) < int(len(graph) * min_cluster_percent):
        clusternum = -1
    #if clusternum < 10:
        #patch = mpatches.Patch(color=colors[clusternum], label='Cluster ' + str(clusternum))
        #plt.legend(handles=[patch], loc=clusternum + 1)
    for j in hashtag_indicies:
        mark = 'o'
        l = ''
        # print hashtag_clusters[hashtag_ids[i]]

        z = plt.scatter(low_dims[j][0], low_dims[j][1], color=colors[color_map[clusternum]], marker=mark)
        if clusternum not in legends:
            legends[clusternum] = z
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

legend_labels = {}
for x in legends.keys():
    if x == -1:
        legend_labels[legends[x]] = "Outlier Cluster"
    else:
        legend_labels[legends[x]] = 'Cluster ' + str(x)

#legend_labels = ["Outlier Cluster"] + ['Cluster ' + str(x) for x in legends.keys()]

plt.legend(tuple(legend_labels.keys()), tuple(legend_labels.values()), scatterpoints=1, loc='lower left', ncol=3, fontsize=8)
# print cents

plt.savefig(filename + '.png')
