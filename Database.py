import psycopg2

# database information

Dbname = 'postgres'
User = 'kenny'
Host = 'localhost'
Password = 'honorsproject2017'

tweets={'table_name': "tweets", 'id_column': 'id', 'text_column': 'text'}
formatted_tweets={'table_name': 'formatted_tweets', 'id_column': 'id', 'tokens_column': 'tokens'}
dictionary={'table_name': 'dictionary', 'default_size': str(1000), 'word_id_column': 'word_id', 'word_column': 'word', 'use_column': 'use'}


# function to return a psycopg2 connection

def get_Conn(dbname=Dbname,  user=User, host=Host, password=Password):
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
