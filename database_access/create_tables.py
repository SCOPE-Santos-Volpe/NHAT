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


# Create FARS_ACCIDENT_2020 table in database:
#cursor.execute("""CREATE TABLE FARS_ACCIDENT_2020(
#STATE integer,
#STATENAME text,
#LATITUDE float,
#LONGITUDE float)""")
#connection.commit()
#print("Created table FARS_ACCIDENT_2020")

# Add data from CSV file into table FARS_ACCIDENT_2020 in the database:
#with open('FARS_ACCIDENT_2020.csv', 'r') as row:
#    next(row)
#    cursor.copy_from(row, 'fars_accident_2020', sep=',')
#connection.commit()
#print("Uploaded FARS data to table FARS_ACCIDENT_2020")

# Create STATES table in database:
#cursor.execute("""CREATE TABLE STATES(
#ID SERIAL PRIMARY KEY,
#NAME text,
#LATITUDE float,
#LONGITUDE float)""")
#connection.commit()
#print("Created table STATES")

# Add data from CSV file into table STATES in the database:
#with open('STATES.csv', 'r') as row:
#    next(row)
#    cursor.copy_from(row, 'states', sep=',')
#connection.commit()
#print("Uploaded STATES data to table")


# List all tables in DB:
query = """ SELECT table_name FROM information_schema.tables WHERE table_schema='public'; """
df = pd.read_sql(query, con=connection)
print(query, df)

# Print data in fars_accident_2020 table in DB:
query = """ SELECT * FROM fars_accident_2020; """
df = pd.read_sql(query, con=connection)
print("fars_accident_2020", df)

# Print data in states table in DB:
query = """ SELECT * FROM states """
df = pd.read_sql(query, con=connection)
print("states", df)
