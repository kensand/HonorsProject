from Library import Database

cur = Database.get_Cur()

'''

cur.execute("""CREATE TABLE train AS (SELECT * FROM (SELECT *,row_number()  OVER (ORDER BY created_at) as rn FROM tweets WHERE issue='abortion') T1  WHERE rn * 2 <= (SELECT count(*) FROM tweets WHERE issue='abortion'));""")
cur.execute("""COMMIT""")
cur.execute("""CREATE UNIQUE INDEX train_id_uindex ON public.train (id);
ALTER TABLE public.train ADD CONSTRAINT train_id_pk PRIMARY KEY (id);""")

cur.execute("""COMMIT""")

cur.execute("""CREATE TABLE test AS (SELECT * FROM (SELECT *,row_number()  OVER (ORDER BY created_at) as rn FROM tweets WHERE issue='abortion') T1  WHERE rn * 2 > (SELECT count(*) FROM tweets WHERE issue='abortion'));""")
cur.execute("""COMMIT""")
cur.execute("""CREATE UNIQUE INDEX test_id_uindex ON public.test (id);
ALTER TABLE public.test ADD CONSTRAINT test_id_pk PRIMARY KEY (id);""")
cur.execute("""COMMIT""")

'''

import random
import math

cur.execute("""TRUNCATE public.test; Truncate public.train; Commit;""")

cur.execute("""SELECT id, user_id FROM tweets WHERE  issue='abortion'""")
outcur = Database.get_Cur()

test_buff = []
train_buff = []
for i in cur:
    id = i[0]
    user_id = i[1]
    if math.floor(random.random() * 2) == 0:
        test_buff.append([id, user_id])
    else:
        train_buff.append([id, user_id])
    if len(test_buff) > Database.batch_size:
        outcur.execute("""INSERT INTO test (id, user_id) VALUES """ + ',' .join(['(' + str(x[0]) + ',' + str(x[1]) + ')' for x in test_buff]))
        outcur.execute("""COMMIT""")
        del test_buff
        test_buff = []
    if len(train_buff) > Database.batch_size:
        outcur.execute("""INSERT INTO train (id, user_id) VALUES """ + ','.join(
            ['(' + str(x[0]) + ',' + str(x[1]) + ')' for x in train_buff]))
        outcur.execute("""COMMIT""")
        del train_buff
        train_buff = []
if len(train_buff) > 0:
    outcur.execute("""INSERT INTO train (id, user_id) VALUES """ + ',' .join(['(' + str(x[0]) + ',' + str(x[1]) + ')' for x in train_buff]))

if len(test_buff) > 0:
    outcur.execute("""INSERT INTO test (id, user_id) VALUES """ + ',' .join(['(' + str(x[0]) + ',' + str(x[1]) + ')' for x in test_buff]))


outcur.execute("""COMMIT;""")
