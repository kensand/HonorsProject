import psycopg2

batch_size = 10000
embedding_length=256

#These are the default database settings, and assumes the tweets, tweets_hashtags, and hashtags tables are in the public schema.


# default database information
Dbname = 'postgres'
User = 'kenny'
Host = 'localhost'
Password = 'honorsproject2017'

# default table information
#You probably should not change column names because the
tweets = {'table_name': "tweets", 'tweet_id_column': 'id', 'text_column': 'text'}


formatted_tweets = {'table_name': 'formatted_tweets', 'tweet_id_column': 'id', 'tokens_column': 'tokens'}
dictionary = {'table_name': 'dictionary', 'default_size': str(50000), 'word_id_column': 'word_id',
              'word_column': 'word',
              'use_column': 'use'}
int_tweets = {'table_name': 'int_tweets', 'id_column': 'id', 'int_array_column': 'int_array'}
word_embeddings = {'table_name': 'word_embeddings', 'embedding_size': str(embedding_length), 'word_id_column': 'word_id',
                   'word_embedding_column': 'word_embedding'}
tweet_embeddings = {'table_name': 'tweet_embeddings', 'tweet_id_column': 'tweet_id',
                    'tweet_embedding_column': 'tweet_embedding'}
hashtag_embeddings = {'table_name': 'hashtag_embeddings', 'hashtag_id_column': 'hashtag_id',
                      'hashtag_embedding_column': 'hashtag_embedding', 'hashtag_use_column': 'use'}
tweets_hashtags = {'table_name': 'tweets_hashtags', 'tweets_id_column': 'tweet_id', 'hashtag_id': 'hashtag_id'}

hashtag_relationships={'table_name': 'hashtag_relationships'}


#A group of functions to create the tables needed and in the specified schemas


#TODO change all the table and column names to depend on the above config.

def CreateHashtagEmbeddingTable(schema='public'):
    cur = get_Cur()
    if not table_exists(hashtag_embeddings['table_name'], schema):
        cur.execute("""create table """ + schema + """.""" + hashtag_embeddings['table_name'] + """(	hashtag_id bigint not null constraint hashtag_embeddings_pkey primary key, hashtag_embedding double precision[], use integer); create index hashtag_embeddings_index_index on """ + schema + """.hashtag_embeddings (use); COMMIT;""")

def CreateWordEmbeddingTable(schema='public'):
    cur = get_Cur()
    if not table_exists(word_embeddings['table_name'], schema):
        cur.execute("""create table """ + schema + """.""" + word_embeddings['table_name'] + """ ( word_id integer not null constraint word_embeddings_pkey primary key, word_embedding double precision[]); create unique index word_embeddings_index_uindex on """ + schema + """.word_embeddings (word_id);  COMMIT;""")

def CreateHashtagRelationshipsTable(schema='public'):
    cur = get_Cur()
    if not table_exists(hashtag_relationships['table_name'], schema):
        cur.execute("""create table """ + schema + """.""" + hashtag_relationships['table_name'] + """ ( index serial not null constraint hashtag_relationships_pkey primary key, hashtag varchar(255), relationships double precision[]); create unique index hashtag_relationships_index_uindex on """ + schema + """.hashtag_relationships (index); COMMIT;""")


def CreateDictionaryTable(schema='public'):
    cur = get_Cur()
    if not table_exists(dictionary['table_name'], schema):
        cur.execute("""create table """ + schema + """.""" + dictionary['table_name'] + """ ( word_id integer not null constraint dictionary_pkey primary key,	use integer, word varchar(256)); COMMIT;""")


def CreateIntTweetsTable(schema='public'):
    cur = get_Cur()
    if not table_exists(int_tweets['table_name'], schema):
        cur.execute(
            """create table """ + schema + """.""" + int_tweets['table_name'] + """ (	id bigint, int_array integer[]); create index tweetvecs_tweet_id_index on """ + schema + """.int_tweets (id); COMMIT;""")

def CreateFormattedTweetsTable(schema='public'):
    cur = get_Cur()
    if not table_exists(formatted_tweets['table_name'], schema):
        cur.execute("""create table """ + schema + """.""" + formatted_tweets['table_name'] + """ (id bigint not null constraint formatted_tweets_tweet_id_pk primary key, tokens varchar(128)[]); COMMIT;""")





    # function to return the default psycopg2 connection
def get_Conn(dbname=Dbname, user=User, host=Host, password=Password):
    try:
        conn = psycopg2.connect(
            "dbname='" + dbname + "' user='" + user + "' host='" + host + "' password='" + password + "'")
    except:
        print("Unable to connect to the database")
        exit(1)
    # print("Connected to database")
    conn.autocommit = False
    return conn


# function to return a cursor, whether from the default database, or with a given connection.
def get_Cur(conn=False):
    if conn == False:
        return get_Conn().cursor()
    return conn.cursor()


# function to get the dictionary, with either the default config or with it given
def get_dictionary(table=dictionary['table_name'], word_id_column=dictionary['word_id_column'],
                   word_column=dictionary['word_column'], cursor=get_Cur(), schema='public'):
    d = dict()
    cursor.execute("""SELECT """ + word_id_column + ", " + word_column + " FROM " + schema + '.' +table)
    for row in cursor:
        id, word = row
        if id not in d:
            d[word] = id
    return d


# function to get the reverse dicitonary, like the regular dictionary but backwards
def get_reverse_dictionary(table=dictionary['table_name'], word_id_column=dictionary['word_id_column'],
                           word_column=dictionary['word_column'], cursor=get_Cur(), schema='public'):
    d = dict()
    cursor.execute("""SELECT """ + word_id_column + ", " + word_column + " FROM " + schema + '.' +table)
    for row in cursor:
        id, word = row
        if id not in d:
            d[id] = word
    return d


# check if a table exists
def table_exists(table_name, schema='public'):
    conn = get_Conn()
    cursor = get_Cur(conn)
    #q = """select exists(SELECT * FROM information_schema.tables WHERE table_name=%s AND table_schema=%s)"""
    #q = """SELECT EXISTS (   SELECT 1    FROM   pg_catalog.pg_class c   JOIN   pg_catalog.pg_namespace n ON n.oid = c.relnamespace   WHERE  n.nspname = %s   AND    c.relname = %s   );"""
    q = """SELECT '""" + schema+ '.' + table_name + """'::regclass"""
    try:
        cursor.execute(q)#, [schema, table_name])
    except psycopg2.ProgrammingError:
        conn.rollback()
        return False
    return True
    if cursor.fetchone() is None:
        return False
    return True


# check if table exists and it contains the given columns
def table_and_columns_exist(cursor, table_name, columns=[]):
    if not table_exists(cursor, table_name):
        return False
    for col in columns:
        q = """select exists(SELECT * FROM information_schema.columns WHERE table_name=%s AND column_name=%s)"""
        cursor.execute(q, [table_name, col])
        if cursor.fetchone() is None:
            return False
    return True




# create all the tables needed
def CreateDatabases(conn=get_Conn()):
    cur = get_Cur(conn)
    if not table_and_columns_exist(cur, tweets['table_name'], [tweets['tweet_id_column'], tweets['text_column']]):
        cur.execute("""CREATE TABLE """ + tweets['table_name'] + """ (""" + tweets['tweet_id_column'] + """ BIGINT, """ + tweets['text_column'] + """ varchar(500))""")
        cur.execute(
            """CREATE INDEX idx_""" + tweets['tweet_id_column'] + """ ON """ + tweets['table_name'] + """ (""" + tweets['tweet_id_column'] + """)""")
    # TODO finish database create function
