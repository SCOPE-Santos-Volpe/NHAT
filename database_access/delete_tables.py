import sqlalchemy as db

# Our DB on RDS:
engine = db.create_engine("postgresql://scope_team:greenTea123@database-1.ci75bfibgs4e.us-east-1.rds.amazonaws.com/FARS")
conn = engine.connect()

metadata = db.MetaData()
metadata.bind = engine
metadata.create_all(engine)

# Get table point from our DB:
point_table = db.Table('point', metadata, autoload=True, autoload_with=engine)
print(point_table)

# Delete table point from DB:
del_table = point_table.drop()
engine.execute(del_table)
print("point table deleted")
