import argparse
import getpass
import time
import nltk
import unicodedata

import Database

stops = ["a", "about", "above", "above", "across", "after", "afterwards", "again", "against", "all", "almost", "alone",
         "along", "already", "also", "although", "always", "am", "among", "amongst", "amoungst", "amount", "an", "and",
         "another", "any", "anyhow", "anyone", "anything", "anyway", "anywhere", "are", "around", "as", "at", "back",
         "be", "became", "because", "become", "becomes", "becoming", "been", "before", "beforehand", "behind", "being",
         "below", "beside", "besides", "between", "beyond", "bill", "both", "bottom", "but", "by", "call", "can",
         "cannot",
         "cant", "co", "con", "could", "couldnt", "cry", "de", "describe", "detail", "do", "done", "down", "due",
         "during",
         "each", "eg", "eight", "either", "eleven", "else", "elsewhere", "empty", "enough", "etc", "even", "ever",
         "every", "everyone", "everything", "everywhere", "except", "few", "fifteen", "fify", "fill", "find", "fire",
         "first", "five", "for", "former", "formerly", "forty", "found", "four", "from", "front", "full", "further",
         "get", "give", "go", "had", "has", "hasnt", "have", "he", "hence", "her", "here", "hereafter", "hereby",
         "herein", "hereupon", "hers", "herself", "him", "himself", "his", "how", "however", "hundred", "ie", "if",
         "least", "less", "ltd", "made", "many", "may", "me", "meanwhile", "might", "mill", "mine", "more", "moreover",
         "most", "mostly", "move", "much", "must", "my", "myself", "name", "namely", "neither", "never", "nevertheless",
         "next", "nine", "no", "nobody", "none", "noone", "nor", "not", "nothing", "now", "nowhere", "of", "off",
         "often", "on", "once", "one", "only", "onto", "or", "other", "others", "otherwise", "our", "ours", "ourselves",
         "out", "over", "own", "part", "per", "perhaps", "please", "put", "rather", "re", "same", "see", "seem",
         "seemed", "seeming", "seems", "serious", "several", "she", "should", "show", "side", "since", "sincere", "six",
         "sixty", "so", "some", "somehow", "someone", "something", "sometime", "sometimes", "somewhere", "still",
         "such", "system", "take", "ten", "than", "that", "the", "their", "them", "themselves", "then", "thence",
         "there", "thereafter", "thereby", "therefore", "therein", "thereupon", "these", "they", "thickv", "thin",
         "third", "this", "those", "though", "three", "through", "throughout", "thru", "thus", "to", "together", "too",
         "top", "toward", "towards", "twelve", "twenty", "two", "un", "under", "until", "up", "upon", "us", "very",
         "via", "was", "we", "well", "were", "what", "whatever", "when", "whence", "whenever", "where", "whereafter",
         "whereas", "whereby", "wherein", "whereupon", "wherever", "whether", "which", "while", "whither", "who",
         "whoever", "whole", "whom", "whose", "why", "will", "with", "within", "without", "would", "yet", "you", "your",
         "yours", "yourself", "yourselves", "the",
         #Custom stop words
         "rt", "in", "is", "in", "it", "its", "i'm",
         ]

replace_words = {'=': ' ', '-': '', '_': ' ', '.': '', '"': '', ';': ' ', ':': '', '+': ' ', '/': '', "'s": '', '!': '', '?': '', ',': ' ' }

def replacements(x):
    for char, rep in replace_words.items():
        x = x.replace(char, rep)
    return x

def format_text(text):
    tokens = [unicodedata.normalize('NFKD', x).encode('ascii', 'ignore').lower() for x in
              nltk.TweetTokenizer(strip_handles=True, preserve_case=True ).tokenize(text=text)]

    #for i in range(len(tokens)):
    #    for j in range(len(tokens[i])):

    #        if tokens[i][j] in


    #print 'before = ' + str(tokens)
    tokens = map(replacements, tokens)
    #print 'after  = ' + str(tokens)
    #filter(lambda x : x is not None, tokens)
    #print tokens

    tokens = ' '.join(tokens).split()



    tokens = filter((lambda x: (x not in stops and len(x) > 1 and len(x) <= 128 and x[:3] != "htt"
                                and x[0] != '@' and x[0] != '#' and x[:2] != "RT" and x[:4] != "&amp" and
                                not x.isdigit()
                                ))

                    , tokens)
    return tokens






# parse arguments
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
parser.add_argument('-m', '--commit', action='store_const', const=True, dest='commit', default=False,
                    help='Using this flag will commit every 1000 tweet insertions. This will drastically increase processing time, but will periodically commit, so that the table can be viewed as it is built')
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
        if args.commit == True:
            outcur.execute("""COMMIT""")
        print str(incur.rownumber) + '/' + str(incur.rowcount) + ". Est. completion time: " + time.strftime(
            "%b %d %Y %H:%M:%S", time.localtime(fin))

print 'Completed, Total time: ' + str(time.mktime(time.localtime()) - time.mktime(start)) + ' seconds, committing'
outcur.execute("""COMMIT""")
print 'Done, exiting'
