from Library import Visualize, Database

cur = Database.get_Cur()
search = Database.get_Cur()
cur.execute("""SELECT tweet_id, tweet_embedding FROM tweet_embeddings""")
labeled_embeddings = {}
for i in range(500):
    r = cur.fetchone()
    #search.execute("SELECT tweets.text FROM tweets WHERE id = %s", [r[0]])
    #s = search.fetchone()[0]
    s=str(r[0])
    labeled_embeddings[s] = r[1]

print labeled_embeddings

Visualize.plot_embeddings(labeled_embeddings, "images/tweet_embeddings.png")