# Lilo's Leaflet example

Sorry for the messy code! Working on fixing it up

Where I got the code:
  
- First I used this guy's example to get the coordinates of the place you click on the map, and used it to learn how to create alerts and popups, and get the window's east west north and south longitudes and latitudes. 
  - https://discuss.streamlit.io/t/using-leaflet-instead-of-folium-in-streamlit-to-return-coordinates-on-map-click/4946
  - https://github.com/andfanilo/streamlit-light-leaflet
- Next I used leaflet.js documentation examples to learn how to add overlays and controls, and to plot points that look different ways.
  - https://leafletjs.com/examples/layers-control/
  - https://discuss.streamlit.io/t/using-leaflet-instead-of-folium-in-streamlit-to-return-coordinates-on-map-click/4946
  - https://github.com/andfanilo/streamlit-light-leaflet
- I also looked at this but didn't end up using it, just consulting it for syntax:
  - https://geospatial.streamlitapp.com/
  - https://github.com/giswqs/streamlit-geospatial

Leaflet has the benefit of being very interactive, but it is javascript and needs a way to receive data to plot from python.
- I figured out a way to read from csv files using "FileReader", it's in the code right now.
- Also this is one possible way which looks promising but I haven't implemented yet:
  - https://programminghistorian.org/en/lessons/mapping-with-python-leaflet


If plotly can also do the same things, I'll happily go with that instead (python yay!) but [Leaflet](https://leafletjs.com) has many great interactive map features. 


--------------------------------------------------------------------------


To run the code:

```
cd streamlit-light-leaflet

cat STARTUP.md
```

Copy the first block into one terminal to start npm

Copy the second block into a new terminal to start the python init file
