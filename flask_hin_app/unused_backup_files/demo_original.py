import sys
import random
from flask import Flask, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy

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
    states = States.query.all()
    print("states:", states)
    return render_template('index.html', districts=states)


@app.route('/district/<int:district_id>')
def district(district_id):
    points = Fars_accident_2020.query.filter_by(state=district_id).all()
    coords = [[point.latitude, point.longitude] for point in points]
    print("district_id, points, coords", district_id, points, coords)
    return jsonify({"data": coords})


if __name__ == '__main__':
    app.run()
