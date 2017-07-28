from Library import Database

cur = Database.get_Cur()
query = "SELECT tweet_id, hashtag_id FROM tweets_hashtags WHERE tweet_id in (SELECT id from tweets where issue='abortion')"
cur.execute(query)

tweetshashtags = {}
count = 0
hashtag_indicies = {}
for row in cur:
    tweet_id = row[0]
    hashtag_id = row[1]
    if hashtag_id not in hashtag_indicies:
        count += 1
        hashtag_indicies[hashtag_id] = count
    if tweet_id in tweetshashtags:
        tweetshashtags[tweet_id].append(hashtag_indicies[hashtag_id])
    else:
        tweetshashtags[tweet_id] = [hashtag_indicies[hashtag_id]]

graph = []
for i in range(count):
    graph.append([0]*count)

for tweet_id, hashtags in tweetshashtags.items():
    if len(hashtags) > 1:
        for hashtag1 in hashtags:
            for hashtag2 in hashtags:
                if hashtag1 != hashtag2: #actually, might be ok if they are the same - just results in coutn of times used
                    graph[hashtag1][hashtag2] += 1

print graph

