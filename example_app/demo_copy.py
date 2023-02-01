import sys
import random
from flask import Flask, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://scope_team:greenTea123@database-1.ci75bfibgs4e.us-east-1.rds.amazonaws.com/FARS'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'

db = SQLAlchemy(app)

BASECOORDS = [40.0, -90.0]

#class Point(db.Model):
class Fars_accident_2020(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    #latitude_off = db.Column(db.Float)
    #longitude_off = db.Column(db.Float)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    #district_id = db.Column(db.Integer, db.ForeignKey('district.id'))
    state = db.Column(db.Integer, db.ForeignKey('states.id'))
    #district = db.relationship("District")
    states = db.relationship("States")

    def __init__(self, id, states, lat, lng):
        print("init point")
        self.id = id
        #self.district = district
        self.states = states
        #self.latitude_off = lat
        #self.longitude_off = lng
        self.lat = latitude
        self.lng = longitude

    def __repr__(self):
        #return "<Point %d: Lat %s Lng %s>" % (self.id, self.latitude_off, self.longitude_off)
        return "<Point %d: Lat %s Lng %s>" % (self.id, self.latitude, self.longitude)

    @property
    def get_latitude(self):
        #return self.latitude_off + self.district.latitude
        return self.latitude

    @property
    def get_longitude(self):
        #return self.longitude_off + self.district.longitude
        return self.longitude

#class District(db.Model):
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
    #districts = District.query.all()
    #districts = States.query.all()
    states = States.query.all()
    print("states:", states)
    #return render_template('index.html', districts=districts)
    return render_template('index.html', districts=states)


@app.route('/district/<int:district_id>')
def district(district_id):
#def district(state):
    #points = Point.query.filter_by(district_id=district_id).all()
    points = Fars_accident_2020.query.filter_by(state=district_id).all()
    #points = Fars_accident_2020.query.filter_by(state=state).all()
    coords = [[point.latitude, point.longitude] for point in points]
    print("district_id, points, coords", district_id, points, coords)
    return jsonify({"data": coords})


def make_random_data(db):
    print("turned off mkdb ability")
#    NDISTRICTS = 5
#    NPOINTS = 10
#    for did in range(NDISTRICTS):
#        district = District(did, "District %d" % did, BASECOORDS[0], BASECOORDS[1])
#        db.session.add(district)
#        for pid in range(NPOINTS):
#            lat = random.random() - 0.5
#            lng = random.random() - 0.5
#            row = Point(pid + NPOINTS * did, district, lat, lng)
#            db.session.add(row)
#    db.session.commit()


if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == 'mkdb':
            with app.app_context():
                db.create_all()
                make_random_data(db)
    else:
        # app.run(debug=True)
        app.run()
