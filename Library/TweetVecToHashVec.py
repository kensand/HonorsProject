import argparse
import getpass
import time

from Library import Util, Database

# function to replace
def tweet_vec_to_hash_vec(conn=Database.get_Conn(), output=Database.hashtag_embeddings['table_name'],
                          hashtag_id_col=Database.hashtag_embeddings['hashtag_id_column'],
                          hashtag_embedding_col=Database.hashtag_embeddings['hashtag_embedding_column'],
                          input_hashtags=Database.hashtags['table_name'],
                          in_hashtag_tweets_id_col=Database.hashtags['tweets_id_column'],
                          in_hashtag_col=Database.hashtags['hashtag_index'],
                          input_tweet_embeddings=Database.tweet_embeddings['table_name'],
                          in_tweet_id_col=Database.tweet_embeddings['tweet_id_column'],
                          in_tweet_embedding_col=Database.tweet_embeddings['tweet_embedding_column'],
                          append=False, where=False, commit=False):
    incur = conn.cursor()
    search = conn.cursor()
    outcur = conn.cursor()
    if append == False:
        outcur.execute("""TRUNCATE """ + output)
        outcur.execute("""COMMIT""")
        print "Truncated " + output

    select = """SELECT """ + in_tweet_id_col + ', ' + in_tweet_embedding_col + """ FROM """ + input_tweet_embeddings
    if where != False:
        select += """ WHERE """ + str(where)
    incur.execute(select)
    hash_embeddings = {}
    for row in incur:
        id = row[0]
        embedding = row[1]
        s = """SELECT """ + in_hashtag_col + """ FROM """ + input_hashtags + """ WHERE """ + in_hashtag_tweets_id_col + """=""" + str(
            id)
        search.execute(s)
        for result in search:
            if result[0] in hash_embeddings:
                hash_embeddings[result[0]] = [x + y for x, y in zip(hash_embeddings[result[0]], embedding)]
            else:
                hash_embeddings[result[0]] = embedding

    count = 0
    start = time.localtime()
    for key, value in hash_embeddings.items():
        out_term = """INSERT INTO """ + output + """ (""" + hashtag_id_col + """, """ + hashtag_embedding_col + """) VALUES (%s, %s)"""
        outcur.execute(out_term, [key, Util.unitize(value)])
        if count % 1000 == 1:  # int(incur.rowcount / 100) == 0:
            fin = ((time.mktime(time.localtime()) - time.mktime(start)) / count) * len(hash_embeddings)
            fin += time.mktime(start)
            if commit == True:
                outcur.execute("""COMMIT""")
            print str(count) + '/' + str(len(hash_embeddings)) + ". Est. completion time: " + time.strftime(
                "%b %d %Y %H:%M:%S", time.localtime(fin))

    #print str(hash_embeddings)
