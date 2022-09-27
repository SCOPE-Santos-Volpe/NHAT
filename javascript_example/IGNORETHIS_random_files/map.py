import pandas as pd
import numpy as np
import streamlit as st
import pydeck as pdk

import time 

df = pd.read_csv("accident.CSV", encoding_errors='ignore')
df = df[['LATITUDE','LONGITUD']]
df = df.rename(columns={'LATITUDE': 'lat','LONGITUD': 'lon'})
print(df.columns)

# st.map(df)


view_state = pdk.ViewState(
                latitude=37.76,
                longitude=-122.4,
                zoom=11,
                pitch=0,
            )


print("view_state", view_state)



deck = pdk.Deck(
    # map_style=None,
    # map_style='light',
    map_style='road',
    # map_style='dark',
    # map_style='satellite',
    initial_view_state=view_state,
    layers=[
        # pdk.Layer(
        #    'HexagonLayer',
        #    data=df,
        #    get_position='[lon, lat]',
        #    radius=200,
        #    elevation_scale=4,
        #    elevation_range=[0, 1000],
        #    pickable=True,
        #    extruded=True,
        # ),
        pdk.Layer(
            'ScatterplotLayer',
            data=df,
            get_position='[lon, lat]',
            get_color='[255,0,0,160]',
            # get_radius=100,
            # radius_units="meters",
            # radiusMinPixels= 2,
            # radiusMaxPixels= 20
        ),
        # {
        #     'type': 'ScatterplotLayer',
        #     'data': df,
        #     'getColor': '[0,0,255]',
        #     'getRadius': 200
        # }
    ],
)

# print("deck", deck)

st.pydeck_chart(deck)

# time.sleep(10)
# print("\nTEST deck", deck)