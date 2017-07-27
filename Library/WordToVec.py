import tensorflow as tf
import math
import time

import numpy

from Library import Database, Util

# create the connection
def WordToVec(schema='public'):

    input = Database.int_tweets['table_name']
    in_id_column = Database.int_tweets['id_column']
    in_int_array_column = Database.int_tweets['int_array_column']
    in_dict=Database.dictionary['table_name']
    dict_word_id_column=Database.dictionary['word_id_column']
    dict_word_column=Database.dictionary['word_column']
    output=Database.word_embeddings['table_name']
    word_id_column=Database.word_embeddings['word_id_column']
    word_embedding_column=Database.word_embeddings['word_embedding_column']
    size=Database.word_embeddings['embedding_size']
    where=False
    append=False
    commit=False
    
    



    conn = Database.get_Conn()
    size = Database.word_embeddings['embedding_size']
    append = False
    batch_size = embedding_size = int(size)
    output = Database.word_embeddings['table_name']

    inp = schema + "." + input
    output = schema + "." + output


    incur = conn.cursor()
    outcur = conn.cursor()
    if append == False:
        outcur.execute("""TRUNCATE """ + output)
        outcur.execute("""COMMIT""")
        print "Truncated " + output



    select = "SELECT " + in_id_column + ", " + in_int_array_column + " FROM " + inp
    if where != False:
        select += ' WHERE ' + where
    print "Executing: "
    print select
    incur.execute(select)
    total = incur.rowcount


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













    #get the dictionary
    dictionary = Database.get_dictionary(cursor=conn.cursor(), table=in_dict, word_column=dict_word_column, word_id_column=dict_word_id_column, schema=schema)
    dict_size = len(dictionary)
    reverse_dictionary = {x: y for y,x in dictionary.items()}
    vocabulary_size = 50000#len(dictionary.items())


    # Step 4: Build and train a skip-gram model.

    #batch_size = 32
    #embedding_size = 32  # Dimension of the embedding vector.
    skip_window = 1  # How many words to consider left and right.
    num_skips = 2  # How many times to reuse an input to generate a label.

    # We pick a random validation set to sample nearest neighbors. Here we limit the
    # validation samples to the words that have a low numeric ID, which by
    # construction are also the most frequent.
    valid_size = 16  # Random set of words to evaluate similarity on.
    valid_window = 100  # Only pick dev samples in the head of the distribution.
    valid_examples = numpy.random.choice(valid_window, valid_size, replace=False)
    num_sampled = valid_size  # Number of negative examples to sample.

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
                tf.random_uniform([int(vocabulary_size), int(embedding_size)], -1.0, 1.0))
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


        # Add variable initializer.
        init = tf.global_variables_initializer()

    # Step 5: Begin training.


    num_steps = total
    start_loss = -1

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
                print "Average loss at step '" + str(step) + "/" + str(num_steps) + "': " + str(average_loss)
                if start_loss == -1:
                    start_loss = average_loss
                average_loss = 0
            '''
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
            '''
        final_embeddings = normalized_embeddings.eval()




    # Step 6: Visualize the embeddings.


    # Run the loop to format each input, put that input into the formatted tweets table.
    start = time.localtime()
    count = 0
    print 'Started at: ' + time.strftime("%b %d %Y %H:%M:%S", start)

    buff = []
    print final_embeddings
    for tokens in final_embeddings:

        id = count

        buff.append([id, tokens])
        if len(buff) > Database.batch_size:
            #print buff
            insert = 'INSERT INTO ' + output + ' (' + word_id_column + ', ' + word_embedding_column + ') VALUES ' + ','.join(outcur.mogrify('(%s, %s)', [x[0], Util.unitize(x[1].tolist())]) for x in buff)

            outcur.execute(insert)
            del buff
            buff = []
        count += 1
        if count % 1000 == 1:  # int(incur.rowcount / 100) == 0:
            fin = ((time.mktime(time.localtime()) - time.mktime(start)) / incur.rownumber) * incur.rowcount
            fin += time.mktime(start)
            outcur.execute("""COMMIT""")
            print str(count) + '/' + str(dict_size) + " Est. completion time: " + time.strftime(
                "%b %d %Y %H:%M:%S", time.localtime(fin))
    if len(buff) > 0:
        insert = 'INSERT INTO ' + output + ' (' + word_id_column + ', ' + word_embedding_column + ') VALUES ' + ','.join(
            outcur.mogrify('(%s, %s)', [x[0], x[1].tolist()]) for x in buff)
        outcur.execute(insert)
    print 'Completed, Total time: ' + str((time.mktime(time.localtime()) - time.mktime(start))) + ' seconds, committing'

    outcur.execute("""COMMIT""")
    print 'Done, exiting'
