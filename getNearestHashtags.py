import Database
import collections

from scipy import spatial


cur = Database.get_Cur()
cur.execute("""SELECT tweet_id, tweet_embedding FROM tweet_embeddings""")
l = cur.fetchmany(50)

for id, embedding in l:
    embedding = embedding[:128]
    cur2 = Database.get_Cur()
    c = collections.Counter()
    cur2.execute("""SELECT text FROM tweets WHERE id = %s""", [id])
    out = "---" + str(cur2.fetchone()[0]) + '-->'
    cur.execute("""SELECT tweet_id, tweet_embedding FROM tweet_embeddings WHERE tweet_id != %s""", [id])
    rel = collections.Counter()
    for row in cur:
        id2, embedding2 = row
        embedding2 = embedding2[:128]
        #print embedding
        #print embedding2
        d = 1 - spatial.distance.cosine(embedding, embedding2)
        rel[id2] = d
    print out
    for i,j in rel.most_common(10):
        cur2.execute("""SELECT text FROM tweets WHERE id = %s""", [i])
        #out +=  str(cur2.fetchone()[0]) + ', '
        print '--'
        print str(cur2.fetchone()[0])
        print ''

    #print rel.most_common(10)