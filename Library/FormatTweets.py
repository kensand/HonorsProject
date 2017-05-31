import argparse
import getpass
import time
import nltk
import unicodedata

from Library import Database

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


def format_tweets(conn=Database.get_Conn(), input=Database.tweets['table_name'], output=Database.formatted_tweets['table_name'], in_id_col=Database.tweets['tweet_id_column'], in_text_col=Database.tweets['text_column'], out_id_col=Database.formatted_tweets['tweet_id_column'], out_tokens_col=Database.formatted_tweets['tokens_column'], append=False, where=False, commit=False):

    incur = conn.cursor()
    outcur = conn.cursor()
    if append == False:
        outcur.execute("""TRUNCATE """ + output)
        outcur.execute("""COMMIT""")
        print "Truncated " + output

    select = "SELECT " + in_id_col + ", " + in_text_col + " FROM " + input
    if where != False:
        select += ' WHERE ' + where
    print "Executing: "
    print select
    incur.execute(select)

    # Run the loop to format each input, put that input into the formatted tweets table.
    start = time.localtime()
    print 'Started at: ' + time.strftime("%b %d %Y %H:%M:%S", start)
    for row in incur:

        id, text = row[0], row[1]
        tokens = format_text(text)
        insert = 'INSERT INTO ' + output + ' (' + out_id_col + ', ' + out_tokens_col + ') VALUES (%s, %s)'
        outcur.execute(insert, [id, tokens])
        if incur.rownumber % 1000 == 1:  # int(incur.rowcount / 100) == 0:
            fin = ((time.mktime(time.localtime()) - time.mktime(start)) / incur.rownumber) * incur.rowcount
            fin += time.mktime(start)
            if commit == True:
                outcur.execute("""COMMIT""")
            print str(incur.rownumber) + '/' + str(incur.rowcount) + ". Est. completion time: " + time.strftime(
                "%b %d %Y %H:%M:%S", time.localtime(fin))

    print 'Completed, Total time: ' + str(time.mktime(time.localtime()) - time.mktime(start)) + ' seconds, committing'
    outcur.execute("""COMMIT""")
    print 'Done, exiting'
