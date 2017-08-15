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
    schema='public'
):
    hash_tab = hash_tab
    int_tweets_tab = schema + '.' + int_tweets_tab
    output = schema + '.' + output


    def count_all_words(conn, schema='public'):
        int_tweets_tab = schema + '.' + Database.int_tweets[ 'table_name']
        int_tweet_tweet_col = Database.int_tweets['id_column']
        int_tweet_arr_col = Database.int_tweets['int_array_column']
        cur = conn.cursor()



        s = """SELECT """ + int_tweet_arr_col + """ FROM """ + int_tweets_tab

        word_count = 0
        cur.execute(s)
        for row in cur:
            word_count += len(row[0])
        return word_count


    def count_words_used_with_hash(hash_id, conn, schema='public'):
        hash_tab = Database.tweets_hashtags['table_name']
        hash_tab_hashtag_col = Database.tweets_hashtags['hashtag_id']
        hash_tab_tweet_col = Database.tweets_hashtags['tweets_id_column']
        int_tweets_tab = schema + '.' + Database.int_tweets[ 'table_name']
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

    def get_tweet_arr(tweet_id, conn, schema):
        int_tweets_tab = schema + '.' + Database.int_tweets['table_name']
        int_tweet_tweet_col = Database.int_tweets['id_column']
        int_tweet_arr_col = Database.int_tweets['int_array_column']

        cur = conn.cursor()
        s= """SELECT """ + int_tweet_arr_col + """ FROM """ + int_tweets_tab + """ WHERE """ + int_tweet_tweet_col + """=""" + str(tweet_id)
        cur.execute(s)
        return cur.fetchone()[0]

    def get_word_emb(word_int, conn, schema):
        word_emb_tab = schema + '.' + Database.word_embeddings['table_name']
        word_emb_col = Database.word_embeddings['word_embedding_column']
        word_id_col = Database.word_embeddings['word_id_column']

        cur = conn.cursor()
        s = """SELECT """ + word_emb_col + """ FROM """ + word_emb_tab + """ WHERE """ + word_id_col + """=""" + str(
            word_int)
        cur.execute(s)
        return cur.fetchone()[0]

    def get_uses(word_int, conn, schema):
        dict_tab = schema + '.' + Database.dictionary['table_name']
        dict_use_col = Database.dictionary['use_column']
        dict_int_col = Database.dictionary['word_id_column']

        cur = conn.cursor()
        s = """SELECT """ + dict_use_col + """ FROM """ + dict_tab + """ WHERE """ + dict_int_col + """=""" + str(word_int)
        cur.execute(s)
        r = cur.fetchone()
        if r != None:
            return int(r[0])
        else:
            return 0

    hashtag_tweet_cur = conn.cursor()

    sel = """SELECT """ + hash_tab_tweet_col + ", " + hash_tab_hashtag_col + """ FROM """ + hash_tab + """ WHERE """ + hash_tab_tweet_col + """ IN (SELECT """ + int_tweets_id_col + """ FROM """ + int_tweets_tab + """)"""
    hashtag_tweet_cur.execute(sel)
    print sel


    hash_counts = {}
    saved_tweets = {}
    word_embs = {}
    hash_embs = {}
    word_uses = {}
    hash_uses = {}
    total_word_count = count_all_words(conn, schema=schema)
    import time
    start = time.localtime()
    #go through all uses of each hashtag
    hash_word_embs = {}
    for row in hashtag_tweet_cur:
        tweet_id=row[0]
        hash_id=row[1]


        if tweet_id not in saved_tweets:
            saved_tweets[tweet_id] = get_tweet_arr(tweet_id, conn, schema=schema)

        if len(saved_tweets[tweet_id]) > 0:

            if hash_id not in hash_counts:
                hash_counts[hash_id] = count_words_used_with_hash(hash_id=hash_id, conn=conn, schema=schema)
            if hash_id not in hash_embs:
                hash_embs[hash_id] = [0]*Database.embedding_length
            if hash_id not in hash_uses:
                hash_uses[hash_id] = 1
            else:
                hash_uses[hash_id] += 1

            if hash_id not in hash_word_embs:
                hash_word_embs[hash_id] = {}

            tweet_emb = [0]*Database.embedding_length
            for word in saved_tweets[tweet_id]:
                if word not in word_embs:
                    word_embs[word] = get_word_emb(word, conn, schema=schema)
                if word not in word_uses:
                    word_uses[word] = get_uses(word, conn, schema=schema)
                if word not in hash_counts[hash_id]:
                    hash_counts[hash_id][word] = 1
                    print "Error, hashcounts was missing the word count for word " + str(word) + " and hashtag " + str(hash_id)

                #calculate the final word embedding by taking the specificity of the word in regards to the hashtag into account
                if word_uses[word] > 0:
                    final_word_emb = Util.scalar_vec_mult(total_word_count * hash_counts[hash_id][word] / word_uses[word], word_embs[word])
                    hash_word_embs[hash_id][word] = final_word_emb

                    #print final_word_emb
                    #this is where we combine the words in the tweets
                    #tweet_emb = Util.sum_vec(tweet_emb, final_word_emb)
            #print tweet_emb
            #this is where each tweet is added to the hashtag embedding
            #hash_embs[hash_id] = Util.sum_vec(hash_embs[hash_id], Util.unitize(tweet_emb))

        #timer
        if hashtag_tweet_cur.rownumber % 1000 == 10:
            fin = ((time.mktime(time.localtime()) - time.mktime(start)) / hashtag_tweet_cur.rownumber) * hashtag_tweet_cur.rowcount
            fin += time.mktime(start)
            print str(hashtag_tweet_cur.rownumber) + '/' + str(hashtag_tweet_cur.rowcount) + ". Est. completion time: " + time.strftime(
                "%b %d %Y %H:%M:%S", time.localtime(fin))

    for hash, word_embs in hash_word_embs.items():
        for word, emb in word_embs.items():
            hash_embs[hash_id] = Util.sum_vec(hash_embs[hash_id], Util.unitize(emb)) #multiply unitized embedding by hash_counts[hash][word]?


    outcur = conn.cursor()
    outcur.execute("""TRUNCATE """ + output)
    outcur.execute("""COMMIT""")
    count = 0
    import time
    start = time.localtime()
    print "hashemb len = " + str(len(hash_embs.items()))
    fails = 0
    for key, value in hash_embs.items():
        out_term = """INSERT INTO """ + output + """ (""" + hashtag_id_col + """, """ + hashtag_embedding_col + """, """ + hashtag_use_col + """) VALUES (%s, %s, %s)"""
        if sum([abs(x) for x in value]) > 0.0:
            outcur.execute(out_term, [key, Util.unitize(value), hash_uses[key]])
        else:
            #outcur.execute(out_term, [key, [0]*Database.embedding_length, hash_uses[key]])
            fails += 1
        if count % 1000 == 1:  # int(incur.rowcount / 100) == 0:
            fin = ((time.mktime(time.localtime()) - time.mktime(start)) / count) * len(hash_embs)
            fin += time.mktime(start)
            if commit == True:
                outcur.execute("""COMMIT""")
            print str(count) + '/' + str(len(hash_embs)) + ". Est. completion time: " + time.strftime(
                "%b %d %Y %H:%M:%S", time.localtime(fin))
    outcur.execute("""COMMIT""")

    print "failures: " + str(fails)
