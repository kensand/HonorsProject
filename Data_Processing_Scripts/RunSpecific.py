from Library import Database, Dictionary, TextToInts, WordToVec, WordVecToHashVec, HashVecToRelations,  ClusterVisualize, FormatTweets
from Results_Analysis import VisualizeHashtags

'''
schema = 'test'

ClusterVisualize.ClusterVisualize('results/' + schema + '/', schema)
VisualizeHashtags.VisualizeHashtags('results/' + schema + '/', schema)


schema = 'train'

ClusterVisualize.ClusterVisualize('results/' + schema + '/', schema)
VisualizeHashtags.VisualizeHashtags('results/' + schema + '/', schema)

exit(0)
'''
#schema = 'abortionweek9'
#WordVecToHashVec.WordVecToHashVec(schema=schema)
#HashVecToRelations.HashVecToRelations(schema=schema)
#ClusterVisualize.ClusterVisualize('results/' + schema + '/', schema)
#exit(0)



runs = {'abortionweek1': """id IN (SELECT id from tweets WHERE created_at >= '2016-06-24' and created_at < '2016-07-01' and issue='abortion')""", 'abortionweek2': """id IN (SELECT id from tweets WHERE created_at >= '2016-07-01' and created_at < '2016-07-08' and issue='abortion')""", 'abortionweek3': """id IN (SELECT id from tweets WHERE created_at >= '2016-07-08' and created_at < '2016-07-15' and issue='abortion')""", 'abortionweek4': """id IN (SELECT id from tweets WHERE created_at >= '2016-07-15' and created_at < '2016-07-22' and issue='abortion')""", 'abortionweek5': """id IN (SELECT id from tweets WHERE created_at >= '2016-07-22' and created_at < '2016-07-29' and issue='abortion')""", 'abortionweek6': """id IN (SELECT id from tweets WHERE created_at >= '2016-07-29' and created_at < '2016-08-05' and issue='abortion')""", 'abortionweek7': """id IN (SELECT id from tweets WHERE created_at >= '2016-08-05' and created_at < '2016-08-12' and issue='abortion')""", 'abortionweek8': """id IN (SELECT id from tweets WHERE created_at >= '2016-08-12' and created_at < '2016-08-19' and issue='abortion')""", 'abortionweek9': """id IN (SELECT id from tweets WHERE created_at >= '2016-08-19' and created_at < '2016-08-26' and issue='abortion')""", 'abortionweek10': """id IN (SELECT id from tweets WHERE created_at >= '2016-08-26' and created_at < '2016-09-02' and issue='abortion')"""}#, 'abortionall': """id IN (SELECT id from tweets WHERE issue='abortion')"""}
#runs= { 'abortionweek2': """id IN (SELECT id from tweets WHERE created_at >= '2016-07-01' and created_at < '2016-07-08' and issue='abortion')""", 'abortionweek3': """id IN (SELECT id from tweets WHERE created_at >= '2016-07-08' and created_at < '2016-07-15' and issue='abortion')""",}
runs = {'abortionall':'id IN (SELECT id from public.test)'}

FormatTweets.format_tweets(append=False, where=""" issue ='abortion'""", commit=True)

#runs = {'abortionall': """id IN (SELECT id from tweets WHERE issue='abortion')"""}
for schema, where in runs.items():
    cur = Database.get_Cur()
    cur.execute("""CREATE SCHEMA IF NOT EXISTS """ + schema + """; COMMIT;""")
    #cur.execute("""SELECT count(*) FROM """ + schema + """.int_tweets""")
    #print cur.fetchone()

    Database.CreateDictionaryTable(schema)
    Dictionary.create_dictionary(schema=schema, where=where)

    Database.CreateIntTweetsTable(schema=schema)
    TextToInts.integerize_tweets(schema=schema, where=where)

    Database.CreateWordEmbeddingTable(schema=schema)
    WordToVec.WordToVec(schema=schema)

    Database.CreateHashtagEmbeddingTable(schema=schema)
    WordVecToHashVec.WordVecToHashVec(schema=schema)

    Database.CreateHashtagRelationshipsTable(schema=schema)
    HashVecToRelations.HashVecToRelations(schema=schema)

    ClusterVisualize.ClusterVisualize('results/' + schema + '/', schema)
    VisualizeHashtags.VisualizeHashtags('results/' + schema + '/', schema)

