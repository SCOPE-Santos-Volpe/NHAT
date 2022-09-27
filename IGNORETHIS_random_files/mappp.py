import plotly.express as px
import pandas as pd

print("getting data...")
df = px.data.carshare()
print(df.head(10))
print(df.tail(10))

fig = px.scatter_mapbox(df,
                        lon = df['centroid_lon'],
                        lat = df['centroid_lat'],
                        zoom = 10, 
                        color = df['peak_hour'],
                        size = df['car_hours'],
                        width = 900,
                        height = 600,
                        title = 'Car Share Scatter Map'
                        )
fig.update_layout(mapbox_style = "open-street-map")
fig.update_layout(margin = {"r":0, "t":50, "l":0, "b":10})
fig.show()
print("plot completes")