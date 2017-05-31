import argparse
import collections
import getpass

from scipy import spatial

from Library import Database

parser = argparse.ArgumentParser(prog='FormatTweets',
                                 usage='python FormatTweets -i tweets -o formatted tweets -u user -p -h localhost -d postgres',
                                 description="\n\n This program TRUNCATES the output table 'formatted_tweets' at the beginning by default.")
#parser.add_argument('-i', '--input', action='store', dest='input', default=Database.formatted_tweets['table_name'], help='The name of the input table, which should have columns "id" and "text", where id is a big int representing the tweet id, and text is a string of some sort.')

table = "hashtag_embeddings"
id = "hashtag_id"
embedding = "hashtag_embedding"



#database options
parser.add_argument('-u', '--user', action='store', dest='user', default=Database.User,
                    help='The user to login to the database as.')
parser.add_argument('-p', '--password', action='store_const', const=True, dest='password', default=False,
                    help='Using this flag will prompt for password for database.')
parser.add_argument('-c', '--host', action='store', dest='host', default=Database.Host,
                    help='The host of the database to be accessed.')
parser.add_argument('-d', '--dbname', action='store', dest='dbname', default=Database.Dbname,
                    help='The database name at the host.')

# create the connection
args = parser.parse_args()
conn = False
if args.password:
    p = getpass.getpass()
    conn = Database.get_Conn(user=args.user, password=p, host=args.host, dbname=args.dbname)
else:
    conn = Database.get_Conn(user=args.user, password=Database.Password, host=args.host, dbname=args.dbname)



def lookup(search_id, conn, lookup_table, lookup_id_column, lookup_text_column):
    cursor = conn.cursor()
    cursor.execute("""SELECT """ + lookup_text_column + """ FROM """ + lookup_table + """ WHERE """ + lookup_id_column + """=%s""", [search_id])
    r = cursor.fetchone()
    if r is not None:
        return r[0]
    else:
        return None


def getClosestTo(search_term, conn, lookup_table, lookup_id_column, lookup_text_column, embeddings_table, embeddings_id_column, embeddings_column, size=50):
    search_term_id = lookup(search_term, conn, lookup_table, lookup_text_column, lookup_id_column)
    if search_term is None:
        print "Search term not found : '" + search_term + "'"
        return None
    embedding = lookup(search_term_id, conn, embeddings_table, embeddings_id_column, embeddings_column)
    embcur = conn.cursor()
    embcur.execute("""SELECT """ + embeddings_id_column + ", " + embeddings_column + " FROM " + embeddings_table)
    dists = collections.Counter()
    for row in embcur:
        id, row_embedding = row[0], row[1]
        if id != search_term_id:
            if sum([x * x for x in embedding]) != 0 and sum([x * x for x in row_embedding]) != 0:
                d = 1 - spatial.distance.cosine(embedding, row_embedding)
                dists[id] = d

    return [(lookup(id, conn, lookup_table, lookup_id_column, lookup_text_column), dist) for id, dist in dists.most_common(size)]

print getClosestTo("life", conn, "hashtags", "id", "hashtag", "hashtag_embeddings", "hashtag_id", "hashtag_embedding")
