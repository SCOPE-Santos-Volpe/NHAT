from codecs import ignore_errors
import pandas as pd
import numpy as np
import streamlit as st
import pydeck as pdk
import glob
import os
# from streamlit_folium import st_folium
# import folium
import plotly.express as px

path="FARS CSVs/"

all_files = glob.glob(os.path.join(path, "*.CSV"))


li = []

for filename in all_files:
    df = pd.read_csv(filename, index_col=None, encoding_errors='ignore', dtype={'LATITUDE': float, 'LONGITUD': float})
    if('LATITUDE' in df.columns and 'LONGITUD' in df.columns):
        li.append(df[['LATITUDE','LONGITUD']])
    print("reloading lol")

df = pd.concat(li, axis=0, ignore_index=True)

# df = pd.read_csv("accident.CSV", encoding_errors='ignore')
# df = df[['STATE','LATITUDE','LONGITUD']]
# df = df.rename(columns={'LATITUDE': 'lat','LONGITUD': 'lon'})
df = df[abs(df['LATITUDE']) <= 90] #and df['LONGITUD' != 88888888]]
df = df[abs(df['LONGITUD']) <= 180]
# print(df.columns)
# print(df.dtypes)
# print(df)


# px.set_mapbox_access_token(open(".mapbox_token").read())
# df = px.data.carshare()
# fig = px.scatter_mapbox(df, lat="LATITUDE", lon="LONGITUD",
#                   color_continuous_scale=px.colors.cyclical.IceFire, size_max=15, zoom=10)
# st.plotly_chart(fig)

fig = px.scatter_mapbox(df,
                        lon = df['LONGITUD'],
                        lat = df['LATITUDE'],
                        zoom = 2, 
                        # color = df['peak_hour'],
                        # size = df['car_hours'],
                        # width = 900,
                        # height = 600
                        # title = 'Car Share Scatter Map'
                        )
fig.update_layout(mapbox_style = "open-street-map")
fig.update_layout(autosize=True)
# fig.update_layout(margin = {"r":0, "t":0, "l":0, "b":0})
# fig.show()
st.plotly_chart(fig, use_container_width=True)

# st.pydeck_chart(pdk.Deck(
#     map_style=None,
#     initial_view_state=pdk.ViewState(
#         latitude=45,
#         longitude=-104,
#         zoom=1,
#         pitch=0,
#     ),
#     layers=[
#         pdk.Layer(
#             'ScatterplotLayer',
#             data=df,
#             get_position='[LONGITUD, LATITUDE]',
#             get_color='[255,0,0,160]',
#             get_radius=150,
#             radius_units="meters",
#             radiusMinPixels= 2,
#             radiusMaxPixels= 20,
#             # auto_highlight=True,
#             # pickable= True
#             # tooltip="Helo!"
#         ),
#         # pdk.Layer(
#         #     'HeatmapLayer',
#         #     data=df,
#         #     get_position='[LONGITUD, LATITUDE]',
#         #     # get_color='[255,0,0,160]',
#         #     # colorRange = [[63,63,63,160],[255,63,63,160]]
#         # )
#     ]
# ))