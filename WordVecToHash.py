import argparse
import getpass
import time
import numpy
import SkipGram
import Database

# The purpose of this file is to convert the tweet_text given fin the formatted tweet table with columns id, tweet_text and convert it into an array of integers representing the sequence of tokens


# parse arguements
# note, default database settings can be found in the database file.
parser = argparse.ArgumentParser(prog='TextToInts',
                                 usage='python TextToInts -i formatted_tweets -k dictionary -o output_table -d dbname -c host -u user -p',
                                 description="\n\n This program TRUNCATES the output table 'formatted_tweets' at the beginning by default.")



parser.add_argument('-i', '--inumpyut', action='store', dest='inumpyut', default=Database.int_tweets['table_name'],
                    help='')
parser.add_argument('-iic', '--inumpyut_id_column', action='store', dest='in_id_column',
                    default=Database.int_tweets['id_column'], help='The name of the inumpyut column holding the tweet ids.')
parser.add_argument('-itc', '--inumpyut_int_array_column', action='store', dest='in_int_array_column',
                    default=Database.int_tweets['int_array_column'], help='The name of the inumpyut column holding the tweet tokens.')



#dictionary options
parser.add_argument('-k', '--dictionary', action='store', dest='dict', default=Database.dictionary['table_name'],
                    help='The name of the inumpyut table, which should have columns "id" and "text", where id is a big int representing the tweet id, and text is a string of some sort.')

parser.add_argument('-kic', '--dictionary_word_id_column', action='store', dest='dict_word_id_column', default=Database.dictionary['word_id_column'],
                    help='')
parser.add_argument('-kwc', '--dictionary_word_column', action='store', dest='dict_word_column', default=Database.dictionary['word_column'],
                    help='')

#output options
parser.add_argument('-o', '--output', action='store', dest='output', default=Database.word_embeddings['table_name'],
                    help='The name of the output table, which will have columns "id", and "tokens", where id will be the same as the inumpyut id, and tokens will be a tokenized and formatted array of strings.')
parser.add_argument('-owc', '--output_word_id_column', action='store', dest='word_id_column',
                    default=Database.word_embeddings['word_id_column'],
                    help='The name of the output column to which the tweet ids will be written.')
parser.add_argument('-oec', '--output_embedding_column', action='store', dest='word_embedding_column',
                    default=Database.word_embeddings['word_embedding_column'],
                    help='The name of the output column to which the integer arrays will be written.')


#utility options
parser.add_argument('-w', '--where', action='store', dest='where', default=False,
                    help='An optional WHERE filter for the inumpyut SELECT call. This allows you to add filters to the inumpyut data. You should write only the contents of the WHERE clause as it would be written in PSQL')
parser.add_argument('-a', '--append', action='store_const', const=True, dest='append', default=False,
                    help='Using this flag will cause the output to be appended to the table as opposed to truncating the table.')



#database options
parser.add_argument('-u', '--user', action='store', dest='user', default=Database.User,
                    help='The user to login to the database as.')
parser.add_argument('-p', '--password', action='store_const', const=True, dest='password', default=False,
                    help='Using this flag will prompt for password for database.')
parser.add_argument('-c', '--host', action='store', dest='host', default=Database.Host,
                    help='The host of the database to be accessed.')
parser.add_argument('-d', '--dbname', action='store', dest='dbname', default=Database.Dbname,
                    help='The database name at the host.')



# create the connection
args = parser.parse_args()
conn = False
if args.password:
    p = getpass.getpass()
    conn = Database.get_Conn(user=args.user, password=p, host=args.host, dbname=args.dbname)
else:
    conn = Database.get_Conn(user=args.user, password=Database.Password, host=args.host, dbname=args.dbname)

incur = conn.cursor()
outcur = conn.cursor()
if args.append == False:
    outcur.execute("""TRUNCATE """ + args.output)
    outcur.execute("""COMMIT""")
    print "Truncated " + args.output

select = "SELECT " + args.in_id_column + ", " + args.in_int_array_column + " FROM " + args.inumpyut
if args.where != False:
    select += ' WHERE ' + args.where
print "Executing: "
print select
incur.execute(select)


##THIS IS WHERE IT GETS FUZZY
def generate_batch(batch_size, skips, skip_window, cur):


    # print("size = ", data_size, ", index = ", data_index)
    batch = numpy.ndarray(shape=(batch_size), dtype=numpy.int32)
    labels = numpy.ndarray(shape=(batch_size, 1), dtype=numpy.int32)
    # if len(d) < 1:
    #    print("ERROR")
    #    exit (0)
    # t = d[numpy.random.randint(len(d))][1]

    t = []
    while len(t) < 2:
        t = cur.fetchone()
        while t == None: #maybe while
            cur.execute(cur.query)
            t = cur.fetchone()
        t = t[1]
        t = filter(lambda a: a != 0, t)
        #print "t = " + str(t)

    def get_skips(tokens):
        if len(tokens) < 2:
            return []
        ret = []
        for i in range(len(tokens)):
            if i == 0:
                ret.append([tokens[i], tokens[i+1]])
                ret.append([tokens[i], tokens[i+1]])
            elif i == len(tokens) - 1:
                ret.append([tokens[i], tokens[i-1]])
                ret.append([tokens[i], tokens[i-1]])
            else:
                ret.append([tokens[i], tokens[i +1]])
                ret.append([tokens[i], tokens[i -1]])
        return ret

    sg = get_skips(t)
    #print str(sg)
    for i in range(batch_size):
        if i >= len(sg):
            batch[i] = 0
            labels[i,0] = 0
        else:
            batch[i] = sg[i][0]
            labels[i,0] = sg[i][1]

    #print str([batch, labels])
    #batch = [x for x, y in sg]
    #labels = [y for x, y in sg]
    del sg
    return batch, labels

    '''
    sg = SkipGram.getAllSkipGram(t, batch_size)
    #print "SG = " + str(sg)
    for i in range(batch_size):
        if i >= len(sg):
            j = numpy.random.randint(len(sg))
        else:
            j = i
        if len(sg[j]) == 2:
            # print("sg = ", sg[i])
            batch[i] = sg[j][0]
            labels[i, 0] = sg[j][1]
    '''
    '''
        else:
            r1 = numpy.random.randint(len(sg[j]))
            r2 = numpy.random.randint(len(sg[j]))
            while r1 == r2:
                r2 = numpy.random.randint(len(sg[j]))
            batch[i] = sg[j][r1]
            labels[i, 0] = sg[j][r2]
        '''




















import tensorflow as tf
import math

#get the dictionary
dictionary = Database.get_dictionary(cursor=conn.cursor(), table=args.dict, word_column=args.dict_word_column, word_id_column=args.dict_word_id_column  )
reverse_dictionary = {x: y for y,x in dictionary.items()}
vocabulary_size = len(dictionary.items())


# Step 4: Build and train a skip-gram model.

batch_size = 32
embedding_size = 32  # Dimension of the embedding vector.
skip_window = 1  # How many words to consider left and right.
num_skips = 2  # How many times to reuse an input to generate a label.

# We pick a random validation set to sample nearest neighbors. Here we limit the
# validation samples to the words that have a low numeric ID, which by
# construction are also the most frequent.
valid_size = 16  # Random set of words to evaluate similarity on.
valid_window = 100  # Only pick dev samples in the head of the distribution.
valid_examples = numpy.random.choice(valid_window, valid_size, replace=False)
num_sampled = 16  # Number of negative examples to sample.

graph = tf.Graph()

with graph.as_default():
    # Input data.
    train_inputs = tf.placeholder(tf.int32, shape=[batch_size])
    train_labels = tf.placeholder(tf.int32, shape=[batch_size, 1])
    valid_dataset = tf.constant(valid_examples, dtype=tf.int32)

    # Ops and variables pinned to the CPU because of missing GPU implementation
    with tf.device('/cpu:0'):
        # Look up embeddings for inputs.
        embeddings = tf.Variable(
            tf.random_uniform([vocabulary_size, embedding_size], -1.0, 1.0))
        embed = tf.nn.embedding_lookup(embeddings, train_inputs)

        # Construct the variables for the NCE loss
        nce_weights = tf.Variable(
            tf.truncated_normal([vocabulary_size, embedding_size],
                                stddev=1.0 / math.sqrt(embedding_size)))
        nce_biases = tf.Variable(tf.zeros([vocabulary_size]))

    # Compute the average NCE loss for the batch.
    # tf.nce_loss automatically draws a new sample of the negative labels each
    # time we evaluate the loss.
    loss = tf.reduce_mean(
        tf.nn.nce_loss(weights=nce_weights,
                       biases=nce_biases,
                       labels=train_labels,
                       inputs=embed,
                       num_sampled=num_sampled,
                       num_classes=vocabulary_size))

    # Construct the SGD optimizer using a learning rate of 1.0.
    optimizer = tf.train.GradientDescentOptimizer(1.0).minimize(loss)

    # Compute the cosine similarity between minibatch examples and all embeddings.
    norm = tf.sqrt(tf.reduce_sum(tf.square(embeddings), 1, keep_dims=True))
    normalized_embeddings = embeddings / norm
    valid_embeddings = tf.nn.embedding_lookup(
        normalized_embeddings, valid_dataset)
    similarity = tf.matmul(
        valid_embeddings, normalized_embeddings, transpose_b=True)

    # Add variable initializer.
    init = tf.global_variables_initializer()

# Step 5: Begin training.
num_steps = 100001


with tf.Session(graph=graph) as session:
    # We must initialize all variables before we use them.
    init.run()
    print("Initialized")

    average_loss = 0
    for step in xrange(num_steps):
        batch_inputs, batch_labels = generate_batch(
            batch_size, num_skips, skip_window, incur)
        feed_dict = {train_inputs: batch_inputs, train_labels: batch_labels}

        # We perform one update step by evaluating the optimizer op (including it
        # in the list of returned values for session.run()
        _, loss_val = session.run([optimizer, loss], feed_dict=feed_dict)
        average_loss += loss_val

        if step % 2000 == 0:
            if step > 0:
                average_loss /= 2000
            # The average loss is an estimate of the loss over the last 2000 batches.
            print("Average loss at step ", step, ": ", average_loss)
            average_loss = 0

        # Note that this is expensive (~20% slowdown if computed every 500 steps)
        if step % 10000 == 0:
            sim = similarity.eval()
            for i in xrange(valid_size):
                valid_word = reverse_dictionary[valid_examples[i]]
                top_k = 8  # number of nearest neighbors
                nearest = (-sim[i, :]).argsort()[1:top_k + 1]
                log_str = "Nearest to %s:" % valid_word
                for k in xrange(top_k):
                    close_word = reverse_dictionary[nearest[k]]
                    log_str = "%s %s," % (log_str, close_word)
                print(log_str)
    final_embeddings = normalized_embeddings.eval()




# Step 6: Visualize the embeddings.


def plot_with_labels(low_dim_embs, labels, filename='tsne.png'):
    assert low_dim_embs.shape[0] >= len(labels), "More labels than embeddings"
    plt.figure(figsize=(18, 18))  # in inches
    for i, label in enumerate(labels):
        x, y = low_dim_embs[i, :]
        plt.scatter(x, y)
        plt.annotate(label,
                     xy=(x, y),
                     xytext=(5, 2),
                     textcoords='offset points',
                     ha='right',
                     va='bottom')

    plt.savefig(filename)


try:
    from sklearn.manifold import TSNE
    import matplotlib.pyplot as plt

    tsne = TSNE(perplexity=30, n_components=2, init='pca', n_iter=5000)
    plot_only = 500
    low_dim_embs = tsne.fit_transform(final_embeddings[:plot_only, :])
    labels = [reverse_dictionary[i] for i in xrange(plot_only)]
    plot_with_labels(low_dim_embs, labels)

except ImportError:
    print("Please install sklearn, matplotlib, and scipy to visualize embeddings.")

print final_embeddings, dictionary, reverse_dictionary



for i in range(len(final_embeddings)):
    outcur.execute("""INSERT INTO """ + args.output + """ (""" + args.word_id_column + ", " + args.word_embedding_column + ") VALUES (%s, %s)", [i, final_embeddings[i].tolist()])



exit(0)





























# Run the loop to format each inumpyut, put that inumpyut into the formatted tweets table.
start = time.localtime()
count = 0
print 'Started at: ' + time.strftime("%b %d %Y %H:%M:%S", start)
row = incur.fetch
for row in incur:

    id, tokens = row[0], row[1]
    arr = []











    insert = 'INSERT INTO ' + args.output + ' (' + args.out_id_column + ', ' + args.out_int_array_column + ') VALUES (%s, %s)'
    outcur.execute(insert, [id, arr])
    count += 1
    if count % 1000 == 1:  # int(incur.rowcount / 100) == 0:
        fin = ((time.mktime(time.localtime()) - time.mktime(start)) / incur.rownumber) * incur.rowcount
        fin += time.mktime(start)
        outcur.execute("""COMMIT""")
        print str(count) + '/' + str(incur.rowcount) + " Est. completion time: " + time.strftime(
            "%b %d %Y %H:%M:%S", time.localtime(fin))

print 'Completed, Total time: ' + str((time.mktime(time.localtime()) - time.mktime(start))) + ' seconds, committing'
outcur.execute("""COMMIT""")
print 'Done, exiting'
