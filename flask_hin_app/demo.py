import sys
import random
from flask import Flask, render_template, jsonify #, request
from flask_sqlalchemy import SQLAlchemy
# from geoalchemy2 import Geometry, WKTElement
# from sqlalchemy.dialects.postgresql import JSON

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://scope_team:greenTea123@database-1.ci75bfibgs4e.us-east-1.rds.amazonaws.com/FARS'
db = SQLAlchemy(app)

BASECOORDS = [40.0, -90.0]


map_state_codes_to_nums = { "AL":1, "AK":2, "AZ":4, "AR":5, "CA": 6, "CO":8, "CT":9, "DE":10, 
                            "DC":11, "FL":12, "GA":13, "HI":15, "ID":16, "IL":17, "IN":18, 
                            "IA":19, "KS":20, "KY":21, "LA":22, "ME":23, "MD":24, "MA":25,
                            "MI":26, "MN":27, "MS":28, "MO":29, "MT":30, "NE":31, "NV":32,
                            "NH":33, "NJ":34, "NM":35, "NY":36, "NC":37, "ND":38, "OH":39, 
                            "OK":40, "OR":41, "PA":42, "PR":72, "RI":44, "SC":45, "SD":46, 
                            "TN":47, "TX":48, "UT":49, "VT":50, "VA":51, "VI":78, "WA":53,
                            "WV":54, "WI":55, "WY":56 }

class Fars_accident_2020(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    state = db.Column(db.Integer, db.ForeignKey('states.id'))
    states = db.relationship("States")

    def __init__(self, id, states, lat, lng):
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

# class Boundaries_state(db.Model):
#     id = db.Column('STATE', db.Integer, primary_key=True)
#     NAME = db.Column(db.String(80))
#     CENSUSAREA = db.Column(db.Float)
#     geom = db.Column(Geometry)
#     states = db.relationship("States")

#     # sql = """ SELECT * FROM "boundaries_mpo_AK" """
#     # df = gpd.read_postgis(sql, con=sqlalchemy_conn)  
#     # print (df)


#     def __init__(self, id, name, lat, lng):
#         print("init boundaries_state")
#         self.id = id
#         self.name = name
#         self.latitude = lat
#         self.longitude = lng

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

@app.route('/')
def index():
	# return 'Hello World!'
    # return render_template('index.html')
    states = States.query.all()
    print("states:", states)
    return render_template('index.html', districts=states)

# Get FARS points by state id
@app.route('/district/<int:district_id>')
def district(district_id):
    points = Fars_accident_2020.query.filter_by(state=district_id).all()
    coords = [[point.latitude, point.longitude] for point in points]
    print("district_id, points, coords", district_id, points, coords)
    return jsonify({"data": coords})

# # Get shapefile boundaries by state
# @app.route('/state_boundaries/<int:district_id>')
# def district(district_id):
#     points = Fars_accident_2020.query.filter_by(state=district_id).all()
#     coords = [[point.latitude, point.longitude] for point in points]
#     print("district_id, points, coords", district_id, points, coords)
#     return jsonify({"data": coords})

# @app.route('/mpo_boundaries/<int:district_id>')
# def district(district_id):
#     points = Fars_accident_2020.query.filter_by(state=district_id).all()
#     coords = [[point.latitude, point.longitude] for point in points]
#     print("district_id, points, coords", district_id, points, coords)
#     return jsonify({"data": coords})


if __name__ == '__main__':
    # app.run(host="localhost", port=8080, debug=True)
    app.run()
