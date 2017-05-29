import psycopg2

# database information

Dbname = 'postgres'
User = 'kenny'
Host = 'localhost'
Password = 'honorsproject2017'

tweets = {'table_name': "tweets", 'tweet_id_column': 'id',  'text_column': 'text'}
formatted_tweets = {'table_name': 'formatted_tweets', 'tweet_id_column': 'id', 'tokens_column': 'tokens'}
dictionary = {'table_name': 'dictionary', 'default_size': str(50000), 'word_id_column': 'word_id', 'word_column': 'word',
              'use_column': 'use'}
int_tweets = {'table_name': 'int_tweets', 'id_column': 'id', 'int_array_column': 'int_array'}
word_embeddings = {'table_name': 'word_embeddings', 'embedding_size': str(128), 'word_id_column': 'word_id', 'word_embedding_column': 'word_embedding'}
tweet_embeddings = {'table_name': 'tweet_embeddings', 'tweet_id_column': 'tweet_id', 'tweet_embedding_column': 'tweet_embedding'}
hashtag_embeddings = {'table_name': 'hashtag_embeddings', 'hashtag_id_column': 'hashtag_id', 'hashtag_embedding_column': 'hashtag_embedding'}
hashtags = {'table_name': 'tweets_hashtags', 'tweets_id_column': 'tweet_id', 'hashtag_index': 'hashtag_id'}

# function to return a psycopg2 connection

def get_Conn(dbname=Dbname, user=User, host=Host, password=Password):
    try:
        conn = psycopg2.connect(
            "dbname='" + dbname + "' user='" + user + "' host='" + host + "' password='" + password + "'")
    except:
        print("Unable to connect to the database")
        exit(1)
    # print("Connected to database")
    return conn


def get_Cur():
    return get_Conn().cursor()


def get_dictionary(table, word_id_column, word_column, cursor):
    d = dict()
    cursor.execute("""SELECT """ + word_id_column + ", " + word_column + " FROM " + table)
    for row in cursor:
        id, word = row
        if id not in d:
            d[word] = id
    return d


def get__reverse_dictionary(table, word_id_column, word_column, cursor):
    d = dict()
    cursor.execute("""SELECT """ + word_id_column + ", " + word_column + " FROM " + table)
    for row in cursor:
        id, word = row
        if id not in d:
            d[id] = word
    return d

    # TODO create get_dictionary function

def table_exists(cursor, table_name):
    q = """select exists(SELECT * FROM information_schema.tables WHERE table_name=%s)"""
    cursor.execute()
    if cursor.fetchone() is None:
        return False
    return True

def table_and_columns_exist(cursor, table_name, columns=[]):
    if not table_exists(cursor, table_name):
        return False
    for col in columns:
        q = """select exists(SELECT * FROM information_schema.columns WHERE table_name=%s AND column_name=%s)"""
        cursor.execute(q, [table_name, col])
        if cursor.fetchone() is None:
            return False
    return True