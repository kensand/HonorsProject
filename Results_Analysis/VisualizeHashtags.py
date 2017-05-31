from Library import Visualize, Database

cur = Database.get_Cur()
search = Database.get_Cur()
cur.execute("""SELECT hashtag_id, hashtag_embedding FROM hashtag_embeddings""")
labeled_embeddings = {}
for i in range(500):
    r = cur.fetchone()
    search.execute("SELECT hashtag FROM hashtags WHERE id = %s", [r[0]])
    s = search.fetchone()[0]
    labeled_embeddings[s] = r[1]

print labeled_embeddings

Visualize.plot_embeddings(labeled_embeddings, "hashtag_embeddings.png")