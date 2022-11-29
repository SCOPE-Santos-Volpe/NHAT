# import json
import geojson
from shapely.geometry import shape, Point, Polygon, MultiPolygon
import pandas as pd


state_codes = {
    'AL': '01', 'AK': '02', 'AZ': '04', 'AR': '05', 'CA': '06', 'CO': '08',
    'CT': '09', 'DE': '10', 'DC': '11', 'FL': '12', 'GA': '13', 'HI': '15',
    'ID': '16', 'IL': '17', 'IN': '18', 'IA': '19', 'KS': '20', 'KY': '21',
    'LA': '22', 'ME': '23', 'MD': '24', 'MA': '25', 'MI': '26', 'MN': '27',
    'MS': '28', 'MO': '29', 'MT': '30', 'NE': '31', 'NV': '32', 'NH': '33', 
    'NJ': '34', 'NM': '35', 'NY': '36', 'NC': '37', 'ND': '38', 'OH': '39',
    'OK': '40', 'OR': '41', 'PA': '42', 'RI': '44', 'SC': '45', 'SD': '46',
    'TN': '47', 'TX': '48', 'UT': '49', 'VT': '50', 'VA': '51', 'WA': '53', 
    'WV': '54', 'WI': '55', 'WY': '56', 'AS': '60', 'GU': '66', 'MP': '69',
    'PR': '72', 'VI': '78'
}

def load_geojson(path='Shapefiles/gz_2010_us_040_00_500k.geojson'):
    with open(path) as f:
        states = geojson.load(f)

    states_dict = {}

    for i in range(len(states['features'])):
        state_name = states['features'][i]['properties']['NAME']
        state_coords = shape(states['features'][i]['geometry'])
        states_dict[state_name] = state_coords

    return states_dict

def get_fars(filename = 'combined_FARS.csv'):
    df=pd.read_csv(filename)
    return df



def main():
    fars = get_fars()
    states_dict = load_geojson()
    state_multipoly = states_dict['California']


    testloc = Point(-122.4721043962023, 37.74900843850233)

    # thing = fars.columns

    fars['point_object'] = fars.apply(lambda x: Point(x['LONGITUD'],x['LATITUDE']), axis=1)
    fars['state_being_checked'] = 'California'
    print(fars)
    fars['point_in_state'] = fars.apply(lambda x: state_multipoly.contains(x['point_object']), axis=1)
    # fars['point_object'] = fars.apply(lambda x: x['LONGITUD'], axis=1)

    # thing = fars['point_object']

    thing = fars

    print(thing)
    print(type(thing))

if __name__=="__main__":
    main()

# test = geojson.intersects(thing,testloc)

# MultiPolygon.contains(thing, testloc)

# thing.contains(testloc)
