
import tensorflow as tf
from sklearn.cluster import KMeans
from pyclustering.cluster.xmeans import xmeans
import Database
# get the graph


clustersize =128

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

start = [[0] * 128]
x = xmeans(data=h_graph, initial_centers=start)
x.process()
c = x.get_clusters()
#c.fit(graph)
for i in range(len(c)):
    print "Cluster " + str(i)
    members = []
    #print c[i]
    for index in c[i]:
        if index in node_ids:
            search.execute("""SELECT hashtag from hashtags WHERE id = %s""", [int(node_ids[index])])
            members.append(search.fetchone()[0])
    print ", ".join(members)




#print "In cluster 1 - " + str(len())
#print c
