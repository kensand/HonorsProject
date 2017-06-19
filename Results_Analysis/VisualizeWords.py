from Library import Visualize, Database

cur = Database.get_Cur()
search = Database.get_Cur()
cur.execute("""SELECT word_id, word_embedding FROM word_embeddings""")
labeled_embeddings = {}
for i in range(100):
    r = cur.fetchone()
    search.execute("SELECT word FROM dictionary WHERE word_id = %s", [r[0]])
    s = search.fetchone()[0]
    #s=str(r[0])
    labeled_embeddings[s] = r[1]

print labeled_embeddings

Visualize.plot_embeddings(labeled_embeddings, "images/word_embeddings.png", label_show=True)