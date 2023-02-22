// var L = require('leaflet');
// magnification with which the map will start
const zoom = 3;

// coordinates
const lat = 45.0;
const lng = -93.25;

const osmLink = '<a href="http://openstreetmap.org">OpenStreetMap</a>';
const cartoDB = '<a href="http://cartodb.com/attributions">CartoDB</a>';

const osmUrl = "http://tile.openstreetmap.org/{z}/{x}/{y}.png";
const osmAttrib = `&copy; ${osmLink} Contributors`;
const landUrl = "https://{s}.basemaps.cartocdn.com/rastertiles/dark_all/{z}/{x}/{y}.png";
const cartoAttrib = `&copy; ${osmLink} Contributors & ${cartoDB}`;

const osmMap = L.tileLayer(osmUrl, { attribution: osmAttrib });
const landMap = L.tileLayer(landUrl, { attribution: cartoAttrib });

// config map
let config = {
  layers: [osmMap],
  minZoom: 3,
  maxZoom: 18,
  preferCanvas: true, // helps to fix slowness by plotting points on a canvas rather than individual layers
  // fullscreenControl: true,
};


const pointsA = [
  [44.960020586193795,  -93.25083755493164, "point A1"],
  [44.95924616170657,   -93.251320352554325, "point A2"],
  [44.959511304688444,  -93.25270973682404, "point A3"],
  [44.96040500771883,   -93.252146472930908, "point A4"],
];

const pointsB = [
  [44.959314161892106,  -93.252055277824405, "point B1"],
  [44.95950144756943,   -93.25193726062775, "point B2"],
  [44.95966573260081,   -93.251829972267154, "point B3"],
  [44.9598333027065,    -93.251744141578678, "point B4"],
  [44.9599680154701,    -93.25164758205414, "point B5"],
  [44.96012572746442,   -93.251583209037784, "point B6"],
  [44.960276867580336,  -93.25143836975098, "point B7"],
  [44.96046414919644,   -93.251341810226444, "point B8"],
];

// calling map
const map = L.map("map", config).setView([lat, lng], zoom);

var baseLayers = {
  "OSM Mapnik": osmMap,
  CartoDB: landMap,
};

// Extended `LayerGroup` that makes it easy to do the same for all layers of its members
const pA = new L.FeatureGroup();
const pB = new L.FeatureGroup();
const fars_points = new L.FeatureGroup();
const mpo_boundaries = new L.FeatureGroup();
const county_boundaries = new L.FeatureGroup();
const state_boundaries = new L.FeatureGroup();
const census_boundaries = new L.FeatureGroup(); // TODO: implement
const roadHighlight_polylineLayer = new L.FeatureGroup(); // TODO: implement

// adding markers to the layer pointsA
for (let i = 0; i < pointsA.length; i++) {
  // var marker = L.marker([pointsA[i][0], pointsA[i][1]]).bindPopup(pointsA[i][2]);
  var marker = L.circleMarker([pointsA[i][0], pointsA[i][1]], {radius: 10, color: '#FF00FF'}).bindPopup(pointsA[i][2]);
  pA.addLayer(marker);
}


var FARS_renderer = L.canvas({ padding: 0.5 }); // helps to fix slowness by plotting points on a canvas rather than individual layers
d3.csv('https://raw.githubusercontent.com/Santos-Volpe-SCOPE/Santos-Volpe-SCOPE-Project/app-framework/FARS2020NationalCSV/accident.csv', function(data) {
  console.log("data.length", data.length);
  
  // for (var i = 0; i < 2000; i++) { 
  for (var i = 0; i < data.length; i++) {
    // console.log(data[i].LATITUDE, data[i].LONGITUD);

    var row = data[i];

    // if (row.STATENAME == "California") { // | row.STATENAME == "Texas"){
    if (row.LATITUDENAME != "Not Available" & row.LONGITUDNAME != "Not Available" & row.LATITUDENAME != "Not Reported" & row.LONGITUDNAME != "Not Reported" & row.LATITUDENAME != "Reported as Unknown" & row.LONGITUDNAME != "Reported as Unknown"){
      // // renderer option helps to fix slowness by plotting points on a canvas rather than individual layers
      var marker = L.circleMarker([row.LATITUDE, row.LONGITUD], {radius: 1, opacity: 0.9, color: '#0000ff', renderer: FARS_renderer}).bindPopup("Coordinates:<br/>" + [row.LATITUDENAME, row.LONGITUDNAME]); //.addTo(map);
      fars_points.addLayer(marker);
    }
    // }
  }
});


// adding markers to the layer pointsB
for (let i = 0; i < pointsB.length; i++) {
  marker = L.marker([pointsB[i][0], pointsB[i][1]]).bindPopup(pointsB[i][2]);
  pB.addLayer(marker);
}


// centering a group of markers
map.on("layeradd layerremove", function () {
  // Create new empty bounds
  let bounds = new L.LatLngBounds();
  // Iterate the map's layers
  // // DO NOT UNCOMMENT SOMETHING IN HERE BREAKS AND MAKES THINGS SLOW
  // map.eachLayer(function (layer) {
  //   // Check if layer is a featuregroup
    // if (layer instanceof L.FeatureGroup) {
    //   // Extend bounds with group's bounds
    //   bounds.extend(layer.getBounds());
    // }
    // console.log("hi");
  // });

  // Check if bounds are valid (could be empty)
  if (bounds.isValid()) {
    // Valid, fit bounds
    map.flyToBounds(bounds);
  } else {
    // Invalid, fit world
    // map.fitWorld();
  }
});


// ------------------------------------------------------------------------------------
// POLYLINE TO HIGHLIGHT ROADS

// define array of points to use for polyline
const points = [
  [45, -89],
  [42, -89],
  [42, -91],
  [42, -93],
  [43, -92],
  [44, -91],
  [45, -91],
];

// add polyline to map
var roadHighlight_polyline = L.polyline(points, {
  color: "black",
  opacity: 0.5,
  weight: 5,
}).bindPopup("polygon"); //.addTo(map);

roadHighlight_polylineLayer.addLayer(roadHighlight_polyline);


// ------------------------------------------------------------------------------------
// CREATE CUSTOM BUTTONS CLASS

L.Control.CustomButtons = L.Control.Layers.extend({
  onAdd: function () {
    this._initLayout();
    this._addMarker();
    this._removeMarker();
    this._update();
    return this._container;
  },
  _addMarker: function () {
    this.createButton("add", "add-button");
  },
  _removeMarker: function () {
    this.createButton("remove", "remove-button");
  },
  createButton: function (type, className) {
    const elements = this._container.getElementsByClassName(
      "leaflet-control-layers-list"
    );
    const button = L.DomUtil.create(
      "button",
      `btn-markers ${className}`,
      elements[0]
    );
    button.textContent = `${type} markers`;

    L.DomEvent.on(button, "click", function (e) {
      const checkbox = document.querySelectorAll(
        ".leaflet-control-layers-overlays input[type=checkbox]"
      );

      // Remove/add all layer from map when click on button
      [].slice.call(checkbox).map((el) => {
        el.checked = type === "add" ? false : true;
        el.click();
      });
    });
  },
});

// ------------------------------------------------------------------------------------
// CREATE CUSTOM TOGGLE BUTTON CLASS

L.Control.CustomToggle = L.Control.Layers.extend({
  onAdd: function () {
    this._initLayout();
    this._addMarker();
    this._removeMarker();
    this._update();
    return this._container;
  },
  _addMarker: function () {
    this.createButton("Toggle County vs. MPO Boundaries", "add-button");
  },
  _removeMarker: function () {
    // this.createButton("remove", "remove-button");
  },
  createButton: function (type, className) {
    const elements = this._container.getElementsByClassName(
      "leaflet-control-layers-list"
    );

    const button = L.DomUtil.create(
      "button",
      `btn-markers ${className}`,
      elements[0]
    );
    button.textContent = `${type}`;

    L.DomEvent.on(button, "click", function (e) {
      toggle_county_vs_mpo = !toggle_county_vs_mpo;
      console.log("toggle_county_vs_mpo changed to", toggle_county_vs_mpo);

      map.removeLayer(state_boundaries); // makes states transition to mpo/county

      if (toggle_county_vs_mpo) { // Shows counties instead of MPOs
        map.removeLayer(mpo_boundaries); // makes states transition to mpo/county
        map.addLayer(county_boundaries); // makes states transition to mpo/county
      } else { // Shows MPOs instead of counties
        map.removeLayer(county_boundaries); // makes states transition to mpo/county
        map.addLayer(mpo_boundaries); // makes states transition to mpo/county
      }  
    });
  },
});


// ------------------------------------------------------------------------------------

// // one marker example
// coord = [52.22983, 21.011728];
// L.marker(coord).addTo(map).bindPopup("Center Warsaw\n" + coord.join());

// this was a text box on the bottom left of the screen:
// const markerPlace = document.querySelector(".marker-position");

// obtaining coordinates after clicking on the map
map.on("click", function (e) {
  // const markerPlace = document.querySelector(".marker-position");
  // markerPlace.textContent = e.latlng;
  console.log("Clicked on", e.latlng);
});


// on drag end
map.on("dragend", setRentacle);

// second option, by dragging the map
map.on("dragstart", updateInfo);

// on zoom end
map.on("zoomend", setRentacle);

// update info about bounds when site loaded
document.addEventListener("DOMContentLoaded", function () {
  const bounds = map.getBounds();
  updateInfo(bounds._northEast, bounds._southWest);
});

// set rentacle function
function setRentacle() {
  const bounds = map.getBounds();

  // update info about bounds
  updateInfo(bounds._northEast, bounds._southWest);

  // // set rentacle
  // L.rectangle(bounds, {
  //   color: randomColor(),
  //   weight: 20,
  //   fillOpacity: 0.1,
  // }).addTo(map);

  // set map
  map.fitBounds(bounds);
}

// generate random color
function randomColor() {
  return `#${Math.floor(Math.random() * 16777215).toString(16)}`;
}

function updateInfo(north, south) {
  // console.log("moving the map", north, south);
  // markerPlace.textContent =
  var textContent = 
    south === undefined
      ? "We are moving the map..."
      : `SouthWest: ${north}, NorthEast: ${south}`;
    console.log(textContent);
}


// ------------------------------------------------------------------------------------
// HEATMAP EXAMPLE

var L = require('leaflet');

// Configure and create the heatmap.js layer. Check out the heatmap.js Leaflet plugin docs for additional configuration options.
let cfg = {
    "radius": 40,
    "useLocalExtrema": true,
    valueField: 'price'
};
let heatmapLayer = new HeatmapOverlay(cfg);

var sale = require('./federal_hill_sales.json');

// Determine min/max (from JSON data exposed as variable in sales.js) for the heatmap.js plugin
let min = Math.min(...sale.map(sale => sale.value))
let max = Math.max(...sale.map(sale => sale.value))

// Add data (from JSON data exposed as variable in sales.js) to the heatmap.js layer
heatmapLayer.setData({
    min: min,
    max: max,
    data: sale
});


// -----------------------------------------------------------------------------------------
// LOAD GEOJSON OF MPOS

function setMposToMap(geojson) {
  const feature = L.geoJSON(geojson, {
    style: function (feature) {
      return {
        color: "blue",
        weight: 1,
      };
    },
    onEachFeature: function (feature, layer) {
      // const coordinates = feature.geometry.coordinates.toString();
      // const coordinate_string = coordinates.match(/[^,]+,[^,]+/g);

      const mpo_name = feature.properties.MPO_NAME.toString();
      layer.bindPopup(
        "<span>MPO Name:<br>" + mpo_name + "</span>"
      );

      layer.on('mouseover', function () {
        this.setStyle({
          'fillColor': 'yellow'
        });
        this.openPopup();
      });
      
      layer.on('mouseout', function () {
        this.setStyle({
          'fillColor': 'blue'
        });
        this.closePopup(); 
      });

      layer.on('click', function (event) {
        map.fitBounds(this.getBounds());
      });
    },
  }); //.addTo(map);
  console.log("feature", feature);
  mpo_boundaries.addLayer(feature);
  // map.flyToBounds(feature.getBounds());
}

d3.json('https://raw.githubusercontent.com/Santos-Volpe-SCOPE/Santos-Volpe-SCOPE-Project/app-framework/hin_app/mpo_data/mpo_boundaries.geojson', function(data) {
  const geojson = data;
  setMposToMap(geojson);
  console.log("mpo boundaries loaded");
});


// -----------------------------------------------------------------------------------------
// LOAD GEOJSON OF COUNTIES

function setCountiesToMap(geojson) {
  const feature = L.geoJSON(geojson, {
    style: function (feature) {
      return {
        color: "green",
        weight: 1,
        opacity: 0.8,
        clickable: true
      };
    },
    onEachFeature: function (feature, layer) {
      // const coordinates = feature.geometry.coordinates.toString();
      // const coordinate_string = coordinates.match(/[^,]+,[^,]+/g);
      const county_name = feature.properties.NAME.toString();
      layer.bindPopup(
        "<span>County Name:<br>" + county_name + "</span>"
      );

      layer.on('mouseover', function () {
        this.setStyle({
          'fillColor': 'yellow'
        });
        this.openPopup();
      });
      
      layer.on('mouseout', function () {
        this.setStyle({
          'fillColor': 'green'
        });
        this.closePopup(); 
      });

      layer.on('click', function (event) {
        map.fitBounds(this.getBounds());
      });
    },
  }); //.addTo(map);
  console.log("feature", feature);
  county_boundaries.addLayer(feature);
  // map.flyToBounds(feature.getBounds());
}

d3.json('https://raw.githubusercontent.com/Santos-Volpe-SCOPE/Santos-Volpe-SCOPE-Project/app-framework/hin_app/county_data/county.geojson', function(data) {
  const geojson = data;
  setCountiesToMap(geojson);
  console.log("county boundaries loaded");
});


// -----------------------------------------------------------------------------------------
// LOAD GEOJSON OF STATES

var toggle_county_vs_mpo = false; // TODO: Later add logic using a toggle switch

function setStatesToMap(geojson) {
  const feature = L.geoJSON(geojson, {
    style: function (feature) {
      return {
        color: "red",
        weight: 1,
        opacity: 0.8,
        clickable: true
      };
    },
    onEachFeature: function (feature, layer) {
      const state_name = feature.properties.NAME.toString();
      layer.bindPopup(
        "<span>State Name:<br>" + state_name + "</span>"
      );

      layer.on('mouseover', function () {
        this.setStyle({
          'fillColor': '#0000ff'
        });
        this.openPopup();
      });
      
      layer.on('mouseout', function () {
        this.setStyle({
          'fillColor': '#ff0000'
        });
        this.closePopup(); 
      });

      layer.on('click', function (event) {
        map.fitBounds(this.getBounds());
        map.removeLayer(state_boundaries); // makes states transition to mpo/county

        if (toggle_county_vs_mpo) { // Shows counties instead of MPOs
          map.addLayer(county_boundaries); // makes states transition to mpo/county
        } else { // Shows MPOs instead of counties
          map.addLayer(mpo_boundaries); // makes states transition to mpo/county
        }
      });
    },
  }); 
  // console.log("feature", feature);
  state_boundaries.addLayer(feature);
  // map.flyToBounds(feature.getBounds());
}

state_boundaries.addTo(map); // makes states always show up on first load of the web app


d3.json('https://raw.githubusercontent.com/Santos-Volpe-SCOPE/Santos-Volpe-SCOPE-Project/app-framework/hin_app/state_data/states.geojson', function(data) {
  const geojson = data;
  setStatesToMap(geojson);
  console.log("state boundaries loaded");
});


// -----------------------------------------------------------------------------------------
// ADD OVERLAYS ONTO MAP ON THE CUSTOM BUTTONS CONTROL PANEL

// object with layers
const overlayMaps = {
  "Circle Example": pA,
  "Pin Example": pB,
  "FARS 2020 Crashes": fars_points,
  // "MPO Boundaries": mpo_boundaries,
  // "County Boundaries": county_boundaries,
  // "State Boundaries": state_boundaries,
  "Heatmap Example": heatmapLayer,
  "Polyline Example": roadHighlight_polylineLayer,
};

// Trying to bring fars to back / bring heatmap to front:
// fars_points.bringToBack();


// -------------------------------------------------------------------------------------------
// EXCLUSIVE LAYER PLUGIN (ALLOWS RADIO BOXES FOR LAYERS, NOT JUST CHECKBOXES)

// A layer control which provides for layer groupings.
// Author: Ishmael Smyrnow
L.Control.GroupedLayers = L.Control.extend({

  options: {
    collapsed: true,
    position: 'topright',
    autoZIndex: true,
    exclusiveGroups: [],
    groupCheckboxes: false
  },

  initialize: function (baseLayers, groupedOverlays, options) {
    var i, j;
    L.Util.setOptions(this, options);

    this._layers = [];
    this._lastZIndex = 0;
    this._handlingClick = false;
    this._groupList = [];
    this._domGroups = [];

    for (i in baseLayers) {
      this._addLayer(baseLayers[i], i);
    }

    for (i in groupedOverlays) {
      for (j in groupedOverlays[i]) {
        this._addLayer(groupedOverlays[i][j], j, i, true);
      }
    }
  },

  onAdd: function (map) {
    this._initLayout();
    this._update();

    map
        .on('layeradd', this._onLayerChange, this)
        .on('layerremove', this._onLayerChange, this);

    return this._container;
  },

  onRemove: function (map) {
    map
        .off('layeradd', this._onLayerChange, this)
        .off('layerremove', this._onLayerChange, this);
  },

  addBaseLayer: function (layer, name) {
    this._addLayer(layer, name);
    this._update();
    return this;
  },

  addOverlay: function (layer, name, group) {
    this._addLayer(layer, name, group, true);
    this._update();
    return this;
  },

  removeLayer: function (layer) {
    var id = L.Util.stamp(layer);
    var _layer = this._getLayer(id);
    if (_layer) {
      delete this._layers[this._layers.indexOf(_layer)];
    }
    this._update();
    return this;
  },

  _getLayer: function (id) {
    for (var i = 0; i < this._layers.length; i++) {
      if (this._layers[i] && L.stamp(this._layers[i].layer) === id) {
        return this._layers[i];
      }
    }
  },

  _initLayout: function () {
    var className = 'leaflet-control-layers',
      container = this._container = L.DomUtil.create('div', className);

    // Makes this work on IE10 Touch devices by stopping it from firing a mouseout event when the touch is released
    container.setAttribute('aria-haspopup', true);

    if (L.Browser.touch) {
      L.DomEvent.on(container, 'click', L.DomEvent.stopPropagation);
    } else {
      L.DomEvent.disableClickPropagation(container);
      L.DomEvent.on(container, 'wheel', L.DomEvent.stopPropagation);
    }

    var form = this._form = L.DomUtil.create('form', className + '-list');

    if (this.options.collapsed) {
      if (!L.Browser.android) {
        L.DomEvent
            .on(container, 'mouseover', this._expand, this)
            .on(container, 'mouseout', this._collapse, this);
      }
      var link = this._layersLink = L.DomUtil.create('a', className + '-toggle', container);
      link.href = '#';
      link.title = 'Layers';

      if (L.Browser.touch) {
        L.DomEvent
            .on(link, 'click', L.DomEvent.stop)
            .on(link, 'click', this._expand, this);
      } else {
        L.DomEvent.on(link, 'focus', this._expand, this);
      }

      this._map.on('click', this._collapse, this);
      // TODO keyboard accessibility
    } else {
      this._expand();
    }

    this._baseLayersList = L.DomUtil.create('div', className + '-base', form);
    this._separator = L.DomUtil.create('div', className + '-separator', form);
    this._overlaysList = L.DomUtil.create('div', className + '-overlays', form);

    container.appendChild(form);
  },

  _addLayer: function (layer, name, group, overlay) {
    var id = L.Util.stamp(layer);

    var _layer = {
      layer: layer,
      name: name,
      overlay: overlay
    };
    this._layers.push(_layer);

    group = group || '';
    var groupId = this._indexOf(this._groupList, group);

    if (groupId === -1) {
      groupId = this._groupList.push(group) - 1;
    }

    var exclusive = (this._indexOf(this.options.exclusiveGroups, group) !== -1);

    _layer.group = {
      name: group,
      id: groupId,
      exclusive: exclusive
    };

    if (this.options.autoZIndex && layer.setZIndex) {
      this._lastZIndex++;
      layer.setZIndex(this._lastZIndex);
    }
  },

  _update: function () {
    if (!this._container) {
      return;
    }

    this._baseLayersList.innerHTML = '';
    this._overlaysList.innerHTML = '';
    this._domGroups.length = 0;

    var baseLayersPresent = false,
      overlaysPresent = false,
      i, obj;

    for (var i = 0; i < this._layers.length; i++) {
      obj = this._layers[i];
      this._addItem(obj);
      overlaysPresent = overlaysPresent || obj.overlay;
      baseLayersPresent = baseLayersPresent || !obj.overlay;
    }

    this._separator.style.display = overlaysPresent && baseLayersPresent ? '' : 'none';
  },

  _onLayerChange: function (e) {

    var obj = this._getLayer(L.Util.stamp(e.layer)),
      type;

    if (!obj) {
      return;
    }

    if (!this._handlingClick) {
      this._update();
    }

    if (obj.overlay) {
      type = e.type === 'layeradd' ? 'overlayadd' : 'overlayremove';

      // LILO : tried adding something to zoom out to fit bounds of the selected layer
      // console.log("obj.layer", obj.layer);
      // map.fitBounds(obj.layer.getBounds());

    } else {
      type = e.type === 'layeradd' ? 'baselayerchange' : null;
    }

    if (type) {
      this._map.fire(type, obj);
    }
  },

  // IE7 bugs out if you create a radio dynamically, so you have to do it this hacky way (see http://bit.ly/PqYLBe)
  _createRadioElement: function (name, checked) {
    var radioHtml = '<input type="radio" class="leaflet-control-layers-selector" name="' + name + '"';
    if (checked) {
      radioHtml += ' checked="checked"';
    }
    radioHtml += '/>';

    var radioFragment = document.createElement('div');
    radioFragment.innerHTML = radioHtml;

    return radioFragment.firstChild;
  },

  _addItem: function (obj) {
    var label = document.createElement('label'),
      input,
      checked = this._map.hasLayer(obj.layer),
      container,
      groupRadioName;

    if (obj.overlay) {
      if (obj.group.exclusive) {
        groupRadioName = 'leaflet-exclusive-group-layer-' + obj.group.id;
        input = this._createRadioElement(groupRadioName, checked);
      } else {
        input = document.createElement('input');
        input.type = 'checkbox';
        input.className = 'leaflet-control-layers-selector';
        input.defaultChecked = checked;
      }
    } else {
      input = this._createRadioElement('leaflet-base-layers', checked);
    }

    input.layerId = L.Util.stamp(obj.layer);
    input.groupID = obj.group.id;
    L.DomEvent.on(input, 'click', this._onInputClick, this);

    var name = document.createElement('span');
    name.innerHTML = ' ' + obj.name;

    label.appendChild(input);
    label.appendChild(name);

    if (obj.overlay) {
      container = this._overlaysList;

      var groupContainer = this._domGroups[obj.group.id];

      // Create the group container if it doesn't exist
      if (!groupContainer) {
        groupContainer = document.createElement('div');
        groupContainer.className = 'leaflet-control-layers-group';
        groupContainer.id = 'leaflet-control-layers-group-' + obj.group.id;

        var groupLabel = document.createElement('label');
        groupLabel.className = 'leaflet-control-layers-group-label';

        if (obj.group.name !== '' && !obj.group.exclusive) {
          // ------ add a group checkbox with an _onInputClickGroup function
          if (this.options.groupCheckboxes) {
            var groupInput = document.createElement('input');
            groupInput.type = 'checkbox';
            groupInput.className = 'leaflet-control-layers-group-selector';
            groupInput.groupID = obj.group.id;
            groupInput.legend = this;
            L.DomEvent.on(groupInput, 'click', this._onGroupInputClick, groupInput);
            groupLabel.appendChild(groupInput);
          }
        }

        var groupName = document.createElement('span');
        groupName.className = 'leaflet-control-layers-group-name';
        groupName.innerHTML = obj.group.name;
        groupLabel.appendChild(groupName);

        groupContainer.appendChild(groupLabel);
        container.appendChild(groupContainer);

        this._domGroups[obj.group.id] = groupContainer;
      }

      container = groupContainer;
    } else {
      container = this._baseLayersList;
    }

    container.appendChild(label);

    return label;
  },

  _onGroupInputClick: function () {
    var i, input, obj;

    var this_legend = this.legend;
    this_legend._handlingClick = true;

    var inputs = this_legend._form.getElementsByTagName('input');
    var inputsLen = inputs.length;

    for (i = 0; i < inputsLen; i++) {
      input = inputs[i];
      if (input.groupID === this.groupID && input.className === 'leaflet-control-layers-selector') {
        input.checked = this.checked;
        obj = this_legend._getLayer(input.layerId);
        if (input.checked && !this_legend._map.hasLayer(obj.layer)) {
          this_legend._map.addLayer(obj.layer);
        } else if (!input.checked && this_legend._map.hasLayer(obj.layer)) {
          this_legend._map.removeLayer(obj.layer);
        }
      }
    }

    this_legend._handlingClick = false;
  },

  _onInputClick: function () {
    var i, input, obj,
      inputs = this._form.getElementsByTagName('input'),
      inputsLen = inputs.length;

    this._handlingClick = true;

    for (i = 0; i < inputsLen; i++) {
      input = inputs[i];
      if (input.className === 'leaflet-control-layers-selector') {
        obj = this._getLayer(input.layerId);

        if (input.checked && !this._map.hasLayer(obj.layer)) {
          this._map.addLayer(obj.layer);
        } else if (!input.checked && this._map.hasLayer(obj.layer)) {
          this._map.removeLayer(obj.layer);
        }
      }
    }

    this._handlingClick = false;
  },

  _expand: function () {
    L.DomUtil.addClass(this._container, 'leaflet-control-layers-expanded');
    // permits to have a scrollbar if overlays heighter than the map.
    var acceptableHeight = this._map._size.y - (this._container.offsetTop * 4);
    if (acceptableHeight < this._form.clientHeight) {
      L.DomUtil.addClass(this._form, 'leaflet-control-layers-scrollbar');
      this._form.style.height = acceptableHeight + 'px';
    }
  },

  _collapse: function () {
    this._container.className = this._container.className.replace(' leaflet-control-layers-expanded', '');
  },

  _indexOf: function (arr, obj) {
    for (var i = 0, j = arr.length; i < j; i++) {
      if (arr[i] === obj) {
        return i;
      }
    }
    return -1;
  }
});

L.control.groupedLayers = function (baseLayers, groupedOverlays, options) {
  return new L.Control.GroupedLayers(baseLayers, groupedOverlays, options);
};


// -----------------------------------------------------------------------------------------
// MAKE MAP CONTROLS PANEL INCLUDING CUSTOM CONTROLS

var groupedOverlays = {
  "Geographic Boundaries":{
      "State Boundaries":state_boundaries,
      "County Boundaries":county_boundaries,
      "MPO Boundaries":mpo_boundaries,
  },
  "Examples":{
    "Circle Example": pA,
    "Pin Example": pB,
    "FARS 2020 Crashes": fars_points,
    "Heatmap Example": heatmapLayer,
    "Polyline Example": roadHighlight_polylineLayer,
  }
}
var options = {
  // Make the overlay group is exclusive (use radio inputs)
  exclusiveGroups: ["Geographic Boundaries"],
  // Show a checkbox next to non-exclusive group labels for toggling all:
  groupCheckboxes: true,
  collapsed: false,
};
// Use grouped layer plugin instead of "L.control.layers" to create radio boxes instead of checkboxes for overlays
var layerControl = L.control.groupedLayers(baseLayers, groupedOverlays, options);
map.addControl(layerControl); 


// Makes separate controls box with a custom button to toggle between county or MPO
// var custom_toggle_control = new L.Control.CustomToggle(null, null, { collapsed: false }).addTo(map);

// Makes base layer default control box
// L.control.layers(baseLayers, null, {collapsed:false}).addTo(map); // make controls not collapse, stay expanded

// Makes base layer and overlay controls inside default box instead of in new separate box
// var layerControl = L.control.layers(baseLayers, overlayMaps).addTo(map);

// Makes separate overlay controls box with checkboxes
// var custom_buttons_control = new L.Control.CustomButtons(null, overlayMaps, { collapsed: false }).addTo(map);


// -----------------------------------------------------------------------------------------
// TRIED TO LOAD GEOJSON FASTER. NOT REALLY WORKING

// var myStyle = {
//   "color": "#ff7800",
//   "weight": 5,
//   "opacity": 0.65
// };
// var geojsonMarkerOptions = {
//   radius: 8,
//   fillColor: "#ff7800",
//   color: "#000",
//   weight: 1,
//   opacity: 1,
//   fillOpacity: 0.8
// };

// d3.json('https://raw.githubusercontent.com/Santos-Volpe-SCOPE/Santos-Volpe-SCOPE-Project/app-framework/hin_app/mpo_data/mpo_boundaries.geojson', function(data) {
//   const geojsonFeature = data;
//   // setGeojsonToMap(geojson);
//   var myLayer = L.geoJSON().addTo(map);
//   myLayer.addData(geojsonFeature, {
//       style: myStyle,
//       onEachFeature: onEachFeature
//     });
//   console.log("mpo boundaries loaded");

//   function onEachFeature(feature, layer) {
//     layer.bindPopup(feature.properties.MPO_NAME);
//   }
// });


// ----------------------------------------------------------------------------------------------------
// sidebar

const menuItems = document.querySelectorAll(".menu-item");
const sidebar = document.querySelector(".sidebar");
const buttonClose = document.querySelector(".close-button");

menuItems.forEach((item) => {
  item.addEventListener("click", (e) => {
    const target = e.target;

    if (
      target.classList.contains("active-item") ||
      !document.querySelector(".active-sidebar")
    ) {
      document.body.classList.toggle("active-sidebar");
    }

    // show content
    showContent(target.dataset.item);
    // add active class to menu item
    addRemoveActiveItem(target, "active-item");
  });
});

// close sidebar when click on close button
buttonClose.addEventListener("click", () => {
  closeSidebar();
});

// remove active class from menu item and content
function addRemoveActiveItem(target, className) {
  const element = document.querySelector(`.${className}`);
  target.classList.add(className);
  if (!element) return;
  element.classList.remove(className);
}

// show specific content
function showContent(dataContent) {
  const idItem = document.querySelector(`#${dataContent}`);
  addRemoveActiveItem(idItem, "active-content");
}

// --------------------------------------------------
// close when click esc
document.addEventListener("keydown", function (event) {
  if (event.key === "Escape") {
    closeSidebar();
  }
});

// close sidebar when click outside
document.addEventListener("click", (e) => {
  if (!e.target.closest(".sidebar")) {
    closeSidebar();
  }
});

// --------------------------------------------------
// close sidebar

function closeSidebar() {
  document.body.classList.remove("active-sidebar");
  const element = document.querySelector(".active-item");
  const activeContent = document.querySelector(".active-content");
  if (!element) return;
  element.classList.remove("active-item");
  activeContent.classList.remove("active-content");
}


// ----------------------------------------------------------------------------------------------------
// SHAPEFILE UPLOAD AND DRAW MENUS

// // --------------------------------------------------
// // Nofiflix options

// Notiflix.Notify.init({
//   width: "280px",
//   position: "right-bottom",
//   distance: "10px",
// });

// // --------------------------------------------------
// // add buttons to map

// const customControl = L.Control.extend({
//   // button position
//   options: {
//     position: "topright",
//   },

//   // method
//   onAdd: function () {
//     const array = [
//       {
//         title: "export features geojson",
//         html: "<svg class='icon-geojson'><use xlink:href='#icon-export'></use></svg>",
//         className: "export link-button leaflet-bar",
//       },
//       {
//         title: "save geojson",
//         html: "<svg class='icon-geojson'><use xlink:href='#icon-add'></use></svg>",
//         className: "save link-button leaflet-bar",
//       },
//       {
//         title: "remove geojson",
//         html: "<svg class='icon-geojson'><use xlink:href='#icon-remove'></use></svg>",
//         className: "remove link-button leaflet-bar",
//       },
//       {
//         title: "load gejson from file",
//         html: "<input type='file' id='geojson' class='geojson' accept='text/plain, text/json, .geojson' onchange='openFile(event)' /><label for='geojson'><svg class='icon-geojson'><use xlink:href='#icon-import'></use></svg></label>",
//         className: "load link-button leaflet-bar",
//       },
//     ];

//     const container = L.DomUtil.create(
//       "div",
//       "leaflet-control leaflet-action-button"
//     );

//     array.forEach((item) => {
//       const button = L.DomUtil.create("a");
//       button.href = "#";
//       button.setAttribute("role", "button");

//       button.title = item.title;
//       button.innerHTML = item.html;
//       button.className += item.className;

//       // add buttons to container;
//       container.appendChild(button);
//     });

//     return container;
//   },
// });
// map.addControl(new customControl());

// // Drow polygon, circle, rectangle, polyline
// // --------------------------------------------------

// let drawnItems = L.featureGroup().addTo(map);

// map.addControl(
//   new L.Control.Draw({
//     edit: {
//       featureGroup: drawnItems,
//       poly: {
//         allowIntersection: false,
//       },
//     },
//     draw: {
//       polygon: {
//         allowIntersection: false,
//         showArea: true,
//       },
//     },
//   })
// );

// map.on(L.Draw.Event.CREATED, function (event) {
//   let layer = event.layer;
//   let feature = (layer.feature = layer.feature || {});
//   let type = event.layerType;

//   feature.type = feature.type || "Feature";
//   let props = (feature.properties = feature.properties || {});

//   props.type = type;

//   if (type === "circle") {
//     props.radius = layer.getRadius();
//   }

//   drawnItems.addLayer(layer);
// });

// // --------------------------------------------------
// // save geojson to file

// const exportJSON = document.querySelector(".export");

// exportJSON.addEventListener("click", () => {
//   // Extract GeoJson from featureGroup
//   const data = drawnItems.toGeoJSON();

//   if (data.features.length === 0) {
//     Notiflix.Notify.failure("You must have some data to save a geojson file");
//     return;
//   } else {
//     Notiflix.Notify.info("You can save the data to a geojson");
//   }

//   // Stringify the GeoJson
//   const convertedData =
//     "text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(data));

//   exportJSON.setAttribute("href", "data:" + convertedData);
//   exportJSON.setAttribute("download", "data.geojson");
// });

// // --------------------------------------------------
// // save geojson to localstorage
// const saveJSON = document.querySelector(".save");

// saveJSON.addEventListener("click", (e) => {
//   e.preventDefault();

//   const data = drawnItems.toGeoJSON();

//   if (data.features.length === 0) {
//     Notiflix.Notify.failure("You must have some data to save it");
//     return;
//   } else {
//     Notiflix.Notify.success("The data has been saved to localstorage");
//   }

//   localStorage.setItem("geojson", JSON.stringify(data));
// });

// // --------------------------------------------------
// // remove gojson from localstorage

// const removeJSON = document.querySelector(".remove");

// removeJSON.addEventListener("click", (e) => {
//   e.preventDefault();
//   localStorage.removeItem("geojson");

//   Notiflix.Notify.info("All layers have been deleted");

//   drawnItems.eachLayer(function (layer) {
//     drawnItems.removeLayer(layer);
//   });
// });

// // --------------------------------------------------
// // load geojson from localstorage

// const geojsonFromLocalStorage = JSON.parse(localStorage.getItem("geojson"));

// function setGeojsonToMap(geojson) {
//   const feature = L.geoJSON(geojson, {
//     style: function (feature) {
//       return {
//         color: "red",
//         weight: 1,
//       };
//     },
//     pointToLayer: (feature, latlng) => {
//       if (feature.properties.type === "circle") {
//         return new L.circle(latlng, {
//           radius: feature.properties.radius,
//         });
//       } else if (feature.properties.type === "circlemarker") {
//         return new L.circleMarker(latlng, {
//           radius: 10,
//         });
//       } else {
//         return new L.Marker(latlng);
//       }
//     },
//     onEachFeature: function (feature, layer) {
//       drawnItems.addLayer(layer);
//       const coordinates = feature.geometry.coordinates.toString();
//       const result = coordinates.match(/[^,]+,[^,]+/g);

//       layer.bindPopup(
//         "<span>Coordinates:<br>" + result.join("<br>") + "</span>"
//       );
//     },
//   }).addTo(map);

//   map.flyToBounds(feature.getBounds());
// }

// if (geojsonFromLocalStorage) {
//   setGeojsonToMap(geojsonFromLocalStorage);
// }

// // --------------------------------------------------
// // get geojson from file

// function openFile(event) {
//   const input = event.target;

//   const reader = new FileReader();
//   reader.onload = function () {
//     const result = reader.result;
//     const geojson = JSON.parse(result);

//     Notiflix.Notify.info("The data has been loaded from the file");

//     setGeojsonToMap(geojson);
//   };
//   reader.readAsText(input.files[0]);
// }
