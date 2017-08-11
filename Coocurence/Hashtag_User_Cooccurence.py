from Library import Database
from sklearn.cluster import KMeans
import array
import numpy as np
import gc
from pyclustering.cluster.xmeans import xmeans

try:
    from sklearn.manifold import TSNE
    import matplotlib.pyplot as plt
    import matplotlib.cm as cm
except ImportError:
    print("Please install sklearn, matplotlib, and scipy to visualize embeddings.")


min_hashtag_occurence = 4


# get the hashtags used by each user.

cur = Database.get_Cur()
query = """SELECT user_id, id from tweets where issue='abortion' limit 100"""
cur.execute(query)

user_tweets = {}
for i in cur:
    user = i[0]
    tweet = i[1]
    if user in user_tweets:
        user_tweets[user].append(tweet)
    else:
        user_tweets[user] = [tweet]

#get the hashtags present in each tweet

query = """SELECT tweet_id, hashtag_id FROM tweets_hashtags where tweet_id in (SELECT tweet_id FROM tweets WHERE issue = 'abortion' LIMIT 100)"""
cur.execute(query)
hashtag_count = {}
tweets_hashtags = {}
for i in cur:
    tweet = i[0]
    hashtag = i[1]
    if hashtag in hashtag_count:
        hashtag_count[hashtag] += 1
    else:
        hashtag_count[hashtag] = 1

    if tweet in user_tweets:
        tweets_hashtags[tweet].append(hashtag)
    else:
        tweets_hashtags[tweet] = [hashtag]


#calculate the hashtags used by each user

user_hashtags = {}
for user, tweets in user_tweets.items():
    if user not in user_hashtags:
        user_hashtags[user] = []
    for tweet in tweets:
        if tweet in tweets_hashtags:
            for hashtag in tweets_hashtags[tweet]:
                if hashtag not in user_hashtags[user]:
                    user_hashtags[user].append(hashtag)

#filter the users that dont user more than one hashtag
user_hashtags = {k: v for k, v in user_hashtags.items() if len(v) > 1}

#assign indicies to each hashtag in the graph
hashtag_indicies = {}
count = 0

for hashtags in user_hashtags.values():
    for hashtag in hashtags:
        if hashtag not in hashtag_indicies and hashtag_count[hashtag] >= min_hashtag_occurence:
            hashtag_indicies[hashtag] = count
            count += 1

#create empty graph
graph = [[0 for x in range(count)] for x in range(count)]

#print user_hashtags
#print user_hashtags
#print hashtag_indicies

#go through each user and if two hashtags coocur in the users tweets mark it ont he graph
for hs in user_hashtags.values():
    for hashtag1 in hs:
        for hashtag2 in hs:
            if hashtag1 in hashtag_indicies and hashtag2 in hashtag_indicies:
                #print graph
                #print str(hashtag1) + ',' + str(hashtag2) + ': ' + str(hashtag_indicies[hashtag1]) + ',' + str(hashtag_indicies[hashtag2]) + ':: ' + str(graph[hashtag_indicies[hashtag1]]) + ',' + str(graph[hashtag_indicies[hashtag1]][hashtag_indicies[hashtag2]])
                graph[hashtag_indicies[hashtag1]][hashtag_indicies[hashtag2]] = 1 #+= 1

#print graph
#exit(0)
#print 'graph length = ' + str(len(graph))
#print [x[:500] for x in graph[:500]]


print "Clustering graph, len=" + str(len(graph))
#cluster the graph



start = [[0] * len(graph)]

'''
x = xmeans(data=graph, initial_centers=start)
x.process()
c = x.get_clusters()
num_clusters = len(c)
l = {}
for i in range(len(c)):
    for j in range(len(c[i])):
        l[c[i][j]] = i
'''

from mcl import mcl_clustering
import networkx as nx

print graph

print np.matrix(graph).shape

inm = nx.from_numpy_matrix(np.matrix(graph))

m, cluster = mcl_clustering.networkx_mcl(inm)

print cluster
exit(0)
'''
print "Searching hashtag names"

hashtag_clusters = {}
search = Database.get_Cur()
hashtag_ids = {}
for hashtag_id, index in hashtag_indicies.items():
    search.execute("""SELECT hashtag FROM hashtags WHERE id='%s'""", [hashtag_id])
    hashtag = search.fetchone()[0]
    hashtag_ids[hashtag_id] = hashtag
    hashtag_clusters[hashtag] = l[index]
'''


ancur = Database.get_Cur()
ancur.execute("SELECT id, hashtag, annotation FROM annotated_hashtags ORDER BY annotation DESC ")
annotated_hashtags = ancur.fetchall()
notable_hashtags = [i[1] for i in annotated_hashtags]
notable_hashtags_clusters = {}



clusters = {}
for hashtag, label in hashtag_clusters.items():
    #print hashtag
    if hashtag in notable_hashtags:
        notable_hashtags_clusters[hashtag] = label
    if label in clusters:
        clusters[label].append(hashtag)
    else:
        clusters[label] = [hashtag]
#print notable_hashtags
#print notable_hashtags_clusters


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

f = open('UserCoocurenceResults', 'w')

f.writelines('\n'.join([str(x) for x in outstrlist]))
f.close()

print "Graphing"

#reduce dimensionality
m = graph
tsne = TSNE(perplexity=30,  n_components=2, init='pca', n_iter=50000)
low_dims = tsne.fit_transform(m)
color_num = num_clusters
x = np.arange(color_num)
ys = [i+x+(i*x)**2 for i in range(color_num)]
colors = cm.rainbow(np.linspace(0, 1, len(ys)))



plt.figure(figsize=(18, 18))  # in inches
lim = 200

for i,j in hashtag_indicies.items():
    mark = 'o'
    l = ''
    if j < 0:
        mark = 's'
    #print hashtag_clusters[hashtag_ids[i]]
    plt.scatter(low_dims[j][0], low_dims[j][1], color=colors[hashtag_clusters[hashtag_ids[i]]], marker=mark)
    if lim > 0:
        l = hashtag_ids[i].decode('UTF-8', 'replace').encode('ascii', 'replace')
        lim -= 1


    #l = ''
    plt.annotate(l,
                 xy=(low_dims[j][0], low_dims[j][1]),
                 xytext=(5, 2),
                 textcoords='offset points',
                 ha='right',
                 va='bottom')

#print cents

plt.savefig('User_hashtag_clusters.png')