from Library import Database
import collections

from scipy import spatial
import collections

from scipy import spatial

from Library import Database
s='prolife'
cur = Database.get_Cur()
cur.execute("""SELECT id FROM hashtags WHERE hashtag = %s""", [s])
i = cur.fetchone()[0]
cur.execute("""SELECT hashtag_id, hashtag_embedding FROM hashtag_embeddings WHERE hashtag_id = %s""", [i])
l = [cur.fetchone()]
for id, embedding in l:
    embedding = embedding[:128]
    cur2 = Database.get_Cur()
    c = collections.Counter()
    cur2.execute("""SELECT hashtag FROM hashtags WHERE id = %s""", [id])
    out = "---" + str(cur2.fetchone()[0]) + '-->'
    cur.execute("""SELECT hashtag_id, hashtag_embedding FROM hashtag_embeddings WHERE hashtag_id != %s""", [id])
    rel = collections.Counter()
    for row in cur:
        id2, embedding2 = row
        embedding2 = embedding2[:128]
        #print embedding
        #print embedding2
        d = 1 - spatial.distance.cosine(embedding, embedding2)
        rel[id2] = d
    print out
    for i,j in rel.most_common()[-100:]:
        cur2.execute("""SELECT hashtag FROM hashtags WHERE id = %s""", [i])
        #out +=  str(cur2.fetchone()[0]) + ', '
        print str(cur2.fetchone()[0]) + ': ' + str(j)

    #print rel.most_common(10)
