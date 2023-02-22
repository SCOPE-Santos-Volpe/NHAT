BASECOORDS = [40.0, -90.0];

function makeMap() {
    var TILE_URL = "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png";
    var MB_ATTR = 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors';
    mymap = L.map('llmap').setView(BASECOORDS, 4);
    L.tileLayer(TILE_URL, {attribution: MB_ATTR}).addTo(mymap);
}

var layer = L.layerGroup();

function renderData(districtid) {
    $.getJSON("/district/" + districtid, function(obj) {
    //  $.getJSON("/fars_accident_2020/" + districtid, function(obj) {
        var markers = obj.data.map(function(arr) {
            //return L.marker([arr[0], arr[1]]);
            return L.circleMarker([arr[0], arr[1]], {radius: 2, color: 'red'}).bindPopup("Coordinates:<br>" + [arr[0], arr[1]]);
        });
        mymap.removeLayer(layer);
        layer = L.layerGroup(markers);
        mymap.addLayer(layer);
    });
}



// attempt to fly to bounds 
// centering a group of markers
//mymap.on("layeradd layerremove", function () {
  // Create new empty bounds
//  let bounds = new L.LatLngBounds();
  // Iterate the map's layers
  // // DO NOT UNCOMMENT SOMETHING IN HERE BREAKS AND MAKES THINGS SLOW
//  mymap.eachLayer(function (layer) {
    // Check if layer is a featuregroup
//   if (layer instanceof L.FeatureGroup) {
     // Extend bounds with group's bounds
//     bounds.extend(layer.getBounds());
//   }
//   console.log("hi");
//   });

  // Check if bounds are valid (could be empty)
//  if (bounds.isValid()) {
    // Valid, fit bounds
//    mymap.flyToBounds(bounds);
//  } else {
    // Invalid, fit world
//     mymap.fitWorld();
//  }
//});




$(function() {
    makeMap();
    renderData('0');
    $('#distsel').change(function() {
        var val = $('#distsel option:selected').val();
        renderData(val);
    });
})
