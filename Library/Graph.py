from pyclustering.cluster.xmeans import xmeans
from sklearn.cluster import KMeans
import Database
from scipy import spatial
import Util
# get the graph
clustersize = 128

h_graph = []
node_ids = {}

conn  = Database.get_Conn()
cur = conn.cursor()
search = conn.cursor()
cur.execute("""SELECT hashtag_id, hashtag_embedding FROM hashtag_embeddings""")
count = 0
for row in cur:
    h_graph.append(row[1])
    node_ids[count] = row[0]
    count += 1

import time
graph = []
start = time.localtime()
for i in range(len(h_graph)):
    tmp = []
    for j in range(len(h_graph)):
        d = 1 - spatial.distance.cosine(h_graph[i], h_graph[j])
        if i == j:
            d = 1
        tmp.append(d)
    #print str(i) + '/' + str(len(h_graph))
    graph.append(tmp)
    del tmp
    if i % 100 == 10:  # int(incur.rowcount / 100) == 0:
        fin = ((time.mktime(time.localtime()) - time.mktime(start)) / i) * len(h_graph)
        fin += time.mktime(start)

        print str(i) + '/' + str(len(h_graph)) + ". Est. completion time: " + time.strftime(
            "%b %d %Y %H:%M:%S", time.localtime(fin))
start = [[0] * 128]




#for i in graph:
    #print len(i)









#x = xmeans(data=graph, initial_centers=start)
#x.process()
#c = x.get_clusters()
#c.fit(graph)
for i in range(len(c)):

    members = []
    #print c[i]
    for index in c[i]:
        if index in node_ids:
            search.execute("""SELECT hashtag from hashtags WHERE id = %s""", [int(node_ids[index])])
            members.append(search.fetchone()[0])
    print "Cluster " + str(i) + ', size = ' + str(len(members))
    print ", ".join(members)




#print "In cluster 1 - " + str(len())
#print c
