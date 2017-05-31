import os
os.system("""python FormatTweets.py -w "issue='taxes'" """)
os.system("""python CreateDictionary.py """)
os.system("""python TextToInts.py""")
os.system("""python WordToVec.py""")
os.system("""python WordVecToTweetVec.py""")
os.system("""python TweetVecToHashVec.py""")