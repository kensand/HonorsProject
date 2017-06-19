import time

from Library import Util, Database


def word_vec_to_tweet_vec(conn=Database.get_Conn(), output=Database.tweet_embeddings['table_name'],
                          tweet_id_col=Database.tweet_embeddings['tweet_id_column'],
                          tweet_embedding_col=Database.tweet_embeddings['tweet_embedding_column'],
                          input_tweets=Database.int_tweets['table_name'],
                          in_tweets_id_col=Database.int_tweets['id_column'],
                          in_tweets_arr_col=Database.int_tweets['int_array_column'],
                          input_word_embeddings=Database.word_embeddings['table_name'],
                          in_word_id_col=Database.word_embeddings['word_id_column'],
                          in_word_embedding_col=Database.word_embeddings['word_embedding_column'],
                          append=False, where=False, commit=False):

    incur = conn.cursor()
    search = conn.cursor()
    outcur = conn.cursor()
    if append == False:
        outcur.execute("""TRUNCATE """ + output)
        outcur.execute("""COMMIT""")
        print "Truncated " + output

    select = """SELECT """ + in_tweets_id_col + ', ' + in_tweets_arr_col + """ FROM """ + input_tweets
    if where != False:
        select += """ WHERE """ + str(where)
    incur.execute(select)

    tweet_embeddings = {}
    start = time.localtime()
    #for every tweet_id and vector that we have in the tweet vecs,
    buff = []
    for row in incur:
        #create the embedding of the tweet
        id = row[0]
        arr = row[1]
        s = [0] * Database.embedding_length #TODO get the max length needed first
        for word in arr:
            searchterm = """SELECT """ + in_word_embedding_col + """ FROM """ + input_word_embeddings + """ WHERE """ + in_word_id_col + "=" + str(word)
            search.execute(searchterm)
            embedding = search.fetchone()
            if embedding != None:
                embedding = embedding[0]
                s = [x + y for x,y in zip(embedding, s)]
        buff.append([id, Util.unitize(s)])
        if len(buff) > Database.batch_size:
            out_term = """INSERT INTO """ + output + """ (""" + tweet_id_col + """, """ + tweet_embedding_col + """) VALUES """ + ','.join(outcur.mogrify('(%s, %s)', x) for x in buff)
            outcur.execute(out_term)
            del buff
            buff = []
        #outcur.execute(out_term, [id, Util.unitize(s)])
        if incur.rownumber % 1000 == 1:  # int(incur.rowcount / 100) == 0:
            fin = ((time.mktime(time.localtime()) - time.mktime(start)) / incur.rownumber) * incur.rowcount
            fin += time.mktime(start)
            if commit == True:
                outcur.execute("""COMMIT""")
            print str(incur.rownumber) + '/' + str(incur.rowcount) + ". Est. completion time: " + time.strftime(
                "%b %d %Y %H:%M:%S", time.localtime(fin))
    if len(buff) > 0:
        out_term = """INSERT INTO """ + output + """ (""" + tweet_id_col + """, """ + tweet_embedding_col + """) VALUES """ + ','.join(outcur.mogrify('(%s, %s)', x) for x in buff)
    outcur.execute("""COMMIT""")