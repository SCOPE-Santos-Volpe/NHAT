import sqlalchemy as db

# Our DB on RDS:
engine = db.create_engine("postgresql://scope_team:greenTea123@database-1.ci75bfibgs4e.us-east-1.rds.amazonaws.com/FARS")
conn = engine.connect()

metadata = db.MetaData()
metadata.bind = engine
metadata.create_all(engine)

# Get table fars_accident_2020 from our DB:
fars_accident_2020 = db.Table('fars_accident_2020', metadata, autoload=True, autoload_with=engine) #Table object

# Print table metadata:
print("metadata:")
print(repr(metadata.tables['fars_accident_2020']))
#print(repr(metadata.tables['states']))

# Print column names aka keys in the table:
print("fars_accident_2020 table keys:\n", fars_accident_2020.columns.keys())

# Try to update the data in table:
#from sqlalchemy import update
#stmt = (
#    update(states)
#    .where(states.c.id == "0")
#    .values(num="0")
#)
#print(stmt)

# Try to delete rows with name value = Alabama from table:
#from sqlalchemy import delete
#dele = fars_accident_2020.delete().where(fars_accident_2020.c.name == "Alabama")
#engine.execute(dele)
#print("deleted")

# Try to remove the column num from table:
#fars_accident_2020._columns.remove(fars_accident_2020._columns['num'])


# Make query and get result:
query = fars_accident_2020.select() #SELECT * FROM divisions
#query = db.select([division]) # also equivalent to SELECT * FROM divisions
print("\nQuery =\n", query)
exe = conn.execute(query) #executing the query
result = exe.fetchmany(5) #extracting top 5 results
print("\nQuery result = \n", result)
