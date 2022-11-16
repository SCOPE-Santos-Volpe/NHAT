import psycopg2
import pandas as pd

connection = psycopg2.connect(
    host = 'database-1.ci75bfibgs4e.us-east-1.rds.amazonaws.com',
    port = 5432,
    user = 'scope_team',
    password = 'greenTea123',
    database='FARS'
    )

# cursor object to interact and execute the commands on the DB
cursor=connection.cursor()
print("connected to DB")

# # Create tables - THESE ARE FAKE FILLER TABLES RN
# cursor.execute("""CREATE TABLE FARS(
# id SERIAL PRIMARY KEY,
# name text,
# sex text,
# age float,
# sibsp integer,
# parch integer)""")

# cursor.execute("""CREATE TABLE survival(
# id SERIAL PRIMARY KEY,
# survived integer)""")

# cursor.execute("""CREATE TABLE tripInfo(
# id SERIAL PRIMARY KEY,
# pclass integer,
# ticket text,
# fare float,
# cabin text,
# embarked text)""")

# connection.commit()


# using pandas to execute SQL queries
#TODO: Need to switch this command to SQL Alchemy

sql = """
SELECT "table_name","column_name", "data_type", "table_schema"
FROM INFORMATION_SCHEMA.COLUMNS
WHERE "table_schema" = 'public'
ORDER BY table_name  
"""
pd.read_sql(sql, con=connection)