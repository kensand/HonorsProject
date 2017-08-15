from Library import Database

cur = Database.get_Cur()

cur.execute("""CREATE TABLE train AS (SELECT * FROM (SELECT *,row_number()  OVER (ORDER BY created_at) as rn FROM tweets WHERE issue='abortion') T1  WHERE rn * 2 <= (SELECT count(*) FROM tweets WHERE issue='abortion'));""")
cur.execute("""COMMIT""")
cur.execute("""CREATE UNIQUE INDEX test_id_uindex ON public.test (id);
ALTER TABLE public.test ADD CONSTRAINT test_id_pk PRIMARY KEY (id);""")
cur.execute("""COMMIT""")

cur.execute("""CREATE TABLE test AS (SELECT * FROM (SELECT *,row_number()  OVER (ORDER BY created_at) as rn FROM tweets WHERE issue='abortion') T1  WHERE rn * 2 > (SELECT count(*) FROM tweets WHERE issue='abortion'));""")
cur.execute("""COMMIT""")
cur.execute("""CREATE UNIQUE INDEX train_id_uindex ON public.train (id);
ALTER TABLE public.train ADD CONSTRAINT train_id_pk PRIMARY KEY (id);""")
cur.execute("""COMMIT""")