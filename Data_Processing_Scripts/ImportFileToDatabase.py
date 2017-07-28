
import sys, os
sys.path.append('/home/kenny/PycharmProjects/HonorsProject/')
from Library import Database


schema = '"semeval-2016"'
table = "twitter_trainA_2016"
table_format = "tweet_id BIGINT, sentiment varchar(10), text varchar(500)"
separator = "\t"
filename = r'../2016-output/twitter_trainA_2016.txt'

f = open(filename, 'r')
cur = Database.get_Cur()
cur.execute("DROP TABLE IF EXISTS " + schema + "." + table + "; COMMIT;")
cur.execute("CREATE TABLE " + schema + "." + table + " (" + table_format + ")")
cur.copy_from(f, schema+"."+table, sep=separator)

f.close()
exit(0)

