import numpy as np
from sklearn.manifold import TSNE

from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
from scipy.spatial import procrustes
import Database
cur = Database.get_Cur()
test = {}
train = {}

schema = 'test'
query = "SELECT hashtag_id, hashtag_embedding FROM " +schema+ "."+Database.hashtag_embeddings['table_name']

cur.execute(query)
for i in cur:
    test[i[0]] = i[1]

schema = 'train'
query = "SELECT hashtag_id, hashtag_embedding FROM " +schema+ "."+Database.hashtag_embeddings['table_name']

cur.execute(query)
for i in cur:
    train[i[0]] = i[1]

test_emb_matrix = []
train_emb_matrix = []
key_vec = []

for key, emb in test.items():
    if key in train:
        key_vec.append(key)
        test_emb_matrix.append(emb)
        train_emb_matrix.append(train[key])

mtx1, mtx2, disparity = procrustes(np.array(train_emb_matrix), np.array(test_emb_matrix))

print mtx1
print mtx2
print disparity

labels = {}
search = Database.get_Cur()
for key in key_vec:
    search.execute("SELECT hashtag FROM hashtags WHERE id = %s", [str(key)])
    s = search.fetchone()[0]
    labels[key] = s.decode('UTF-8', 'replace').encode('ascii', 'replace')

pca = PCA(n_components=64)


tsne = TSNE(perplexity=30, n_components=2, init='pca', n_iter=5000)
plot_only = 500
train_low_dim_embs = tsne.fit_transform(pca.fit_transform(mtx1))
test_low_dim_embs = tsne.fit_transform(pca.fit_transform(mtx2))


plt.figure(figsize=(18, 18))  # in inches
count = 0
for key in key_vec[100:300]:
    l = labels[key]
    #l = ''
    x, y = train_low_dim_embs[count, :]
    plt.scatter(x, y, color='r')
    plt.annotate(l,
                 xy=(x, y),
                 xytext=(5, 2),
                 textcoords='offset points',
                 ha='right',
                 va='bottom')

    x, y = test_low_dim_embs[count, :]

    plt.scatter(x, y, color='b')
    plt.annotate(l,
                 xy=(x, y),
                 xytext=(5, 2),
                 textcoords='offset points',
                 ha='right',
                 va='bottom')

    count += 1
plt.savefig("all_aligned_embeddings.png")