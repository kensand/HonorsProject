import argparse
import collections
import getpass
import time

from Library import Database
from Library import Dictionary
# parse arguements
# note, default database settings can be found in the database file.

# TODO update help text

#Program Info
parser = argparse.ArgumentParser(prog='CreateDictionary',
                                 usage='python CreateDictionary -i formatted_tweets -o formatted tweets -u user -p -h localhost -d postgres',
                                 description="\n\n This program TRUNCATES the output table 'formatted_tweets' at the beginning by default.")

#input arguements
parser.add_argument('-i', '--input', action='store', dest='input', default=Database.formatted_tweets['table_name'],
                    help='The name of the input table, which should have columns "id" and "text", where id is a big int representing the tweet id, and text is a string of some sort.')

parser.add_argument('-itc', '--input_tokens_column', action='store', dest='in_tokens_column',
                    default=Database.formatted_tweets['tokens_column'],
                    help='The name of the input column holding the tweet ids.')


#output arguments
parser.add_argument('-o', '--output', action='store', dest='output', default=Database.dictionary['table_name'],
                    help='The name of the table to place the dictionary in')

parser.add_argument('-oic', '--output_id_column', action='store', dest='out_id_column',
                    default=Database.dictionary['word_id_column'],
                    help='The name of the output column to which the word ids will be written.')
parser.add_argument('-owc', '--output_word_column', action='store', dest='out_word_column',
                    default=Database.dictionary['word_column'],
                    help='The name of the output column to which the word will be written.')
parser.add_argument('-ouc', '--output_use_column', action='store', dest='out_use_column',
                    default=Database.dictionary['use_column'],
                    help='The name of the output column to which the number of uses for each word will be written.')

#database info
parser.add_argument('-u', '--user', action='store', dest='user', default=Database.User,
                    help='The user to login to the database as.')
parser.add_argument('-p', '--password', action='store_const', const=True, dest='password', default=False,
                    help='Using this flag will prompt for password for database.')
parser.add_argument('-c', '--host', action='store', dest='host', default=Database.Host,
                    help='The host of the database to be accessed.')
parser.add_argument('-d', '--dbname', action='store', dest='dbname', default=Database.Dbname,
                    help='The database name at the host.')


#utility functions
parser.add_argument('-a', '--append', action='store_const', const=True, dest='append', default=False,
                    help='Using this flag will cause the output to be appended to the table as opposed to truncating the table first.')
parser.add_argument('-w', '--where', action='store', dest='where', default=False,
                    help='An optional WHERE filter for the input SELECT call. This allows you to add filters to the input data. You should write only the contents of the WHERE clause as it would be written in PSQL. It may be prudent to put your clause in double quotes and use single quotes for string objects.')

#database options
parser.add_argument('-s', '--size', action='store', dest='size', default=Database.dictionary['default_size'],
                    help='The number of words to be recorded in the dictionary')

# create the connection
args = parser.parse_args()
size = int(args.size)
if size == 0:
    print "Error with size (-s) in dictionary , given: " + args.size
    exit(0)

# Create a database connection
conn = False
if args.password:
    p = getpass.getpass()
    conn = Database.get_Conn(user=args.user, password=p, host=args.host, dbname=args.dbname)
else:
    conn = Database.get_Conn(user=args.user, password=Database.Password, host=args.host, dbname=args.dbname)

Dictionary.create_dictionary(conn=conn, input=args.input, output=args.output, in_tokens_col=args.in_tokens_column, out_id_col=args.out_id_column, out_word_col=args.out_word_column, out_use_col=args.out_use_column, append=args.append, where=args.where, size=size)
