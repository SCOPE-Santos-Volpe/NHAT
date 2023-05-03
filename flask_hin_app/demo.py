"""
https://stackoverflow.com/questions/36141323/spatial-datatype-geometry-to-geojson
https://realpython.com/flask-javascript-frontend-for-rest-api/#investigate-the-project-structure\

"""

import sys
import random
from flask import Flask, render_template, jsonify, request
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
    return jsonify({"data": fars_state_county_coords})


@app.route('/get_fars_data_by_mpo/<int:state_id><string:mpo_name>')
def get_fars_data_by_mpo(state_id, mpo_name):
    # Filter data points by a particular state id
    print("getting fars data for state: ", state_id, " mpo_name: ", mpo_name)
    fars_state_mpo_data = FARS.query.filter(FARS.STATE_ID == state_id).\
                                        filter(FARS.MPO_NAME == mpo_name).all()
    fars_state_mpo_data_coords = [[point.LAT, point.LON] for point in fars_state_mpo_data]
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


def get_mpo_boundaries_from_rds(state_id:int, mpo_name:String = None):
    if mpo_name == None:
        sql = text(""" SELECT * FROM "boundaries_mpo" WHERE "STATE_ID" = {} """.format(state_id))
    else:
        sql = text(""" SELECT * FROM "boundaries_mpo" WHERE "STATE_ID" = {} AND "MPO_NAME" = '{}' """.format(state_id, mpo_name))
    gdf = gpd.read_postgis(sql, con=sqlalchemy_conn)  
    geojson = gdf.to_json()
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


def get_county_boundaries_from_rds(state_id:int, county_name:String = None):
    if county_name == None:
        sql = text(""" SELECT * FROM "boundaries_county" WHERE "STATE_ID" = {} """.format(state_id))
    else: 
        sql = text(""" SELECT * FROM "boundaries_county" WHERE "STATE_ID" = {} AND "COUNTY_NAME" = '{}' """.format(state_id, county_name))
    gdf = gpd.read_postgis(sql, con=sqlalchemy_conn)  
    geojson = gdf.to_json()
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

class hin_properties(db.Model):
    __tablename__ = 'hin_properties'
    STATE_ID = db.Column(db.Integer)
    COUNTY_ID = db.Column(db.Integer)
    MPO_ID = db.Column(db.String)
    THRESHOLD = db.Column(db.Float)
    LENGTH = db.Column(db.Float)
    NUM_CRASHES = db.Column(db.Integer)
    TOTAL_LENGTH = db.Column(db.Float)
    TOTAL_CRASHES = db.Column(db.Integer)
    PERCENT_LENGTH = db.Column(db.Float)
    PERCENT_CRASHES = db.Column(db.Float)
    DATA_SOURCE = db.Column(db.String)
    ID = db.Column(db.Integer, primary_key=True)

    def __init__(self, STATE_ID, COUNTY_ID, MPO_ID, THRESHOLD, DATA_SOURCE):
        print("init properties")
        self.STATE_ID = STATE_ID
        self.COUNTY_ID = COUNTY_ID
        self.MPO_ID = MPO_ID
        self.MPO_ID = THRESHOLD
        self.DATA_SOURCE = DATA_SOURCE
    
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    

def get_hin_from_rds(state_id:int, datasource:String, threshold: float, county_id:int = None, mpo_id:int = None):
    
    hin_property_row = get_hin_properties_from_rds(state_id, datasource, threshold, county_id, mpo_id)
    hin_id = hin_property_row.ID
    hin_state = hin_property_row.STATE_ID

    # Get hin from hin_properties - these are the polylines
    sql = text(""" SELECT * FROM "hin_state_{}" WHERE "ID" = {} """.format(hin_state, hin_id))
    hin_gdf = gpd.read_postgis(sql, con=sqlalchemy_conn)  
    hin_geojson = hin_gdf.to_json()
    return hin_geojson


def get_hin_properties_from_rds(state_id:int, datasource:String, threshold: float, county_id:int = None, mpo_id:int = None):
    print("in get hin from rds")
    # Get hin properties

    print("DATASOURCE", datasource)
    if datasource == "fars":
        datasource = "FARS"
    elif datasource == "sds":
        datasource = "SDS"
        
    hin_properties_data = None
    if county_id != None:
        hin_properties_data = hin_properties.query.filter(hin_properties.STATE_ID == state_id).\
                                        filter(hin_properties.COUNTY_ID == county_id).\
                                        filter(hin_properties.DATA_SOURCE == datasource).\
                                        filter(hin_properties.THRESHOLD == threshold).all()
    elif mpo_id != None:
        hin_properties_data = hin_properties.query.filter(hin_properties.STATE_ID == state_id).\
                                        filter(hin_properties.MPO_ID == mpo_id).\
                                        filter(hin_properties.DATA_SOURCE == datasource).\
                                        filter(hin_properties.THRESHOLD == threshold).all()
    # print("HIN PROPERTIES DATA: ", type(hin_properties_data))
    print("HIN PROPERTIES DATA: ", hin_properties_data)

    hin_property_row = hin_properties_data[0]

    return hin_property_row

# Get HIN by MPO/County and properties
@app.route('/get_hin_by_mpo_id_and_properties/<int:state_id><int:mpo_id><float:threshold>')
def get_hin_by_mpo_id_and_properties(state_id, mpo_id, threshold):
    print("getting hin boundaries for {} in # {} for threshold {}".format(state_id, mpo_id, threshold))
    hin_geojson = get_hin_from_rds(state_id, threshold = threshold, mpo_id = mpo_id)
    return hin_geojson

# Get HIN by County and properties
@app.route('/get_hin_by_county_id_and_properties/', methods = ['GET'])
def get_hin_by_county_id_and_properties():
    state_id = request.args.get('state_id')
    county_id = request.args.get('county_id')
    threshold = request.args.get('threshold')
    datasource = request.args.get('datasource')

    print("getting hin boundaries for {} in # {} for threshold {} using {}".format(state_id, county_id, threshold, datasource))
    hin_geojson = get_hin_from_rds(state_id, datasource = datasource, threshold = threshold, county_id = county_id)
    return hin_geojson

# Get HIN properties
@app.route('/get_hin_properties/', methods = ['GET'])
def get_hin_properties():
    state_id = request.args.get('state_id')
    county_id = request.args.get('county_id')
    threshold = request.args.get('threshold')
    datasource = request.args.get('datasource')
    
    print("getting hin properties for {} in # {} for threshold {} using {}".format(state_id, county_id, threshold, datasource))
    hin_properties = get_hin_properties_from_rds(state_id, datasource = datasource, threshold = threshold, county_id = county_id)
    return jsonify(hin_properties.as_dict())


@app.route('/')
def index():
    states = States.query.all()
    print("states:", states)
    return render_template('index.html', states=states) 

if __name__ == '__main__':
    # app.run(host="localhost", port=8080, debug=True)
    app.run(debug=True)
