"""
https://stackoverflow.com/questions/36141323/spatial-datatype-geometry-to-geojson
https://realpython.com/flask-javascript-frontend-for-rest-api/#investigate-the-project-structure\

"""

import sys
import random
from flask import Flask, render_template, jsonify #, request
from flask_sqlalchemy import SQLAlchemy
from geoalchemy2 import Geometry, WKTElement
import geopandas as gpd
from sqlalchemy import create_engine, Table, Column, Integer, String, text


# Establish sqlalchemy connection
conn_string = 'postgresql://scope_team:greenTea123@database-1.ci75bfibgs4e.us-east-1.rds.amazonaws.com/FARS'
db = create_engine(conn_string)
sqlalchemy_conn = db.connect()
print('Python connected to PostgreSQL via Sqlalchemy')

# Connect to database using the model abstraction
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://scope_team:greenTea123@database-1.ci75bfibgs4e.us-east-1.rds.amazonaws.com/FARS'
db = SQLAlchemy(app)

BASECOORDS = [40.0, -90.0]

class Fars_accident_2020(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    state = db.Column(db.Integer, db.ForeignKey('states.id'))
    states = db.relationship("States")

    def __init__(self, id, states, latitude, longitude):
        print("init point")
        self.id = id
        self.states = states
        self.lat = latitude
        self.lng = longitude

    def __repr__(self):
        return "<Point %d: Lat %s Lng %s>" % (self.id, self.latitude, self.longitude)

    @property
    def get_latitude(self):
        return self.latitude

    @property
    def get_longitude(self):
        return self.longitude

class FARS(db.Model):
    __tablename__ = 'FARS'
    YEAR = db.Column(db.Integer)
    STATE_ID = db.Column(db.Integer)
    STATE_NAME = db.Column(db.String(80))
    COUNTY_ID = db.Column(db.Float)
    COUNTY_NAME = db.Column(db.String(80))
    MPO_ID = db.Column(db.Float)
    MPO_NAME = db.Column(db.String(80))
    IS_FATAL =  db.Column(db.Integer)
    SEVERITY = db.Column(db.Integer)
    IS_PED = db.Column(db.Integer)
    IS_CYC = db.Column(db.Integer)
    WEATHER_COND = db.Column(db.String(80))
    LIGHT_COND = db.Column(db.String(80))
    ROAD_COND = db.Column(db.String(80))
    ROAD_NAME = db.Column(db.String(80))
    IS_INTERSECTION = db.Column(db.Integer)
    LAT = db.Column(db.Float, primary_key=True)
    LON = db.Column(db.Float)

    def __init__(self, STATE_ID, COUNTY_ID, LAT, LON):
        print("init point")
        self.STATE_ID = STATE_ID
        self.COUNTY_ID = COUNTY_ID
        self.LAT = LAT
        self.LON = LON

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self):
        return "<State %d: Lat %s Lng %s>" % (self.STATE_ID, self.LAT, self.LON)

@app.route('/get_fars_data_by_county/<int:state_id><string:county_name>')
def get_fars_data_by_county(state_id, county_name):
    # Filter data points by a particular state id
    print("getting fars data for state: ", state_id, " county_name: ", county_name)
    fars_state_county_data = FARS.query.filter(FARS.STATE_ID == state_id).\
                                        filter(FARS.COUNTY_NAME == county_name).all()
    fars_state_county_coords = [[point.LAT, point.LON] for point in fars_state_county_data]
    print(fars_state_county_coords)
    return jsonify({"data": fars_state_county_coords})


@app.route('/get_fars_data_by_mpo/<int:state_id><string:mpo_name>')
def get_fars_data_by_mpo(state_id, mpo_name):
    # Filter data points by a particular state id
    print("getting fars data for state: ", state_id, " mpo_name: ", mpo_name)
    fars_state_mpo_data = FARS.query.filter(FARS.STATE_ID == state_id).\
                                        filter(FARS.MPO_NAME == mpo_name).all()
    fars_state_mpo_data_coords = [[point.LAT, point.LON] for point in fars_state_mpo_data]
    print(fars_state_mpo_data_coords)
    return jsonify({"data": fars_state_mpo_data_coords})


class SDS_California(db.Model):
    __tablename__ = 'SDS_California'
    YEAR = db.Column(db.Integer)
    COUNTY_ID = db.Column(db.Float)
    COUNTY_NAME = db.Column(db.String(80))
    MPO_ID = db.Column(db.Float)
    MPO_NAME = db.Column(db.String(80))
    IS_FATAL =  db.Column(db.Integer)
    SEVERITY = db.Column(db.Integer)
    IS_PED = db.Column(db.Integer)
    IS_CYC = db.Column(db.Integer)
    WEATHER_COND = db.Column(db.String(80))
    LIGHT_COND = db.Column(db.String(80))
    ROAD_COND = db.Column(db.String(80))
    ROAD_NAME = db.Column(db.String(80))
    IS_INTERSECTION = db.Column(db.Integer)
    LAT = db.Column(db.Float, primary_key=True)
    LON = db.Column(db.Float)

    def __init__(self, STATE_ID, COUNTY_ID, LAT, LON):
        print("init point")
        self.COUNTY_ID = COUNTY_ID
        self.LAT = LAT
        self.LON = LON

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self):
        return "<State %d: Lat %s Lng %s>" % (self.LAT, self.LON)

class SDS_Massachusetts(db.Model):
    __tablename__ = 'SDS_Massachusetts'
    YEAR = db.Column(db.Integer)
    COUNTY_ID = db.Column(db.Float)
    COUNTY_NAME = db.Column(db.String(80))
    MPO_ID = db.Column(db.Float)
    MPO_NAME = db.Column(db.String(80))
    IS_FATAL =  db.Column(db.Integer)
    SEVERITY = db.Column(db.Integer)
    IS_PED = db.Column(db.Integer)
    IS_CYC = db.Column(db.Integer)
    WEATHER_COND = db.Column(db.String(80))
    LIGHT_COND = db.Column(db.String(80))
    ROAD_COND = db.Column(db.String(80))
    ROAD_NAME = db.Column(db.String(80))
    IS_INTERSECTION = db.Column(db.Integer)
    LAT = db.Column(db.Float, primary_key=True)
    LON = db.Column(db.Float)

    def __init__(self, STATE_ID, COUNTY_ID, LAT, LON):
        print("init point")
        self.COUNTY_ID = COUNTY_ID
        self.LAT = LAT
        self.LON = LON

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self):
        return "<State %d: Lat %s Lng %s>" % (self.LAT, self.LON)


SDS_database_name_dict = {
    6: SDS_California,
    25: SDS_Massachusetts
}

@app.route('/get_sds_data_by_county/<int:state_id><string:county_name>')
def get_sds_data_by_county(state_id, county_name):
    # Filter data points by a particular state id
    print("getting fars data for state: ", state_id, " county_name: ", county_name)
    SDS_table = SDS_database_name_dict[state_id]
    SDS_county_data = SDS_table.query.filter(SDS_table.COUNTY_NAME == county_name).all()
    if state_id == 6:
            SDS_coords = [[point.LAT, -point.LON] for point in SDS_county_data]
    else:
        SDS_coords = [[point.LAT, point.LON] for point in SDS_county_data]
    print(SDS_coords)
    return jsonify({"data": SDS_coords})

@app.route('/get_sds_data_by_mpo/<int:state_id><string:mpo_name>')
def get_sds_data_by_mpo(state_id, mpo_name):
    # Filter data points by a particular state id
    print("getting fars data for state: ", state_id, " mpo_name: ", mpo_name)
    SDS_table = SDS_database_name_dict[state_id]
    SDS_mpo_data = SDS_table.query.filter(SDS_table.MPO_NAME == mpo_name).all()
    if state_id == 6:
            SDS_coords = [[point.LAT, -point.LON] for point in SDS_mpo_data]
    else:
        SDS_coords = [[point.LAT, point.LON] for point in SDS_mpo_data]
    print(SDS_coords)
    return jsonify({"data": SDS_coords})

class States(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)

    def __init__(self, id, name, lat, lng):
        print("init district")
        self.id = id
        self.name = name
        self.latitude = lat
        self.longitude = lng


def get_state_geojson_from_rds(state_id:int = None):
    """ Returns a geojson object from the boundaries_state table in the RDS
        that matches the given state_id

        Args: 
            state_id: integer. If none, return all shapefiles

        Returns:
            geojson: geojson object of the particular state. 
    """
    if state_id == None:
        sql = text(""" SELECT * FROM "boundaries_state" """)
    else:
        sql = text(""" SELECT * FROM "boundaries_state" WHERE "STATE_ID" = {} """.format(state_id))
    gdf = gpd.read_postgis(sql, con=sqlalchemy_conn)  
    geojson = gdf.to_json()
    return geojson

def get_mpo_boundaries_from_rds(state_id:int, mpo_name:String = None):
    if mpo_name == None:
        sql = text(""" SELECT * FROM "boundaries_mpo" WHERE "STATE_ID" = {} """.format(state_id))
    else:
        sql = text(""" SELECT * FROM "boundaries_mpo" WHERE "STATE_ID" = {} AND "MPO_NAME" = '{}' """.format(state_id, mpo_name))
    gdf = gpd.read_postgis(sql, con=sqlalchemy_conn)  
    geojson = gdf.to_json()
    return geojson


def get_county_boundaries_from_rds(state_id:int, county_name:String = None):
    if county_name == None:
        sql = text(""" SELECT * FROM "boundaries_county" WHERE "STATE_ID" = {} """.format(state_id))
    else: 
        sql = text(""" SELECT * FROM "boundaries_county" WHERE "STATE_ID" = {} AND "COUNTY_NAME" = '{}' """.format(state_id, county_name))
    gdf = gpd.read_postgis(sql, con=sqlalchemy_conn)  
    geojson = gdf.to_json()
    return geojson

def get_census_tract_boundaries_from_rds(state_id:int, county_name:String = None, mpo_name:String = None):
    if county_name != None:
        sql = text(""" SELECT * FROM "boundaries_census_tract_v3" WHERE "STATE_ID" = {} AND "COUNTY_NAME" = '{}' AND "IDENTIFIED_AS_DISADVANTAGED" = 1 """.format(state_id, county_name))
    elif mpo_name != None:
        sql = text(""" SELECT * FROM "boundaries_census_tract_v3" WHERE "STATE_ID" = {} AND "MPO_NAME" = '{}' AND "IDENTIFIED_AS_DISADVANTAGED" = 1 """.format(state_id, mpo_name))
    elif state_id == None:
        sql = text(""" SELECT * FROM "boundaries_census_tract_v3" """)
    else:
        sql = text(""" SELECT * FROM "boundaries_census_tract_v3" WHERE "STATE_ID" = {} """.format(state_id))
    gdf = gpd.read_postgis(sql, con=sqlalchemy_conn)  
    geojson = gdf.to_json()
    return geojson

def get_fars_from_rds(state_id:int, county_name:String = None, mpo_name:String = None):
    if county_name != None:
        sql = text(""" SELECT * FROM "FARS" WHERE "STATE_ID" = {} AND "COUNTY_NAME" = '{}' """.format(state_id, county_name))
    elif mpo_name != None:
        sql = text(""" SELECT * FROM "FARS" WHERE "STATE_ID" = {} AND "MPO_NAME" = '{}' """.format(state_id, mpo_name))
    gdf = gpd.read_postgis(sql, con=sqlalchemy_conn)  
    geojson = gdf.to_json()
    return geojson


# Query fars accident data by state
@app.route('/get_fars_data/<int:state_id>')
def get_fars_data(state_id):
    # Filter data points by a particular state id
    fars_state_data = Fars_accident_2020.query.filter_by(state=state_id).all()
    fars_state_coords = [[point.latitude, point.longitude] for point in fars_state_data]
    # print("state_id, points, coords", state_id, fars_state_data, fars_state_coords)
    return jsonify({"data": fars_state_coords})



# Get state boundaries and return it as as a geojson
@app.route('/get_state_boundaries_by_state/<int:state_id>')
def get_state_boundaries_by_state(state_id):
    print("getting state boundaries for # {}".format(state_id))
    geojson = get_state_geojson_from_rds(state_id)
    return geojson

@app.route('/get_all_state_boundaries/')
def get_all_state_boundaries():
    print("getting all state boundaries")
    geojson = get_state_geojson_from_rds()
    return geojson

@app.route('/get_mpo_boundaries_by_state_id/<int:state_id>')
def get_mpo_boundaries_by_state_id(state_id):
    print("getting mpo boundaries for # {}".format(state_id))
    geojson = get_mpo_boundaries_from_rds(state_id)
    return geojson

@app.route('/get_mpo_boundaries_by_state_id_and_mpo_name/<int:state_id><string:mpo_name>')
def get_mpo_boundaries_by_state_id_and_mpo_name(state_id, mpo_name):
    print("getting mpo boundaries for {} in # {}".format(mpo_name, state_id))
    geojson = get_mpo_boundaries_from_rds(state_id, mpo_name)
    return geojson

@app.route('/get_county_boundaries_by_state_id/<int:state_id>')
def get_county_boundaries_by_state_id(state_id):
    print("getting county boundaries for # {}".format(state_id))
    geojson = get_county_boundaries_from_rds(state_id)
    return geojson

@app.route('/get_county_boundaries_by_state_id_and_county_name/<int:state_id><string:county_name>')
def get_county_boundaries_by_state_id_and_county_name(state_id, county_name):
    print("getting county boundaries for {} in # {}".format(county_name, state_id))
    geojson = get_county_boundaries_from_rds(state_id, county_name)
    return geojson

@app.route('/get_census_tract_boundaries/')
def get_census_tract_boundaries():
    print("getting census tract boundaries")
    geojson = get_census_tract_boundaries_from_rds()
    return geojson

@app.route('/get_census_tract_boundaries_by_state_id/<int:state_id>')
def get_census_tract_boundaries_by_state_id(state_id):
    print("getting census tract boundaries for # {}".format(state_id))
    geojson = get_census_tract_boundaries_from_rds(state_id)
    return geojson

@app.route('/get_census_tract_boundaries_by_state_id_and_county_name/<int:state_id><string:county_name>')
def get_census_tract_boundaries_by_state_id_and_county_name(state_id, county_name):
    print("getting census tract boundaries for {} in # {}".format(county_name, state_id))
    geojson = get_census_tract_boundaries_from_rds(state_id, county_name=county_name)
    return geojson

@app.route('/get_census_tract_boundaries_by_state_id_and_mpo_name/<int:state_id><string:mpo_name>')
def get_census_tract_boundaries_by_state_id_and_mpo_name(state_id, mpo_name):
    print("getting census tract for {} in # {}".format(mpo_name, state_id))
    geojson = get_census_tract_boundaries_from_rds(state_id, mpo_name=mpo_name)
    return geojson

@app.route('/')
def index():
    states = States.query.all()
    print("states:", states)
    return render_template('index.html', states=states) 

if __name__ == '__main__':
    # app.run(host="localhost", port=8080, debug=True)
    app.run(debug=True)
