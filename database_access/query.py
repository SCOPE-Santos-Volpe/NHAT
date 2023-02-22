import psycopg2
import pandas as pd

connection = psycopg2.connect(
    host = 'database-1.ci75bfibgs4e.us-east-1.rds.amazonaws.com',
    port = 5432,
    user = 'scope_team',
    password = 'greenTea123',
    database='FARS'
    )
print("Connected to DB")
cursor=connection.cursor()


#sql = """ SELECT * FROM boundaries_mpo_AK """
#df = pd.read_sql(sql, con=connection)
#print ("stuff we get from df, ", df)


# List all tables in DB:
query = """ SELECT table_name FROM information_schema.tables WHERE table_schema='public'; """
df = pd.read_sql(query, con=connection)
print(query, df)

# Query DB to get data in a table:
query = """ SELECT * FROM BOUNDARIES_MPO_AK; """
#query = """ SELECT * FROM fars_accident_2020; """
df = pd.read_sql(query, con=connection)
print("fars_accident_2020", df)

#query = """ SELECT LATITUDE,LONGITUDE FROM fars_accident_2020; """
#df = pd.read_sql(query, con=connection)
#print("fars_accident_2020, df)

query = """ SELECT * FROM states """
df = pd.read_sql(query, con=connection)
print("states", df)

query = """ SELECT * FROM district """
df = pd.read_sql(query, con=connection)
print("district", df)

query = """ SELECT * FROM data """
df = pd.read_sql(query, con=connection)
print("data", df)
