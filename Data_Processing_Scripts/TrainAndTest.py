from Library import Database, Dictionary, TextToInts, WordToVec, WordVecToHashVec, HashVecToRelations,  ClusterVisualize
from Results_Analysis import VisualizeHashtags
1
#schema = 'abortionweek9'
#WordVecToHashVec.WordVecToHashVec(schema=schema)
#HashVecToRelations.HashVecToRelations(schema=schema)
#ClusterVisualize.ClusterVisualize('results/' + schema + '/', schema)
#exit(0)
runs = {
'training_set_query': '', 'test_set_query' : ''
}

for schema, where in runs.items():
    cur = Database.get_Cur()
    cur.execute("""CREATE SCHEMA IF NOT EXISTS """ + schema + """; COMMIT;""")

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


#using a training set, predict the outcome of a test set, which will also be trained.
