import argparse
import getpass
import time

from Library import Database

def integerize_tweets(dictionary=Database.get_dictionary(), conn=Database.get_Conn(), input=Database.formatted_tweets['table_name'], output=Database.int_tweets['table_name'], in_id_col=Database.formatted_tweets['tweet_id_column'], in_tokens_col=Database.formatted_tweets['tokens_column'], out_id_col=Database.int_tweets['id_column'], out_int_arr_col=Database.int_tweets['int_array_column'], append=False, where=False, commit=False, schema='public'):
    incur = conn.cursor()
    outcur = conn.cursor()
    output = schema + '.' + output
    if append == False:
        outcur.execute("""TRUNCATE """ + output)
        outcur.execute("""COMMIT""")
        print "Truncated " + output

    select = "SELECT " + in_id_col + ", " + in_tokens_col + " FROM " + input
    if where != False:
        select += ' WHERE ' + where
    print "Executing: "
    print select
    incur.execute(select)

    # Run the loop to format each input, put that input into the formatted tweets table.
    start = time.localtime()
    count = 0
    buff = []
    print 'Started at: ' + time.strftime("%b %d %Y %H:%M:%S", start)
    for row in incur:

        id, tokens = row[0], row[1]
        arr = []
        for token in tokens:
            if token in dictionary:
                arr.append(dictionary[token])
            else:
                #print token
                arr.append(dictionary['/*UNKNOWN*/'])
        buff.append([id, arr])
        if len(buff) > Database.batch_size:
            insert = 'INSERT INTO ' + output + ' (' + out_id_col + ', ' + out_int_arr_col + ') VALUES ' + ','.join(outcur.mogrify('(%s, %s)', x) for x in buff)
            outcur.execute(insert)
            del buff
            buff = []
        count += 1
        if count % 10000 == 1:  # int(incur.rowcount / 100) == 0:
            fin = ((time.mktime(time.localtime()) - time.mktime(start)) / incur.rownumber) * incur.rowcount
            fin += time.mktime(start)
            print str(count) + '/' + str(incur.rowcount) + " Est. completion time: " + time.strftime(
                "%b %d %Y %H:%M:%S", time.localtime(fin))
            if commit:
                outcur.execute("""COMMIT""")

    print 'Completed, Total time: ' + str((time.mktime(time.localtime()) - time.mktime(start))) + ' seconds, committing'
    if len(buff) > 0:
        insert = 'INSERT INTO ' + output + ' (' + out_id_col + ', ' + out_int_arr_col + ') VALUES ' + ','.join(
        outcur.mogrify('(%s, %s)', x) for x in buff)
        outcur.execute(insert)
    outcur.execute("""COMMIT""")
    print 'Done, exiting'
