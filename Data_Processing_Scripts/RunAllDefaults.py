import os
#os.system("""python FormatTweets.py  """)
os.system("""python CreateDictionary.py -w "id IN (SELECT id from tweets where issue='abortion' AND created_at >= '2016-07-29'  AND created_at < '2016-08-05')" """)
os.system("""python TextToInts.py -w "id IN (SELECT id from tweets where issue='abortion' AND created_at >= '2016-07-29'  AND created_at < '2016-08-05')" """)
os.system("""python WordToVec.py""")
#os.system("""python WordVecToTweetVec.py""")
os.system("""python WordVecToHashVec.py""")
os.system("""python ../Results_Analysis/GraphAndCluster.py""")