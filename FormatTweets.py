import argparse
import getpass
import time

import Database


def format_text(text):
    # tokens = nltk.TweetTokenizer().tokenize(text=text)
    tokens = text.split()
    return tokens


# parse arguements
# note, default database settings can be found in the database file.
parser = argparse.ArgumentParser(prog='FormatTweets',
                                 usage='python FormatTweets -i tweets -o formatted tweets -u user -p -h localhost -d postgres',
                                 description="\n\n This program TRUNCATES the output table 'formatted_tweets' at the beginning by default.")
parser.add_argument('-i', '--input', action='store', dest='input', default=Database.tweets['table_name'],
                    help='The name of the input table, which should have columns "id" and "text", where id is a big int representing the tweet id, and text is a string of some sort.')
parser.add_argument('-o', '--output', action='store', dest='output', default=Database.formatted_tweets['table_name'],
                    help='The name of the output table, which will have columns "id", and "tokens", where id will be the same as the input id, and tokens will be a tokenized and formatted array of strings.')
parser.add_argument('-u', '--user', action='store', dest='user', default=Database.User,
                    help='The user to login to the database as.')
parser.add_argument('-p', '--password', action='store_const', const=True, dest='password', default=False,
                    help='Using this flag will prompt for password for database.')
parser.add_argument('-c', '--host', action='store', dest='host', default=Database.Host,
                    help='The host of the database to be accessed.')
parser.add_argument('-d', '--dbname', action='store', dest='dbname', default=Database.Dbname,
                    help='The database name at the host.')
parser.add_argument('-a', '--append', action='store_const', const=True, dest='append', default=False,
                    help='Using this flag will cause the output to be appended to the table as opposed to truncating the table.')
parser.add_argument('-iic', '--input_id_column', action='store', dest='in_id_column',
                    default=Database.tweets['tweet_id_column'],
                    help='The name of the input column holding the tweet ids.')
parser.add_argument('-itc', '--input_text_column', action='store', dest='in_text_column',
                    default=Database.tweets['text_column'], help='The name of the input column holding the tweet ids.')
parser.add_argument('-oic', '--output_id_column', action='store', dest='out_id_column',
                    default=Database.formatted_tweets['tweet_id_column'],
                    help='The name of the output column to which the tweet ids will be written.')
parser.add_argument('-otc', '--output_token_column', action='store', dest='out_token_column',
                    default=Database.formatted_tweets['tokens_column'],
                    help='The name of the output column to which the tokens will be written.')
parser.add_argument('-w', '--where', action='store', dest='where', default=False,
                    help='An optional WHERE filter for the input SELECT call. This allows you to add filters to the input data. You should write only the contents of the WHERE clause as it would be written in PSQL')

# create the connection
args = parser.parse_args()
conn = False
if args.password:
    p = getpass.getpass()
    conn = Database.get_Conn(user=args.user, password=p, host=args.host, dbname=args.dbname)
else:
    conn = Database.get_Conn(user=args.user, password=Database.Password, host=args.host, dbname=args.dbname)

incur = conn.cursor()
outcur = conn.cursor()
if args.append == False:
    outcur.execute("""TRUNCATE """ + args.output)
    outcur.execute("""COMMIT""")
    print "Truncated " + args.output

select = "SELECT " + args.in_id_column + ", " + args.in_text_column + " FROM " + args.input
if args.where != False:
    select += ' WHERE ' + args.where
print "Executing: "
print select
incur.execute(select)

# Run the loop to format each input, put that input into the formatted tweets table.
start = time.localtime()
print 'Started at: ' + time.strftime("%b %d %Y %H:%M:%S", start)
for row in incur:

    id, text = row[0], row[1]
    tokens = format_text(text)
    insert = 'INSERT INTO ' + args.output + ' (' + args.out_id_column + ', ' + args.out_token_column + ') VALUES (%s, %s)'
    outcur.execute(insert, [id, tokens])
    if incur.rownumber % 1000 == 1:  # int(incur.rowcount / 100) == 0:
        fin = ((time.mktime(time.localtime()) - time.mktime(start)) / incur.rownumber) * incur.rowcount
        fin += time.mktime(start)
        outcur.execute("""COMMIT""")
        print str(int(incur.rownumber / incur.rowcount)) + "% complete. Est. completion time: " + time.strftime(
            "%b %d %Y %H:%M:%S", time.localtime(fin))

print 'Completed, Total time: ' + str(time.localtime() - start) + ' seconds, committing'
outcur.execute("""COMMIT""")
print 'Done, exiting'
