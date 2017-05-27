# 2 columns - hashtag id and embedding

parser.add_argument('-o', '--output', action='store', dest='output', default=Database.hashtag_embeddings['table_name'],
                    help='')

parser.add_argument('-ohc', '--output_hashtag_id_column', action='store', dest='hashtag_id_column',
                    default=Database.hashtag_embeddings['hashtag_id_column'],
                    help='')
parser.add_argument('-oec', '--output_hashtag_embedding_column', action='store', dest='hashtag_embedding_column',
                    default=Database.hashtag_embeddings['hashtags_embedding_column'],
                    help='')

# hashtag reference options
parser.add_argument('-it', '--input_hashtags', action='store', dest='input_hashtags',
                    default=Database.hashtags['table_name'],
                    help='')
parser.add_argument('-iic', '--input_hashtags_tweet_id_column', action='store', dest='in_hashtag_tweets_id_column',
                    default=Database.hashtags['tweets_id_column'],
                    help='The name of the column in the hashtag table that has the tweet id')
parser.add_argument('-iic', '--input_hashtags_hashtag_column', action='store', dest='in_hashtag_column',
                    default=Database.hashtags['hashtag_index'],
                    help='The name of the column in the hashtag table that has the hashtag index')