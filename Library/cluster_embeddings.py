from Library import Database
from pyclustering.cluster.xmeans import xmeans
from sklearn.cluster import KMeans
from Library import Database, Util
from scipy import spatial
from collections import Counter
import numpy
try:
    from sklearn.manifold import TSNE
    import matplotlib.pyplot as plt
    import matplotlib.cm as cm
except ImportError:
    print("Please install sklearn, matplotlib, and scipy to visualize embeddings.")

cluster_num = 2


def get_hashtags_uses(schema):
    counter = Counter()
    cur = Database.get_Cur()
    cur.execute("""SELECT hashtag_id FROM tweets_hashtags WHERE tweet_id in (SELECT id FROM """ + schema + """.int_tweets)""")
    for i in cur:
        counter[i[0]] += 1
    return counter


def cluster_hashtag_embeddings(filename, schema):
    counter = get_hashtags_uses(schema)
    cur = Database.get_Cur()
    cur.execute("""SELECT id, hashtag FROM hashtags""")
    hashtags = {}
    for i in cur:
        hashtags[i[0]] = i[1]
    cur.execute("""SELECT hashtag_id, hashtag_embedding FROM """ + schema + """.hashtag_embeddings""")
    hashtag_embeddings = {}
    for i in cur:
        hashtag_embeddings[i[0]] = i[1]

    hashtag_indicies = {}
    indicies_hashtags = {}
    graph = []
    for index, i in enumerate(hashtag_embeddings.items()):
        id = i[0]
        emb = i[1]
        hashtag_indicies[hashtags[id]] = index
        indicies_hashtags[index] = hashtags[id]
        graph.append(emb)


    clusters_hashtags = {}
    hashtag_clusters = {}

    km = KMeans(n_clusters=cluster_num, random_state=0)
    # km.fit(graph.values())
    km.fit(graph)
    l = km.labels_.tolist()

    for index, hashtag in indicies_hashtags.items():
        cluster = l[index]
        if cluster in clusters_hashtags and hashtag not in clusters_hashtags[cluster]:
            clusters_hashtags[cluster].append(hashtag)
        else:
            clusters_hashtags[cluster] = [hashtag]

        if hashtag not in hashtag_clusters:
            hashtag_clusters[hashtag] = [cluster]
        else:
            hashtag_clusters[hashtag].append(cluster)

    print clusters_hashtags

    numclusters = len(clusters_hashtags.keys())
    ancur = Database.get_Cur()
    ancur.execute("SELECT id, hashtag, annotation FROM annotated_hashtags ORDER BY annotation DESC ")
    annotated_hashtags = ancur.fetchall()
    notable_hashtags = [i[1] for i in annotated_hashtags]
    notable_hashtags_clusters = {}
    labels = indicies_hashtags
    clusterl = [0] * numclusters
    clusterc = [0] * numclusters
    outstrlist = []
    for label, hashtags in clusters_hashtags.items():
        if True:  # len(hashtags) > 2:
            outstrlist.append("Cluster " + str(label) + ", (size = " + str(len(hashtags)) + "): ")
            outstrlist.append([labels[hashtag] for hashtag in hashtags if hashtag in labels])
            for hashtag in hashtags:
                if hashtag in labels:
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

    # outstrlist.append(str(affinityToAdjacency(graph).tolist()))

    f = open(filename, 'w')

    f.writelines('\n'.join([str(x) for x in outstrlist]))
    f.close()
    # exit(0)

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
    from Library import Util

    # reduce dimensionality
    #m = Util.affinityToAdjacency(graph)
    m = graph
    tsne = TSNE(perplexity=30, n_components=2, init='pca', n_iter=50000)
    low_dims = tsne.fit_transform(m)

    color_num = numclusters

    color_num = 2
    for clusternum, hashtag_indicies in clusters_hashtags.items():
        if len(hashtag_indicies) >= len(graph) / 20:
            color_num += 1

    x = numpy.arange(color_num)
    ys = [i + x + (i * x) ** 2 for i in range(color_num)]
    colors = cm.rainbow(numpy.linspace(0, 1, len(ys)))

    plt.figure(figsize=(18, 18))  # in inches
    lim = 200

    top = [x for x, y in counter.most_common(lim)]

    legends = {}

    for clusternum, hashes in clusters_hashtags.items():
        if len(hashtag_indicies) < len(graph) / 20:
            clusternum = -1
            # if clusternum < 10:
            # patch = mpatches.Patch(color=colors[clusternum], label='Cluster ' + str(clusternum))
            # plt.legend(handles=[patch], loc=clusternum + 1)
        for j in hashes:
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

