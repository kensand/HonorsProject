import argparse
import Database
import getpass
import nltk
import time
import collections


#parse arguements
#note, default database settings can be found in the database file.

#TODO update help text
parser = argparse.ArgumentParser(prog='FormatTweets', usage='python FormatTweets -i tweets -o formatted tweets -u user -p -h localhost -d postgres', description="\n\n This program TRUNCATES the output table 'formatted_tweets' at the beginning by default.")
parser.add_argument('-i', '--input', action='store', dest='input', default=Database.formatted_tweets['table_name'], help='The name of the input table, which should have columns "id" and "text", where id is a big int representing the tweet id, and text is a string of some sort.')
parser.add_argument('-o', '--output', action='store', dest='output', default=Database.dictionary['table_name'], help='The name of the output table, which will have columns "id", and "tokens", where id will be the same as the input id, and tokens will be a tokenized and formatted array of strings.')
parser.add_argument('-u', '--user', action='store', dest='user', default=Database.User, help='The user to login to the database as.')
parser.add_argument('-p', '--password', action='store_const', const=True, dest='password', default=False, help='Using this flag will prompt for password for database.')
parser.add_argument('-c', '--host', action='store', dest='host', default=Database.Host, help='The host of the database to be accessed.')
parser.add_argument('-d', '--dbname', action='store', dest='dbname', default=Database.Dbname, help='The database name at the host.')
parser.add_argument('-a', '--append', action='store_const', const=True, dest='append', default=False, help='Using this flag will cause the output to be appended to the table as opposed to truncating the table.')
parser.add_argument('-itc', '--input_tokens_column', action='store', dest='in_tokens_column', default=Database.formatted_tweets['tokens_column'], help='The name of the input column holding the tweet ids.')
parser.add_argument('-oic', '--output_id_column', action='store', dest='out_id_column', default=Database.dictionary['word_id_column'], help='The name of the output column to which the tweet ids will be written.')
parser.add_argument('-owc', '--output_word_column', action='store', dest='out_word_column', default=Database.dictionary['word_column'], help='The name of the output column to which the tokens will be written.')
parser.add_argument('-ouc', '--output_use_column', action='store', dest='out_use_column', default=Database.dictionary['use_column'], help='The name of the output column to which the tokens will be written.')
parser.add_argument('-w', '--where', action='store', dest='where', default=False, help='An optional WHERE filter for the input SELECT call. This allows you to add filters to the input data. You should write only the contents of the WHERE clause as it would be written in PSQL')
parser.add_argument('-s', '--size', action='store', dest='size', default=Database.dictionary['default_size'], help='The number of words to be recorded in the dictionary')


#create the connection
args = parser.parse_args()
size= int(args.size)
if size == 0:
    print "Error with size (-s) in dictionary , given: " + args.size
    exit(0)


#Create a database connection
conn = False
if args.password:
    p = getpass.getpass()
    conn = Database.get_Conn(user=args.user, password=p, host=args.host, dbname=args.dbname)
else:
    conn = Database.get_Conn(user=args.user, password=Database.Password, host=args.host, dbname=args.dbname)


#create our cursors and truncate output if needed
incur = conn.cursor()
outcur = conn.cursor()
if args.append == False:
    outcur.execute("""TRUNCATE """ + args.output)
    outcur.execute("""COMMIT""")
    print "Truncated " + args.output

#create and execute the input select statement
select = "SELECT " + args.in_tokens_column + " FROM " + args.input
if args.where != False:
    select += ' WHERE ' + args.where
#print "Executing: "
#print select
incur.execute(select)


#Count the number of occurences of each token
d = collections.Counter()
start = time.localtime()
print 'Started counting the words at: ' + time.strftime("%b %d %Y %H:%M:%S", start)
total = 0
for row in incur:
    tokens = row[0]
    for word in tokens:
        d[word] += 1
        total += 1


#get the most common tokens, size dictates how many
l = d.most_common(size - 1)
#print l

#check how many tokens were not included in the dictionary
unk = total - sum([y for x,y in l])

#add the number of unknown to the head of the dictionary
outlist = [("/*UNKNOWN*/", unk)]
outlist.extend(l)

# store all of the dictionary in the database
count = 0
for row in outlist:
    #print row
    word, use = row
    outcur.execute("""INSERT INTO """ + args.output + """ (""" + args.out_id_column + ", " + args.out_word_column + ", " + args.out_use_column + ") VALUES (%s, %s, %s)", [count, word, use])
    count += 1
outcur.execute("""COMMIT""")

count = 0

print d.most_common(10)
exit(0)

