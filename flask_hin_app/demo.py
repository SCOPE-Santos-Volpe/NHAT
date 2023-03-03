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
from sqlalchemy import create_engine, Table, Column, Integer, String


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

# TODO: Database storing list of states along with their abbreviations, ids, and xy coords
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

class Boundaries_state(db.Model):
    STATE = db.Column(db.Integer, db.ForeignKey('states.id'), primary_key=True) 
    # state = db.relationship("States")
    name = db.Column('NAME', db.String(80))
    census_area = db.Column('CENSUSAREA', db.Float)
    geom = db.Column(Geometry)

    print("boundaries_state (STATE): ", STATE)

    def __repr__(self):
        return f'<{int(self.STATE)} {self.name} >'
    # filtered_states = Boundaries_state.query.filter_by(STATE=state_id).all()
    # print("state_id, filtered_states:", state_id, filtered_states)
    # return jsonify({"data": filtered_states[0].name})


def get_state_geojson_from_rds(state_id:int = None):
    """ Returns a geojson object from the boundaries_state table in the RDS
        that matches the given state_id

        Args: 
            state_id: integer. If none, return all shapefiles

        Returns:
            geojson: geojson object of the particular state. 
    """
    if state_id == None:
        sql = """ SELECT * FROM "boundaries_state" """
    else:
        sql = """ SELECT * FROM "boundaries_state" WHERE "STATE" = {} """.format(state_id)
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

@app.route('/')
def index():
    states = States.query.all()
    # state_boundaries = Boundaries_state.query.filter_by(state=1).all()
    print("states:", states)
    # Return states as a variable ot be used in index.html
    return render_template('index.html', states=states) 

if __name__ == '__main__':
    # app.run(host="localhost", port=8080, debug=True)
    app.run()
