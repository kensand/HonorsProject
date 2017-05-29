import argparse
import getpass
import time
import numpy
import SkipGram
import Database

# The purpose of this file is to convert the tweet_text given fin the formatted tweet table with columns id, tweet_text and convert it into an array of integers representing the sequence of tokens




# parse arguements
# note, default database settings can be found in the database file.
parser = argparse.ArgumentParser(prog='TextToInts',
                                 usage='python TextToInts -i formatted_tweets -k dictionary -o output_table -d dbname -c host -u user -p',
                                 description="\n\n This program TRUNCATES the output table 'formatted_tweets' at the beginning by default.")



# 2 columns - hashtag id and embedding

parser.add_argument('-o', '--output', action='store', dest='output', default=Database.hashtag_embeddings['table_name'],
                    help='')

parser.add_argument('-ohc', '--output_hashtag_id_column', action='store', dest='hashtag_id_column',
                    default=Database.hashtag_embeddings['hashtag_id_column'],
                    help='')
parser.add_argument('-oec', '--output_hashtag_embedding_column', action='store', dest='hashtag_embedding_column',
                    default=Database.hashtag_embeddings['hashtag_embedding_column'],
                    help='')

# hashtag reference options
parser.add_argument('-it', '--input_hashtags', action='store', dest='input_hashtags',
                    default=Database.hashtags['table_name'],
                    help='')
parser.add_argument('-iic', '--input_hashtags_tweet_id_column', action='store', dest='in_hashtag_tweets_id_column',
                    default=Database.hashtags['tweets_id_column'],
                    help='The name of the column in the hashtag table that has the tweet id')
parser.add_argument('-ihc', '--input_hashtags_hashtag_column', action='store', dest='in_hashtag_column',
                    default=Database.hashtags['hashtag_index'],
                    help='The name of the column in the hashtag table that has the hashtag index')


# tweet embedding input options
parser.add_argument('-ie', '--input_tweet_embeddings', action='store', dest='input_tweet_embeddings',
                    default=Database.tweet_embeddings['table_name'],
                    help='')
parser.add_argument('-itc', '--input_tweet_id_column', action='store', dest='in_tweet_id_column',
                    default=Database.tweet_embeddings['tweet_id_column'],
                    help='The name of the input column holding the tweet ids.')
parser.add_argument('-iec', '--input_embeddings_column', action='store', dest='in_tweet_embedding_column',
                    default=Database.tweet_embeddings['tweet_embedding_column'],
                    help='The name of the input column holding the tweet tokens.')



#utility options
parser.add_argument('-w', '--where', action='store', dest='where', default=False,
                    help='An optional WHERE filter for the inumpyut SELECT call. This allows you to add filters to the inumpyut data. You should write only the contents of the WHERE clause as it would be written in PSQL')
parser.add_argument('-a', '--append', action='store_const', const=True, dest='append', default=False,
                    help='Using this flag will cause the output to be appended to the table as opposed to truncating the table.')



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



incur = conn.cursor()
search = conn.cursor()
outcur = conn.cursor()
if args.append == False:
    outcur.execute("""TRUNCATE """ + args.output)
    outcur.execute("""COMMIT""")
    print "Truncated " + args.output

select = """SELECT """ + args.in_tweet_id_column + ', ' + args.in_tweet_embedding_column + """ FROM """ + args.input_tweet_embeddings
if args.where != False:
    select += """ WHERE """ + str(args.where)
incur.execute(select)
hash_embeddings={}
for row in incur:
    id = row[0]
    embedding = row[1]
    s = """SELECT """ + args.in_hashtag_column + """ FROM """ + args.input_hashtags + """ WHERE """ + args.in_hashtag_tweets_id_column + """=""" + str(id)
    search.execute(s)
    for result in search:
        if result[0] in hash_embeddings:
            hash_embeddings[result[0]] = [x+y for x,y in zip(hash_embeddings[result[0]], embedding)]
        else:
            hash_embeddings[result[0]] = embedding

count = 0
start = time.localtime()
for key, value in hash_embeddings.items():
    out_term = """INSERT INTO """ + args.output + """ (""" + args.hashtag_id_column + """, """ + args.hashtag_embedding_column + """) VALUES (%s, %s)"""
    outcur.execute(out_term, [key, value])
    if count % 1000 == 1:  # int(incur.rowcount / 100) == 0:
        fin = ((time.mktime(time.localtime()) - time.mktime(start)) / count) * len(hash_embeddings)
        fin += time.mktime(start)
        if args.commit == True:
            outcur.execute("""COMMIT""")
        print str(count) + '/' + str(len(hash_embeddings)) + ". Est. completion time: " + time.strftime(
            "%b %d %Y %H:%M:%S", time.localtime(fin))




print str(hash_embeddings)