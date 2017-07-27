from Library import Database, Dictionary, TextToInts, WordToVec, WordVecToHashVec, HashVecToRelations,  ClusterVisualize
import random

print "setting up"

random.seed()

train_schema = 'train'
test_schema = 'test'
cur = Database.get_Cur()
out = Database.get_Cur()
'''
print "creating schemas"
cur.execute("""CREATE SCHEMA IF NOT EXISTS """ + test_schema + """; COMMIT;""")
cur.execute("""CREATE SCHEMA IF NOT EXISTS """ + train_schema + """; COMMIT;""")


print "counting tweets"

cur.execute("""SELECT count(*) FROM tweets WHERE issue='abortion'""")
size = cur.fetchone()[0]

print "dropping tables"

cur.execute("""DROP TABLE IF EXISTS """ + train_schema + """.tweets_used; COMMIT;""")
cur.execute("""DROP TABLE IF EXISTS """ + test_schema + """.tweets_used; COMMIT;""")

print "creating tables"

cur.execute("""CREATE TABLE IF NOT EXISTS """ + train_schema + """.tweets_used (id bigint not null constraint train_tweets_used_id_pk primary key); COMMIT;""")

cur.execute("""CREATE TABLE IF NOT EXISTS """ + test_schema + """.tweets_used (id bigint not null constraint test_tweets_used_id_pk primary key); COMMIT;""")



print "finding tweets"
cur.execute("""SELECT id FROM tweets WHERE issue='abortion'""")

print "starting splitting"

test = []
test_count = 0
train = []
train_count = 0
test_buff = 0
train_buff = 0
for i in cur:
    if cur.rownumber % 10000 == 0:
        print str(cur.rownumber) + '/' + str(size)
    id = i[0]
    if test_count >= size / 2:
        train.append(id)
        train_count += 1
        train_buff += 1
    elif train_count >= size / 2:
        test.append(id)
        test_count += 1
        test_buff += 1
    else:
        if random.randint(0,1) == 0:
            train.append(id)
            train_count += 1
            train_buff += 1
        else:
            test.append(id)
            test_count += 1
            test_buff += 1
    if test_buff >= 10000:
        test_buff = 0
        q = """INSERT INTO """ + test_schema + """.tweets_used VALUES """ + ",".join(['(' + str(x) + ')' for x in test]) + """; COMMIT;"""
        out.execute(q)
        test = []
    if train_buff >= 10000:
        train_buff = 0
        q = """INSERT INTO """ + train_schema + """.tweets_used VALUES """ + ",".join(['(' + str(x) + ')' for x in train]) + """; COMMIT;"""
        out.execute(q)
        train = []

where = 'id IN (SELECT id from ' + train_schema + '.tweets_used)'

Database.CreateDictionaryTable(train_schema)
Dictionary.create_dictionary(schema=train_schema, where=where)

Database.CreateIntTweetsTable(schema=train_schema)
TextToInts.integerize_tweets(schema=train_schema, where=where)

Database.CreateWordEmbeddingTable(schema=train_schema)
WordToVec.WordToVec(schema=train_schema)

Database.CreateHashtagEmbeddingTable(schema=train_schema)
WordVecToHashVec.WordVecToHashVec(schema=train_schema)

#Database.CreateHashtagRelationshipsTable(schema=train_schema)
#HashVecToRelations.HashVecToRelations(schema=train_schema)

'''
print "Now for the test phase:"

cur.execute("""DROP TABLE IF EXISTS """ + test_schema + """.""" + Database.dictionary['table_name'] + """; COMMIT;""")
cur.execute("""CREATE TABLE """ + test_schema + """.""" + Database.dictionary['table_name'] + """ AS (SELECT * FROM """ + train_schema + """.""" + Database.dictionary['table_name'] + """); COMMIT;""")

where = 'id IN (SELECT id from ' + test_schema + '.tweets_used)'

Database.CreateIntTweetsTable(schema=test_schema)
TextToInts.integerize_tweets(schema=test_schema, where=where)
cur.execute("""DROP TABLE IF EXISTS """ + test_schema + """.""" + Database.word_embeddings['table_name'] + """; COMMIT;""")
cur.execute("""CREATE TABLE """ + test_schema + """.""" + Database.word_embeddings['table_name'] + """ AS (SELECT * FROM """ + train_schema + """.""" + Database.word_embeddings['table_name'] + """); COMMIT;""")

Database.CreateHashtagEmbeddingTable(schema=test_schema)
WordVecToHashVec.WordVecToHashVec(schema=test_schema)

#Database.CreateHashtagRelationshipsTable(schema=test_schema)
#HashVecToRelations.HashVecToRelations(schema=test_schema)


