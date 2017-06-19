import os
os.system("""python FormatTweets.py -w "issue='abortion' and created_at>='2016-06-24' and created_at<'2016-07-01'" """)
os.system("""python CreateDictionary.py """)
os.system("""python TextToInts.py""")
os.system("""python WordToVec.py""")
#os.system("""python WordVecToTweetVec.py""")
os.system("""python WordVecToHashVec.py""")