import argparse
import getpass

from Library import Database, WordVecToHashVec

# The purpose of this file is to convert the tweet_text given fin the formatted tweet table with columns id, tweet_text and convert it into an array of integers representing the sequence of tokens


# parse arguements
# note, default database settings can be found in the database file.
parser = argparse.ArgumentParser(prog='TextToInts',
                                 usage='python TextToInts -i formatted_tweets -k dictionary -o output_table -d dbname -c host -u user -p',
                                 description="\n\n This program TRUNCATES the output table 'formatted_tweets' at the beginning by default.")

# tweets hashtags input options
parser.add_argument('-ith', '--tweet_hashtags', action='store', dest='tweet_hashtags', default=Database.tweets_hashtags['table_name'],
                    help='The tweet hashtag table name')
parser.add_argument('-ithic', '--input_tweet_hashtags_tweet_id_column', action='store', dest='tweet_hashtags_tweet_id_column',
                    default=Database.tweets_hashtags['tweets_id_column'],
                    help='The name of the input column holding the tweet ids in the hashtag tweets table.')
parser.add_argument('-ithhic', '--input_tweet_hashtags_hashtag_id_column', action='store', dest='tweet_hashtags_tweet_hashtag_column',
                    default=Database.tweets_hashtags['hashtag_id'],
                    help='The name of the input column holding the tweet tokens.')

# integer_tweets input options
parser.add_argument('-it', '--integer_tweets', action='store', dest='integer_tweets', default=Database.int_tweets['table_name'],
                    help='')
parser.add_argument('-itic', '--input_tweet_id_column', action='store', dest='integer_tweets_id_column',
                    default=Database.int_tweets['id_column'],
                    help='The name of the input column holding the tweet ids.')
parser.add_argument('-tac', '--input_tweet_array_column', action='store', dest='integer_tweets_array_column',
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

# 3 columns - hashtag id, embedding, and number of hashtag uses

parser.add_argument('-o', '--output', action='store', dest='output', default=Database.hashtag_embeddings['table_name'],
                    help='')

parser.add_argument('-ohc', '--output_hashtag_id_column', action='store', dest='hashtag_id_column',
                    default=Database.hashtag_embeddings['hashtag_id_column'],
                    help='')
parser.add_argument('-oec', '--output_hashtag_embedding_column', action='store', dest='hashtag_embedding_column',
                    default=Database.hashtag_embeddings['hashtag_embedding_column'],
                    help='')
parser.add_argument('-ouc', '--output_hashtag_use_column', action='store', dest='hashtag_use_column',
                    default=Database.hashtag_embeddings['hashtag_use_column'],
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

#call the function



WordVecToHashVec.WordVecToHashVec(
    conn=conn,
    hash_tab = args.tweet_hashtags,
    hash_tab_hashtag_col = args.tweet_hashtags_tweet_hashtag_column,
    hash_tab_tweet_col = args.tweet_hashtags_tweet_id_column,
    int_tweets_tab = args.integer_tweets,
    int_tweets_id_col = args.integer_tweets_id_column,
    int_tweets_array_column = args.integer_tweets_array_column,
    output = args.output,
    hashtag_id_col = args.hashtag_id_column,
    hashtag_embedding_col = args.hashtag_embedding_column,
    hashtag_use_col = args.hashtag_use_column,
    append = False,
    where = False,
    commit = False,)

