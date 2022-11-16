import psycopg2
connection = psycopg2.connect(
    host = 'database-1.ci75bfibgs4e.us-east-1.rds.amazonaws.com',
    port = 5432,
    user = 'scope_team',
    password = 'greenTea123',
    database='FARS'
    )

# cursor object to interact and execute the commands on the DB
cursor=connection.cursor()

# Create tables
cursor.execute("""CREATE TABLE FARS(
id SERIAL PRIMARY KEY,
name text,
sex text,
age float,
sibsp integer,
parch integer)""")

cursor.execute("""CREATE TABLE survival(
id SERIAL PRIMARY KEY,
survived integer)""")

cursor.execute("""CREATE TABLE tripInfo(
id SERIAL PRIMARY KEY,
pclass integer,
ticket text,
fare float,
cabin text,
embarked text)""")

connection.commit()
