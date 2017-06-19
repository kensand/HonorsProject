import argparse
import getpass
import time

from Library import Database
from Library import TweetVecToHashVec

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
parser.add_argument('-ouc', '--output_use_column', action='store', dest='hashtag_use_column',
                    default=Database.hashtag_embeddings['hashtag_use_column'],
                    help='')

# hashtag reference options
parser.add_argument('-it', '--input_hashtags', action='store', dest='input_hashtags',
                    default=Database.tweets_hashtags['table_name'],
                    help='')
parser.add_argument('-iic', '--input_hashtags_tweet_id_column', action='store', dest='in_hashtag_tweets_id_column',
                    default=Database.tweets_hashtags['tweets_id_column'],
                    help='The name of the column in the hashtag table that has the tweet id')
parser.add_argument('-ihc', '--input_hashtags_hashtag_column', action='store', dest='in_hashtag_column',
                    default=Database.tweets_hashtags['hashtag_id'],
                    help='The name of the column in the hashtag table that has the hashtag id')


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

#call the function
TweetVecToHashVec.tweet_vec_to_hash_vec(conn=conn, output=args.output,
                                        hashtag_id_col=args.hashtag_id_column,
                                        hashtag_embedding_col=args.hashtag_embedding_column,
                                        hashtag_use_col=args.hashtag_use_column,
                                        input_hashtags=args.input_hashtags,
                                        in_hashtag_tweets_id_col=args.in_hashtag_tweets_id_column,
                                        in_hashtag_col=args.in_hashtag_column,
                                        input_tweet_embeddings=args.input_tweet_embeddings,
                                        in_tweet_id_col=args.in_tweet_id_column,
                                        in_tweet_embedding_col=args.in_tweet_embedding_column,
                                        append=False, where=False, commit=False)
