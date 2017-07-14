from Library import Visualize, Database, Util

cur = Database.get_Cur()
search = Database.get_Cur()
cur.execute("""SELECT word_id, word_embedding FROM abortionall.word_embeddings WHERE word_id in (SELECT word_id FROM dictionary ORDER BY use DESC LIMIT 100)""")
labeled_embeddings = {}
for r in cur:
    search.execute("SELECT word FROM dictionary WHERE word_id = %s", [r[0]])
    s = search.fetchone()[0]
    #s=str(r[0])
    if s[0] != '#':
        labeled_embeddings[s] = r[1]
    if len(labeled_embeddings) == 10000:
        break

print labeled_embeddings

from sklearn.manifold import TSNE
import matplotlib.pyplot as plt

final_embeddings = labeled_embeddings.values()
tsne = TSNE(perplexity=30, n_components=2, init='pca', n_iter=5000)

low_dim_embs = tsne.fit_transform(final_embeddings)
#low_dim_embs = numpy.array([Util.normalize(x) for x in tsne.fit_transform(final_embeddings)])
labels = [s.decode('UTF-8', 'replace').encode('ascii', 'replace') for s in labeled_embeddings.keys()] #[reverse_dictionary[i].decode('UTF-8', 'replace').encode('ascii', 'replace') for i in xrange(plot_only)]
count = 200
plt.figure(figsize=(18, 18))  # in inches
for i, label in enumerate(labels):
    if count> 0:
        l = label
        count -= 1
    else:
        l = ''

    x, y = low_dim_embs[i, :]
    plt.scatter(x, y)
    plt.annotate(l,
                 xy=(x, y),
                 xytext=(5, 2),
                 textcoords='offset points',
                 ha='right',
                 va='bottom')

    plt.savefig('wordembeddings.png')



