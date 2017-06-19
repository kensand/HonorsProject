from Library import Visualize, Database

cur = Database.get_Cur()
search = Database.get_Cur()
cur.execute("""SELECT hashtag_id, hashtag_embedding FROM hashtag_embeddings ORDER BY use DESC""")
labeled_embeddings = {}
for i in range(100):
    r = cur.fetchone()
    search.execute("SELECT hashtag FROM hashtags WHERE id = %s", [r[0]])
    s = search.fetchone()[0]
    labeled_embeddings[s] = r[1]

print labeled_embeddings

Visualize.plot_embeddings(labeled_embeddings, "images/hashtag_embeddings.png", label_show=True)