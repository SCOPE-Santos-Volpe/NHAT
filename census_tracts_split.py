import json
import helper
import pandas as pd
  

states_df = helper.load_df_from_csv(path='states.csv', low_memory = False)
# Dictionaries to convert the STATE_INITIAL to STATE_ID & STATE_NAME
# d_state_initial2id = dict(zip(states_df.state, states_df.id))
# d_state_initial2name = dict(zip(states_df.state, states_df.name))
# d_state_id2name = dict(zip(states_df.id, states_df.name))
d_state_name2initial = dict(zip(states_df.name, states_df.state))

# Opening JSON file
f = open('Shapefiles/census_tracts.geojson')
  
# returns JSON object as dictionary
data = json.load(f)
print("loaded in geojson")


# state_codes = {
#     'AL': '01', 'AK': '02', 'AZ': '04', 'AR': '05', 'CA': '06', 'CO': '08',
#     'CT': '09', 'DE': '10', 'DC': '11', 'FL': '12', 'GA': '13', 'HI': '15',
#     'ID': '16', 'IL': '17', 'IN': '18', 'IA': '19', 'KS': '20', 'KY': '21',
#     'LA': '22', 'ME': '23', 'MD': '24', 'MA': '25', 'MI': '26', 'MN': '27',
#     'MS': '28', 'MO': '29', 'MT': '30', 'NE': '31', 'NV': '32', 'NH': '33', 
#     'NJ': '34', 'NM': '35', 'NY': '36', 'NC': '37', 'ND': '38', 'OH': '39',
#     'OK': '40', 'OR': '41', 'PA': '42', 'RI': '44', 'SC': '45', 'SD': '46',
#     'TN': '47', 'TX': '48', 'UT': '49', 'VT': '50', 'VA': '51', 'WA': '53', 
#     'WV': '54', 'WI': '55', 'WY': '56', 'AS': '60', 'GU': '66', 'MP': '69',
#     'PR': '72', 'VI': '78'
# }

# for key in state_codes.keys():
#     int_code = int(state_codes[key])
#     state_codes[key]= int_code

# res = dict((v,k) for k,v in state_codes.items())

state_dict = {}
# print(data["features"])
  
# Iterating through the json list
for i, tract in enumerate(data['features']):
    state_name = str(tract["properties"]["SF"])
    #json_object = json.dumps(data['features'][i])
    if(state_name not in state_dict):
        state_dict[state_name] = []
    state_dict[state_name].append(data['features'][i])

print("finished categorizing into diff states")

for state_name in state_dict.keys():
    string = "{\"type\":\"FeatureCollection\",\"name\":\"census_tracts_split\",\"features\":" + json.dumps(state_dict[state_name]) + "}"

    label = state_name
    if state_name in d_state_name2initial:
        label = d_state_name2initial[state_name]
    with open(f"Shapefiles/census_tracts_by_state/census_tract_{label}.geojson", "w") as outfile:
        print("writing to file for ", state_name)
        outfile.write(string)

# Closing file
f.close()
