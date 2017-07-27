import os
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


notable_hashtags = ['defundpp',
'praytoendabortion',
'prolife',
'ppsellsbabyparts',
'stopabortion',

'abortion',
'pregnant',
'healthcare',
'medical',
'health',

'prochoice',
'antichoice',
'womensrights',
'mybodymychoice',
'fundpp']


ancur = Database.get_Cur()
ancur.execute("SELECT id, hashtag, annotation FROM annotated_hashtags ORDER BY annotation DESC ")
annotated_hashtags = ancur.fetchall()
notable_hashtags = [i[1] for i in annotated_hashtags]


def ClusterVisualize(folder='', schema='public'):
    print "Loading hashtag relationships"
    if not os.path.exists(folder):
        os.makedirs(folder)
    # get the graph
    cluster_num = 2
    kmeans = True
    outstrlist = []
    conn = Database.get_Conn()
    cur = conn.cursor()
    search = conn.cursor()
    search_string = """SELECT index, hashtag, relationships FROM """ + schema + """.""" + Database.hashtag_relationships['table_name'] #TODO move column names to database dict
    #outstrlist.append( search_string
    cur.execute(search_string)
    graph = {}
    hashtags = {}
    for i in cur:
        #outstrlist.append( i[0]
        #outstrlist.append( i[1]
        graph[i[0]] = i[2]
        #hashtags[i[0]] = i[1] #here

    search_string = """SELECT hashtag_id, hashtag_embedding FROM """ + schema + """.""" + \
                    Database.hashtag_embeddings['table_name'] # TODO move column names to database dict
    # outstrlist.append( search_string
    matrix = {}
    cur.execute(search_string)
    for i in cur:
        matrix[i[0]] = i[1]
        search.execute("""SELECT hashtag FROM hashtags WHERE id=%s""", [i[0]]) #here
        hashtags[i[0]] = search.fetchone()[0] #here

    cluster_labels = {}
    if kmeans:

        km = KMeans(n_clusters=cluster_num, random_state=0)
        #km.fit(graph.values())
        km.fit(matrix.values())
        l = km.labels_.tolist()
        for i,j in enumerate(matrix.keys()):#graph.keys()): #here
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






    print "Done clustering"
    notable_hashtags_clusters = {}
    clusters = {}
    for i,j in cluster_labels.items():
        if hashtags[i] in notable_hashtags:
            notable_hashtags_clusters[hashtags[i]] = j
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
            m.append(matrix[ind])#graph[ind]) #here

        dists = [spatial.distance.euclidean(x,cents[count]) for x in m]
        #outstrlist.append( cents[count]*len(m)
        s = numpy.std(dists)
        stddevs.append(s)
        outstrlist.append( "Cluster " + str(count + 1) + ', size = ' + str(len(mem)) + ', stdev = ' + str(s)) #+ ', within = ' + str(len(pr))
        outstrlist.append( ", ".join(mem))
        count+=1

    print 'Calculated cluster standard deviations'

    centavg = 0
    for ind,i in enumerate(cents):
        graph[(ind +1) * -1] = i
        hashtags[(ind + 1) * -1] = "CLUSTER CENTER " + str(ind + 1)
        cluster_labels[(ind + 1) * -1] = ind
        for j in cents:
            centavg += spatial.distance.euclidean(i,j)
    centavg /= len(cents)
    outstrlist.append( "Average distance between centers of clusters: " + str(centavg)+ "\n")
    clusterl = [0,0]
    clusterc=[0,0]
    for i in annotated_hashtags:
        if i[1] in notable_hashtags_clusters:
            if str(i[2]) == 'l':
                clusterl[notable_hashtags_clusters[i[1]]] += 1
            elif str(i[2]) == 'c':
                clusterc[notable_hashtags_clusters[i[1]]] += 1
            outstrlist.append(str(i[1]) + '(' + str(i[2]) + '): ' + str(notable_hashtags_clusters[i[1]]))
        else:
            outstrlist.append(str(i[1]) + '(' + str(i[2]) + '): Not found')

    outstrlist.append("Prolife annotated hashtags: Cluster 0: " + str(clusterl[0]) + " Cluster 1: " + str(clusterl[1]))
    outstrlist.append("Prochoice annotated hashtags: Cluster 0: " + str(clusterc[0]) + " Cluster 1: " + str(clusterc[1]))


    print "Compared clustering for annotated hashtags, proceeding to graph"
    '''
    for i in notable_hashtags:
        if i in notable_hashtags_clusters:
            outstrlist.append(str(i) + ': ' + str(notable_hashtags_clusters[i]))
        else:
            outstrlist.append(str(i) + ': Not found')
    '''

    f = open(folder + '' + schema + 'Result', 'w')

    f.writelines('\n'.join([str(x) for x in outstrlist]))
    return

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
    outstrlist.append( schema)
    outstrlist.append( len(graph))
    #print l
    plt.savefig(folder + schema + '-labled_relationships.png')
    plt.clf()

    m = matrix.values()
    tsne = TSNE(perplexity=30, n_components=2, init='pca', n_iter=50000)
    low_dims = tsne.fit_transform(m)
    color_num = cluster_num
    x = numpy.arange(color_num)
    ys = [i + x + (i * x) ** 2 for i in range(color_num)]
    colors = cm.rainbow(numpy.linspace(0, 1, len(ys)))

    plt.figure(figsize=(18, 18))  # in inches
    lim = 200

    for i, j in enumerate(matrix.keys()):
        mark = 'o'
        l = ''
        if j < 0:
            mark = 's'
        plt.scatter(low_dims[i][0], low_dims[i][1], marker=mark)


    plt.savefig(folder + schema + '-hashtag_embeddings.png')
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
    plt.savefig(folder + schema + '-unlabeled_relationships.png')

