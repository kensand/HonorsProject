try:
    from sklearn.manifold import TSNE
    import matplotlib.pyplot as plt
except ImportError:
    print("Please install sklearn, matplotlib, and scipy to visualize embeddings.")


def plot_with_labels(low_dim_embs, labels, filename='word_embeddings.png'):
    assert low_dim_embs.shape[0] >= len(labels), "More labels than embeddings"
    plt.figure(figsize=(18, 18))  # in inches
    for i, label in enumerate(labels):
        x, y = low_dim_embs[i, :]
        plt.scatter(x, y)
        plt.annotate(label,
                     xy=(x, y),
                     xytext=(5, 2),
                     textcoords='offset points',
                     ha='right',
                     va='bottom')

    plt.savefig(filename)

def plot_embeddings(labeled_embeddings, filename):

    final_embeddings = labeled_embeddings.values()
    tsne = TSNE(perplexity=30, n_components=2, init='pca', n_iter=5000)
    plot_only = 500
    low_dim_embs = tsne.fit_transform(final_embeddings)
    labels = [s.decode('UTF-8', 'replace').encode('ascii', 'replace') for s in labeled_embeddings.keys()] #[reverse_dictionary[i].decode('UTF-8', 'replace').encode('ascii', 'replace') for i in xrange(plot_only)]
    plot_with_labels(low_dim_embs, labels, filename=filename)


