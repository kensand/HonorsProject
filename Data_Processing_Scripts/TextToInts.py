import argparse
import getpass

from Library import Database
from Library import TextToInts

# The purpose of this file is to convert the tweet_text given fin the formatted tweet table with columns id, tweet_text and convert it into an array of integers representing the sequence of tokens


# parse arguements
# note, default database settings can be found in the database file.
parser = argparse.ArgumentParser(prog='TextToInts',
                                 usage='python TextToInts -i formatted_tweets -k dictionary -o output_table -d dbname -c host -u user -p',
                                 description="\n\n This program TRUNCATES the output table 'formatted_tweets' at the beginning by default.")

# word embedding input optionsR
parser.add_argument('-i', '--input', action='store', dest='input', default=Database.formatted_tweets['table_name'],
                    help='')
parser.add_argument('-iic', '--input_id_column', action='store', dest='in_id_column',
                    default=Database.formatted_tweets['tweet_id_column'],
                    help='The name of the input column holding the tweet ids.')
parser.add_argument('-itc', '--input_tokens_column', action='store', dest='in_tokens_column',
                    default=Database.formatted_tweets['tokens_column'],
                    help='The name of the input column holding the tweet tokens.')

# dictionary options
parser.add_argument('-k', '--dictionary', action='store', dest='dict', default=Database.dictionary['table_name'],
                    help='The name of the input table, which should have columns "id" and "text", where id is a big int representing the tweet id, and text is a string of some sort.')

parser.add_argument('-kic', '--dictionary_word_id_column', action='store', dest='dict_word_id_column',
                    default=Database.dictionary['word_id_column'],
                    help='')
parser.add_argument('-kwc', '--dictionary_word_column', action='store', dest='dict_word_column',
                    default=Database.dictionary['word_column'],
                    help='')

# output options
parser.add_argument('-o', '--output', action='store', dest='output', default=Database.int_tweets['table_name'],
                    help='The name of the output table, which will have columns "id", and "tokens", where id will be the same as the input id, and tokens will be a tokenized and formatted array of strings.')
parser.add_argument('-oic', '--output_id_column', action='store', dest='out_id_column',
                    default=Database.int_tweets['id_column'],
                    help='The name of the output column to which the tweet ids will be written.')
parser.add_argument('-otc', '--output_arr_column', action='store', dest='out_int_array_column',
                    default=Database.int_tweets['int_array_column'],
                    help='The name of the output column to which the integer arrays will be written.')

# utility options
parser.add_argument('-w', '--where', action='store', dest='where', default=False,
                    help='An optional WHERE filter for the input SELECT call. This allows you to add filters to the input data. You should write only the contents of the WHERE clause as it would be written in PSQL')
parser.add_argument('-a', '--append', action='store_const', const=True, dest='append', default=False,
                    help='Using this flag will cause the output to be appended to the table as opposed to truncating the table.')

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

# get the dictionary
dictionary = Database.get_dictionary(cursor=conn.cursor(), table=args.dict, word_column=args.dict_word_column,
                                     word_id_column=args.dict_word_id_column)

TextToInts.integerize_tweets(dictionary=dictionary, conn=conn, input=args.input, output=args.output,
                             in_id_col=args.in_id_column, in_tokens_col=args.in_tokens_column,
                             out_id_col=args.out_id_column, out_int_arr_col=args.out_int_array_column,
                             append=args.append, where=args.where, commit=args.commit)
