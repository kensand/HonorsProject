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

# integer_tweets input options
parser.add_argument('-t', '--tweet_input', action='store', dest='ints', default=Database.int_tweets['table_name'],
                    help='')
parser.add_argument('-tic', '--input_tweet_id_column', action='store', dest='ints_id_column',
                    default=Database.int_tweets['id_column'],
                    help='The name of the input column holding the tweet ids.')
parser.add_argument('-tac', '--input_tweet_array_column', action='store', dest='ints_array_column',
                    default=Database.int_tweets['int_array_column'],
                    help='The name of the input column holding the tweet tokens.')

# word embedding input options
parser.add_argument('-ie', '--input_word_embeddings', action='store', dest='input_word_embeddings',
                    default=Database.word_embeddings['table_name'],
                    help='')
parser.add_argument('-iic', '--input_word_id_column', action='store', dest='in_word_id_column',
                    default=Database.word_embeddings['word_id_column'],
                    help='The name of the input column holding the tweet ids.')
parser.add_argument('-iec', '--input_embeddings_column', action='store', dest='in_word_embedding_column',
                    default=Database.word_embeddings['word_embedding_column'],
                    help='The name of the input column holding the tweet tokens.')



# output options

# 2 columns - tweet id and embedding

parser.add_argument('-o', '--output', action='store', dest='output', default=Database.tweet_embeddings['table_name'],
                    help='')

parser.add_argument('-ohc', '--output_tweet_id_column', action='store', dest='tweet_id_column',
                    default=Database.tweet_embeddings['tweet_id_column'],
                    help='')
parser.add_argument('-oec', '--output_tweet_embedding_column', action='store', dest='tweet_embedding_column',
                    default=Database.tweet_embeddings['tweet_embedding_column'],
                    help='')

# utility options
parser.add_argument('-w', '--where', action='store', dest='where', default=False,
                    help='An optional WHERE filter for the inumpyut SELECT call. This allows you to add filters to the inumpyut data. You should write only the contents of the WHERE clause as it would be written in PSQL')
parser.add_argument('-a', '--append', action='store_const', const=True, dest='append', default=False,
                    help='Using this flag will cause the output to be appended to the table as opposed to truncating the table.')
parser.add_argument('-m', '--commit', action='store_const', const=True, dest='commit', default=False,
                    help='Using this flag will commit every 1000 tweet insertions. This will drastically increase processing time, but will periodically commit, so that the table can be viewed as it is built')

# database options
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

select = """SELECT """ + args.ints_id_column + ', ' + args.ints_array_column + """ FROM """ + args.ints
if args.where != False:
    select += """ WHERE """ + str(args.where)
incur.execute(select)

tweet_embeddings = {}
start = time.localtime()
#for every tweet_id and vector that we have in the tweet vecs,
for row in incur:
    #create the embedding of the tweet
    id = row[0]
    arr = row[1]
    s = [0] * 128 #TODO get the max length needed first
    for word in arr:
        searchterm = """SELECT """ + args.in_word_embedding_column + """ FROM """ + args.input_word_embeddings + """ WHERE """ + args.in_word_id_column + "=" + str(word)
        search.execute(searchterm)
        embedding = search.fetchone()
        if embedding != None:
            embedding = embedding[0]
            s = [x + y for x,y in zip(embedding, s)]
    out_term = """INSERT INTO """ + args.output + """ (""" + args.tweet_id_column + """, """ + args.tweet_embedding_column + """) VALUES (%s, %s)"""
    outcur.execute(out_term, [id, s])
    if incur.rownumber % 1000 == 1:  # int(incur.rowcount / 100) == 0:
        fin = ((time.mktime(time.localtime()) - time.mktime(start)) / incur.rownumber) * incur.rowcount
        fin += time.mktime(start)
        if args.commit == True:
            outcur.execute("""COMMIT""")
        print str(incur.rownumber) + '/' + str(incur.rowcount) + ". Est. completion time: " + time.strftime(
            "%b %d %Y %H:%M:%S", time.localtime(fin))