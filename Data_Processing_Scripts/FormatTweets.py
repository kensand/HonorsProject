import argparse
import getpass
import time
import nltk
import unicodedata

from Library import Database
from Library import FormatTweets

# parse arguments
# note, default database settings can be found in the database file.
parser = argparse.ArgumentParser(prog='FormatTweets',
                                 usage='python FormatTweets -i tweets -o formatted tweets -u user -p -h localhost -d postgres',
                                 description="\n\n This program TRUNCATES the output table 'formatted_tweets' at the beginning by default.")

#input arguments
parser.add_argument('-i', '--input', action='store', dest='input', default=Database.tweets['table_name'],
                    help='The name of the input table, which should have columns "id" and "text", where id is a big int representing the tweet id, and text is a string of some sort.')
parser.add_argument('-iic', '--input_id_column', action='store', dest='in_id_column',
                    default=Database.tweets['tweet_id_column'],
                    help='The name of the input column holding the tweet ids.')
parser.add_argument('-itc', '--input_text_column', action='store', dest='in_text_column',
                    default=Database.tweets['text_column'], help='The name of the input column holding the tweet ids.')

#output arguments
parser.add_argument('-o', '--output', action='store', dest='output', default=Database.formatted_tweets['table_name'],
                    help='The name of the output table, which will have columns "id", and "tokens", where id will be the same as the input id, and tokens will be a tokenized and formatted array of strings.')
parser.add_argument('-oic', '--output_id_column', action='store', dest='out_id_column',
                    default=Database.formatted_tweets['tweet_id_column'],
                    help='The name of the output column to which the tweet ids will be written.')
parser.add_argument('-otc', '--output_token_column', action='store', dest='out_token_column',
                    default=Database.formatted_tweets['tokens_column'],
                    help='The name of the output column to which the tokens will be written.')

#database options
parser.add_argument('-u', '--user', action='store', dest='user', default=Database.User,
                    help='The user to login to the database as.')
parser.add_argument('-p', '--password', action='store_const', const=True, dest='password', default=False,
                    help='Using this flag will prompt for password for database.')
parser.add_argument('-c', '--host', action='store', dest='host', default=Database.Host,
                    help='The host of the database to be accessed.')
parser.add_argument('-d', '--dbname', action='store', dest='dbname', default=Database.Dbname,
                    help='The database name at the host.')

#utility args
parser.add_argument('-w', '--where', action='store', dest='where', default=False,
                    help='An optional WHERE filter for the input SELECT call. This allows you to add filters to the input data. You should write only the contents of the WHERE clause as it would be written in PSQL')
parser.add_argument('-m', '--commit', action='store_const', const=True, dest='commit', default=False,
                    help='Using this flag will commit every 1000 table insertions. This will drastically increase processing time, but will periodically commit, so that the table can be viewed as it is built')
parser.add_argument('-a', '--append', action='store_const', const=False, dest='append', default=True,
                    help='Using this flag will cause the output to be appended to the table as opposed to truncating the table.')



# create the connection
args = parser.parse_args()
conn = False
if args.password:
    p = getpass.getpass()
    conn = Database.get_Conn(user=args.user, password=p, host=args.host, dbname=args.dbname)
else:
    conn = Database.get_Conn(user=args.user, password=Database.Password, host=args.host, dbname=args.dbname)

FormatTweets.format_tweets(conn=conn, input=args.input, output=args.output, in_id_col=args.in_id_column, in_text_col=args.in_text_column, out_id_col=args.out_id_column, out_tokens_col=args.out_token_column, append=args.append, where=args.where, commit=args.commit)