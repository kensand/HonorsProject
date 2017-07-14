from Library import Visualize, Database
import os

def VisualizeHashtags(folder='', schema='public'):
    cur = Database.get_Cur()
    search = Database.get_Cur()
    cur.execute("""SELECT hashtag_id, hashtag_embedding FROM hashtag_embeddings ORDER BY use DESC""")
    labeled_embeddings = {}
    for r in cur:

        search.execute("SELECT hashtag FROM hashtags WHERE id = %s", [r[0]])
        s = search.fetchone()[0]
        labeled_embeddings[s] = r[1]

    print labeled_embeddings
    if not os.path.exists(folder):
        os.makedirs(folder)

    Visualize.plot_embeddings(labeled_embeddings, folder + schema + '-hashtag_embeddings.png', label_show=True)