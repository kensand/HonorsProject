from Library import Database
from sklearn.cluster import KMeans
import array
import numpy as np
import gc
from pyclustering.cluster.xmeans import xmeans

cur = Database.get_Cur()
query = "SELECT tweet_id, hashtag_id FROM tweets_hashtags WHERE tweet_id in (SELECT id from tweets where issue='abortion') ORDER BY tweet_id ASC "
cur.execute(query)

tweetshashtags = {}
count = 0
hashtag_indicies = {}
for row in cur:
    tweet_id = row[0]
    hashtag_id = row[1]
    if hashtag_id not in hashtag_indicies and count < 25000:
        hashtag_indicies[hashtag_id] = count
        count += 1
    if hashtag_id in hashtag_indicies:
        if tweet_id in tweetshashtags:
            tweetshashtags[tweet_id].append(hashtag_indicies[hashtag_id])
        else:
            tweetshashtags[tweet_id] = [hashtag_indicies[hashtag_id]]

graph = []
print count
for i in range(count):
    arr = array.array('H')
    arr.append(np.int16(0))
    graph.append(arr*count)
    #print type(graph[i][0])
max = 0
for tweet_id, hashtags in tweetshashtags.items():
    if len(hashtags) > 1:
        for hashtag1 in hashtags:
            for hashtag2 in hashtags:
                if hashtag1 != hashtag2: #actually, might be ok if they are the same - just results in coutn of times used
                    graph[hashtag1][hashtag2] = np.uint16(1)
                    if max < graph[hashtag1][hashtag2]:
                        max = graph[hashtag1][hashtag2]
                    #print type(graph[hashtag1][hashtag2])

#for i in range(len(graph)):
    #for j in range(len(graph[i])):
        #graph[i][j] = max - graph[i][j]
del(tweetshashtags)
gc.collect()


'''
cluster_num = 2
print "starting clustering"
km = KMeans(n_clusters=cluster_num, random_state=0)
#km.fit(graph.values())
print "fitting"
km.fit(graph)
print "getting labels"
l = km.labels_.tolist()
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


hashtag_clusters = {}
search = Database.get_Cur()
for hashtag_id, index in hashtag_indicies.items():
    search.execute("""SELECT hashtag FROM hashtags WHERE id='%s'""", [hashtag_id])
    hashtag = search.fetchone()

    hashtag_clusters[hashtag] = l[index]

#print hashtag_clusters


ancur = Database.get_Cur()
ancur.execute("SELECT id, hashtag, annotation FROM annotated_hashtags ORDER BY annotation DESC ")
annotated_hashtags = ancur.fetchall()
notable_hashtags = [i[1] for i in annotated_hashtags]
notable_hashtags_clusters = {}



clusters = {}
for h, label in hashtag_clusters.items():
    hashtag = h[0]
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
clusterc=[0] * num_clusters
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

f = open('CoocurenceResults', 'w')

f.writelines('\n'.join([str(x) for x in outstrlist]))
f.close()