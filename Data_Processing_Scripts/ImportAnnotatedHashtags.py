


import sys, os
sys.path.append('/home/kenny/PycharmProjects/HonorsProject/')
from Library import Database

filename = r'annotated_hashtags.csv'
f = open(filename, 'r')
cur = Database.get_Cur()
cur.execute("DROP TABLE IF EXISTS annotated_hashtags; COMMIT;")
cur.execute("CREATE TABLE annotated_hashtags (id integer, hashtag varchar(250), annotation CHAR)")
cur.copy_from(f, 'annotated_hashtags', sep=',')
#cur.execute("COPY annotated_hashtags FROM '" + filename + "' DELIMITERS ',' CSV; COMMIT;")

f.close()

cur.execute("""SELECT id, hashtag, annotation FROM annotated_hashtags""")
cur2 = Database.get_Cur()
table = []
for i in cur:
    if i[2] == ' ':
        cur2.execute("""DELETE FROM annotated_hashtags WHERE id=%s""", [i[0]])

cur2.execute("""COMMIT;""")

