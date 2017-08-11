from Library import Database
from sklearn.cluster import KMeans
import array
import numpy as np
from mcl import mcl_clustering
import networkx
import gc
from pyclustering.cluster.xmeans import xmeans

try:
    from sklearn.manifold import TSNE
    import matplotlib.pyplot as plt
    import matplotlib.cm as cm
except ImportError:
    print("Please install sklearn, matplotlib, and scipy to visualize embeddings.")

filename = 'smalltest'
graph_size = 500
min_user_hashtags = 2
create_new_graph = True


def loadGraph():
    cur = Database.get_Cur()
    output = 'UserCoocurence'
    cur.execute("""SELECT index, count, hashtag, edges FROM """ + output + """ ORDER BY index ASC""")
    labels = {}
    from collections import Counter
    counter = Counter()
    graph = []
    for i in cur:
        index = i[0]
        count = i[1]
        hashtag = i[2]
        edges = i[3]
        graph.append(edges)
        counter[hashtag] = count
        labels[index] = hashtag
    return labels, counter, graph


import time
def saveGraph(graph, labels, counter):
    start = time.localtime()
    count = 0
    commit = True
    print 'Started at: ' + time.strftime("%b %d %Y %H:%M:%S", start)
    size = len(graph)
    output = 'UserCoocurence'
    cur = Database.get_Cur()
    cur.execute("""DROP TABLE IF EXISTS """ + output)
    cur.execute("""CREATE TABLE IF NOT EXISTS """ + output + """ (index int, count int, hashtag varchar(255), edges FLOAT[])""")
    buff = []
    for rownum, row in enumerate(graph):
        buff.append([rownum, counter[labels[rownum]], labels[rownum], row.tolist()])
        if len(buff) > 1000:
            insert = 'INSERT INTO ' + output + ' (index, count, hashtag, edges) VALUES ' + ','.join(cur.mogrify('(%s, %s, %s, %s)', x) for x in buff)
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


    #create a dictionary listing each use of a hashtag by a user

    userHashtags = {}


    from collections import Counter


    hashtag_counter = Counter()
    # for each user
    for user in userToTweets.keys():
        # start a list of each hashtag occurence from that user
        hashtags = []
        # for each tweet by that user
        for tweet in userToTweets[user]:
            #for each hashtag in that tweet
            if tweet in tweetToHashtagIds:
                for hashtag_id in tweetToHashtagIds[tweet]:
                    #add it to the list of hashtags for the user
                    hashtags.append(hashtagIdToHashtag[hashtag_id])

        #check that there are more than the minimum number of hashtags per user -
        # if there is only 1 hashtag, there are no coocurences with other hashtags
        # also count the number of occurences of each hashtag
        if len(hashtags) >= min_user_hashtags:
            for hashtag in hashtags:
                hashtag_counter[hashtag] += 1
            userHashtags[user] = hashtags


    graph_size = len(hashtag_counter.keys())

    # give each hashtag a index
    # and the reverse
    indicies_hashtags = {}
    hashtag_indicies = {}
    for i,j in enumerate(hashtag_counter.most_common(graph_size)):
        hashtag_indicies[j[0]] = i
        indicies_hashtags[i] = j[0]

    #create a graph full of 0s

    graph = np.zeros((graph_size, graph_size))


    #increase the edge values for each coocurence of a hashtag by a user
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
                    if hashtag2 in hashtag_indicies: # and hashtag2 != hashtag1:
                        graph[hashtag_indicies[hashtag1]][hashtag_indicies[hashtag2]] += 1

    #print graph.tolist()

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
                    #not sure how this will work
                    exit(0)


def getClusters(graph):


    print np.matrix(graph).shape

    inm = networkx.from_numpy_matrix(np.matrix(graph))

    m, cluster = mcl_clustering.networkx_mcl(G=inm, expand_factor = 10, inflate_factor = 2, max_loop = 100 , mult_factor = 1 ) # (G=inm, expand_factor = 2, inflate_factor = 2, max_loop = 10 , mult_factor = 1 )
    '''

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


    print cluster
    return cluster



#main
if create_new_graph:
    labels, counter, graph = getGraph(graph_size, min_user_hashtags)
    saveGraph(graph, labels, counter)
else:
    labels, counter, graph = loadGraph()
clusters = getClusters(graph)

#clusters = removeOverlap(clusters)

print 'printing'

numclusters = len(clusters.keys())
ancur = Database.get_Cur()
ancur.execute("SELECT id, hashtag, annotation FROM annotated_hashtags ORDER BY annotation DESC ")
annotated_hashtags = ancur.fetchall()
notable_hashtags = [i[1] for i in annotated_hashtags]
notable_hashtags_clusters = {}

clusterl = [0] * numclusters
clusterc=[0] * numclusters
outstrlist = []
for label, hashtags in clusters.items():
    outstrlist.append("Cluster " + str(label) + ", (size = " + str(len(hashtags)) + "): ")
    outstrlist.append([labels[hashtag] for hashtag in hashtags])
    for hashtag in hashtags:
        notable_hashtags_clusters[labels[hashtag]] = label

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

f = open(filename, 'w')

f.writelines('\n'.join([str(x) for x in outstrlist]))
f.close()


try:
    from sklearn.manifold import TSNE
    import matplotlib.pyplot as plt
    import matplotlib.cm as cm
    import matplotlib.patches as mpatches
except ImportError:
    print("Please install sklearn, matplotlib, and scipy to visualize embeddings.")

print "Graphing"

#reduce dimensionality
m = graph
tsne = TSNE(perplexity=30,  n_components=2, init='pca', n_iter=50000)
low_dims = tsne.fit_transform(m)



color_num = numclusters
x = np.arange(color_num)
ys = [i+x+(i*x)**2 for i in range(color_num)]
colors = cm.rainbow(np.linspace(0, 1, len(ys)))



plt.figure(figsize=(18, 18))  # in inches
lim = 200



top = [x for x,y in counter.most_common(lim)]

for clusternum, hashtag_indicies in clusters.items():
    patch = mpatches.Patch(color=colors[clusternum], label='Cluster ' + str(clusternum))
    plt.legend(handles=[patch], loc=clusternum)
    for j in hashtag_indicies:
        mark = 'o'
        l = ''
        #print hashtag_clusters[hashtag_ids[i]]
        plt.scatter(low_dims[j][0], low_dims[j][1], color=colors[clusternum], marker=mark)
        if lim > 0 and labels[j] in top:
            l = labels[j].decode('UTF-8', 'replace').encode('ascii', 'replace')
            lim -= 1


        #l = ''
        plt.annotate(l,
                     xy=(low_dims[j][0], low_dims[j][1]),
                     xytext=(5, 2),
                     textcoords='offset points',
                     ha='right',
                     va='bottom')

#print cents

plt.savefig(filename + '.png')

