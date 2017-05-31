from Library import Database
import collections
import time


def create_dictionary(conn=Database.get_Conn(), input=Database.formatted_tweets['table_name'], output=Database.dictionary['table_name'], in_tokens_col=Database.formatted_tweets['tokens_column'], out_id_col=Database.dictionary['word_id_column'], out_word_col=Database.dictionary['word_column'], out_use_col=Database.dictionary['use_column'], append=False, where=False, commit=False, size=int(Database.dictionary['default_size'])):
    # create our cursors and truncate output if needed
    incur = conn.cursor()
    outcur = conn.cursor()
    if append == False:
        outcur.execute("""TRUNCATE """ + output)
        outcur.execute("""COMMIT""")
        print "Truncated " + output

    # create and execute the input select statement
    select = "SELECT " + in_tokens_col + " FROM " + input
    if where != False:
        select += ' WHERE ' + where
    # print "Executing: "
    # print select
    incur.execute(select)

    # Count the number of occurences of each token
    d = collections.Counter()
    start = time.localtime()
    print 'Started counting the words at: ' + time.strftime("%b %d %Y %H:%M:%S", start)
    total = 0
    for row in incur:
        tokens = row[0]
        for word in tokens:
            d[word] += 1
            total += 1

    # get the most common tokens, size dictates how many
    l = d.most_common(size - 1)
    # print l

    # check how many tokens were not included in the dictionary
    unk = total - sum([y for x, y in l])

    # add the number of unknown to the head of the dictionary
    outlist = [("/*UNKNOWN*/", unk)]
    outlist.extend(l)
    ret = []
    # store all of the dictionary in the database
    count = 0
    for row in outlist:
        word, use = row
        outcur.execute(
            """INSERT INTO """ + output + """ (""" + out_id_col + ", " + out_word_col + ", " + out_use_col + ") VALUES (%s, %s, %s)",
            [count, word, use])
        ret.append([count, word, use])
        count += 1
        if count % 1000 == 1:
            if commit:
                outcur.execute("""COMMIT""")
            print str(count) + '/' + str(total)
    outcur.execute("""COMMIT""")

    return ret
