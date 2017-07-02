from Library import Database
import collections
cur = Database.get_Cur()
print 'executing'
cur.execute("""SELECT hashtag_id from tweets_hashtags WHERE tweet_id in (SELECT tweet_id FROM tweets WHERE issue = 'abortion')""")

print 'executed'
counter = collections.Counter()
for row in counter:
    print str(cur.rownumber) + '/' + str(cur.rowcount)
    counter[row[0]] += 1

for i in counter.most_common(100):
    print i

