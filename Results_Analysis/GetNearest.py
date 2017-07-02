from Library import Database
import collections

from scipy import  spatial



schema='abortionweek7.'
cur = Database.get_Cur()
cur.execute("""SELECT word_id, word_embedding FROM """ + schema + """word_embeddings""")
l = cur.fetchmany(50000)

for id, embedding in l:
    cur2 = Database.get_Cur()
    c = collections.Counter()
    cur2.execute("""SELECT word FROM """ + schema + """dictionary WHERE word_id = %s""", [id])
    out = str(cur2.fetchone()) + '->'
    cur.execute("""SELECT word_id, word_embedding FROM """ + schema + """word_embeddings WHERE word_id != %s""", [id])
    rel = collections.Counter()
    for row in cur:
        id2, embedding2 = row
        d = 1 - spatial.distance.cosine(embedding, embedding2)
        rel[id2] = d
    for i,j in rel.most_common(10):
        cur2.execute("""SELECT word FROM """ + schema + """dictionary WHERE word_id = %s""", [i])
        out +=  str(cur2.fetchone()[0]) + ', '
    print out
    #print rel.most_common(10)

