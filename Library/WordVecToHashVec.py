from Library import Database, Util



def WordVecToHashVec(
    conn = Database.get_Conn(),
    hash_tab = Database.tweets_hashtags['table_name'],
    hash_tab_hashtag_col = Database.tweets_hashtags['hashtag_id'],
    hash_tab_tweet_col = Database.tweets_hashtags['tweets_id_column'],
    int_tweets_tab = Database.int_tweets['table_name'],
    int_tweets_id_col = Database.int_tweets['id_column'],
    int_tweets_array_column=Database.int_tweets['int_array_column'],
    output = Database.hashtag_embeddings['table_name'],
    hashtag_id_col = Database.hashtag_embeddings['hashtag_id_column'],
    hashtag_embedding_col = Database.hashtag_embeddings['hashtag_embedding_column'],
    hashtag_use_col = Database.hashtag_embeddings['hashtag_use_column'],
    append = False,
    where = False,
    commit = False,
):

    def count_words_used_with_hash(hash_id, conn):
        hash_tab = Database.tweets_hashtags['table_name']
        hash_tab_hashtag_col = Database.tweets_hashtags['hashtag_id']
        hash_tab_tweet_col = Database.tweets_hashtags['tweets_id_column']
        int_tweets_tab = Database.int_tweets[ 'table_name']
        int_tweet_tweet_col = Database.int_tweets['id_column']
        int_tweet_arr_col = Database.int_tweets['int_array_column']
        cur = conn.cursor()



        s = """SELECT """ + int_tweet_arr_col + """ FROM """ + int_tweets_tab + """ WHERE """ + int_tweet_tweet_col + """ IN (SELECT """ + hash_tab_tweet_col + """ FROM """ + hash_tab + """ WHERE """ + hash_tab_hashtag_col + """=""" + str(hash_id) + """)"""

        word_count = {}
        cur.execute(s)
        for row in cur:
            for word in row[0]:
                if word in word_count:
                    word_count[word] += 1
                else:
                    word_count[word] = 1
        return word_count

    def get_tweet_arr(tweet_id, conn):
        int_tweets_tab = Database.int_tweets['table_name']
        int_tweet_tweet_col = Database.int_tweets['id_column']
        int_tweet_arr_col = Database.int_tweets['int_array_column']

        cur = conn.cursor()
        s= """SELECT """ + int_tweet_arr_col + """ FROM """ + int_tweets_tab + """ WHERE """ + int_tweet_tweet_col + """=""" + str(tweet_id)
        cur.execute(s)
        return cur.fetchone()[0]

    def get_word_emb(word_int, conn):
        word_emb_tab = Database.word_embeddings['table_name']
        word_emb_col = Database.word_embeddings['word_embedding_column']
        word_id_col = Database.word_embeddings['word_id_column']

        cur = conn.cursor()
        s = """SELECT """ + word_emb_col + """ FROM """ + word_emb_tab + """ WHERE """ + word_id_col + """=""" + str(
            word_int)
        cur.execute(s)
        return cur.fetchone()[0]

    def get_uses(word_int, conn):
        dict_tab = Database.dictionary['table_name']
        dict_use_col = Database.dictionary['use_column']
        dict_int_col = Database.dictionary['word_id_column']

        cur = conn.cursor()
        s = """SELECT """ + dict_use_col + """ FROM """ + dict_tab + """ WHERE """ + dict_int_col + """=""" + str(word_int)
        cur.execute(s)
        return cur.fetchone()[0]

    hashtag_tweet_cur = conn.cursor()

    hashtag_tweet_cur.execute("""SELECT """ + hash_tab_tweet_col + ", " + hash_tab_hashtag_col + """ FROM """ + hash_tab + """ WHERE """ + hash_tab_tweet_col + """ IN (SELECT """ + int_tweets_id_col + """ FROM """ + int_tweets_tab + """)""")

    hash_counts = {}
    saved_tweets = {}
    word_embs = {}
    hash_embs = {}
    word_uses = {}
    hash_uses = {}
    import time
    start = time.localtime()
    #go through all uses of each hashtag
    for row in hashtag_tweet_cur:
        tweet_id=row[0]
        hash_id=row[1]
        if hash_id not in hash_counts:
            hash_counts[hash_id] = count_words_used_with_hash(hash_id=hash_id, conn=conn)
        if hash_id not in hash_embs:
            hash_embs[hash_id] = [0]*Database.embedding_length
        if hash_id not in hash_uses:
            hash_uses[hash_id] = 1
        else:
            hash_uses[hash_id] += 1
        if tweet_id not in saved_tweets:
            saved_tweets[tweet_id] = get_tweet_arr(tweet_id, conn)
        tweet_emb = [0]*Database.embedding_length
        for word in saved_tweets[tweet_id]:
            if word not in word_embs:
                word_embs[word] = get_word_emb(word, conn)
            if word not in word_uses:
                word_uses[word] = get_uses(word, conn)
            if word not in hash_counts[hash_id]:
                hash_counts[hash_id][word] = 1
            #this is where we combine the words in the tweets
            tweet_emb = Util.sum_vec(tweet_emb, Util.scalar_vec_mult(hash_counts[hash_id][word] / word_uses[word], word_embs[word]))

        #this is where each tweet is added to the hashtag embedding
        hash_embs[hash_id] = Util.unitize(Util.sum_vec(hash_embs[hash_id], tweet_emb))
        if hashtag_tweet_cur.rownumber % 1000 == 10:
            fin = ((time.mktime(time.localtime()) - time.mktime(start)) / hashtag_tweet_cur.rownumber) * hashtag_tweet_cur.rowcount
            fin += time.mktime(start)
            print str(hashtag_tweet_cur.rownumber) + '/' + str(hashtag_tweet_cur.rowcount) + ". Est. completion time: " + time.strftime(
                "%b %d %Y %H:%M:%S", time.localtime(fin))

    outcur = conn.cursor()
    outcur.execute("""TRUNCATE """ + output)
    outcur.execute("""COMMIT""")
    count = 0
    import time
    start = time.localtime()
    print hash_embs.items()
    for key, value in hash_embs.items():
        out_term = """INSERT INTO """ + output + """ (""" + hashtag_id_col + """, """ + hashtag_embedding_col + """, """ + hashtag_use_col + """) VALUES (%s, %s, %s)"""
        if sum(value) != 0.:
            outcur.execute(out_term, [key, Util.unitize(value), hash_uses[key]])
        if count % 1000 == 1:  # int(incur.rowcount / 100) == 0:
            fin = ((time.mktime(time.localtime()) - time.mktime(start)) / count) * len(hash_embs)
            fin += time.mktime(start)
            if commit == True:
                outcur.execute("""COMMIT""")
            print str(count) + '/' + str(len(hash_embs)) + ". Est. completion time: " + time.strftime(
                "%b %d %Y %H:%M:%S", time.localtime(fin))
    outcur.execute("""COMMIT""")
