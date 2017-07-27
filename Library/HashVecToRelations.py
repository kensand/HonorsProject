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



def HashVecToRelations(schema='public'):
    # get the graph
    cluster_num = 2
    kmeans = True

    conn = Database.get_Conn()
    cur = conn.cursor()
    search = conn.cursor()
    search_string = """SELECT hashtag_id, hashtag_embedding FROM """ + schema + """.hashtag_embeddings"""
    #print search_string
    cur.execute(search_string)
    graph = {}
    hashtags = {}
    for i in cur:
        if cur.rownumber >100000:
            break
        #print i[0]
        #print i[1]
        graph[i[0]] = i[1]
        hashtags[i[0]] = ''

    for i in hashtags.keys():
        search.execute("""SELECT hashtag from hashtags WHERE id = %s""", [int(i)])
        s = search.fetchone()[0]
        hashtags[i] = s.decode('UTF-8', 'replace').encode('ascii', 'replace')

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

    append = False
    output = schema + "." + Database.hashtag_relationships['table_name'] #TODO make table name static
    outcur = Database.get_Cur()
    if append == False:
        outcur.execute("""TRUNCATE """ + output)
        outcur.execute("""COMMIT""")
        print "Truncated " + output

    for index, key in indicies.items():
        outcur.execute("""INSERT INTO """ + output + """ (index, hashtag, relationships) VALUES (%s, %s, %s)""", [index, hashtags[indicies[index]], sims[indicies[index]]])
    outcur.execute("""COMMIT""")