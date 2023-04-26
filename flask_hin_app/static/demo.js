// import grouped_layers

var map;

function makeMap() {
  // Make Map
    // magnification and coordinates with which the map will start
    const zoom = 4;
    const lat = 35;
    const lng = -108;

    const osmLink = '<a href="http://openstreetmap.org">OpenStreetMap</a>';
    const cartoDB = '<a href="http://cartodb.com/attributions">CartoDB</a>';
    const osmUrl = "http://tile.openstreetmap.org/{z}/{x}/{y}.png";
    const osmAttrib = `&copy; ${osmLink} Contributors`;
    const landUrl = "https://{s}.basemaps.cartocdn.com/rastertiles/dark_all/{z}/{x}/{y}.png";
    const cartoAttrib = `&copy; ${osmLink} Contributors & ${cartoDB}`;

    const osmMap = L.tileLayer(osmUrl, { attribution: osmAttrib });
    // const landMap = L.tileLayer(landUrl, { attribution: cartoAttrib });

    // config map
    let config = {
      layers: [osmMap],
      minZoom: 3,
      maxZoom: 18,
      zoomControl: false,
      preferCanvas: true, // helps to fix slowness by plotting points on a canvas rather than individual layers
      // fullscreenControl: true,
    };

    // calling map
    map = L.map("llmap", config).setView([lat, lng], zoom);

    L.control.zoom({ position: "topright" }).addTo(map);

    var baseLayers = {
      "OSM": osmMap,
      // CartoDB: landMap,
    };

  // Make Layers
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
    
    // Extended `LayerGroup` that makes it easy to do the same for all layers of its members
    const pA = new L.FeatureGroup();
    const pB = new L.FeatureGroup();
    const crash_points = new L.FeatureGroup();
    const selection_boundaries = new L.FeatureGroup(); // TODO: implement
    const mpo_boundaries = new L.FeatureGroup();
    const county_boundaries = new L.FeatureGroup();
    const state_boundaries = new L.FeatureGroup();
    const census_boundaries = new L.FeatureGroup(); // TODO: implement
    const roadHighlight_polylineLayer = new L.FeatureGroup(); // TODO: implement

    // adding markers to the layer pointsA
    for (let i = 0; i < pointsA.length; i++) {
        var marker = L.circleMarker([pointsA[i][0], pointsA[i][1]], {radius: 10, color: '#FF00FF'}).bindPopup(pointsA[i][2]);
        pA.addLayer(marker);
    }
    
    // adding markers to the layer pointsB
    for (let i = 0; i < pointsB.length; i++) {
        marker = L.marker([pointsB[i][0], pointsB[i][1]]).bindPopup(pointsB[i][2]);
        pB.addLayer(marker);
    }

    var SDS_renderer = L.canvas({ padding: 0.5 }); // helps to fix slowness by plotting points on a canvas rather than individual layers

    var fars_layer;
    var sds_layer;


    // ------------------------------------------------------------------------------------
    // HEATMAP EXAMPLE

    // Configure and create the heatmap.js layer. Check out the heatmap.js Leaflet plugin docs for additional configuration options.
    let cfg = {
      "radius": 40,
      "useLocalExtrema": true,
      valueField: 'price'
    };

    let heatmapLayer = new HeatmapOverlay(cfg);

    
    d3.json('https://raw.githubusercontent.com/SCOPE-Santos-Volpe/SCOPE-Santos-Volpe-Project/app-framework/hin_app/federal_hill_sales.json', function(data) { 
    // $.getJSON('../federal_hill_sales.json', function(data){

      // Add data (from JSON data exposed as variable in sales.js) to the heatmap.js layer
      heatmapLayer.setData({
        data: data
      });
    });

    // -----------------------------------------------------------------------------------------
    // LOAD GEOJSON OF MPOS

    const map_state_codes_to_nums = { "AL":1, "AK":2, "AZ":4, "AR":5, "CA": 6, "CO":8, "CT":9, "DE":10, 
                                      "DC":11, "FL":12, "GA":13, "HI":15, "ID":16, "IL":17, "IN":18, 
                                      "IA":19, "KS":20, "KY":21, "LA":22, "ME":23, "MD":24, "MA":25,
                                      "MI":26, "MN":27, "MS":28, "MO":29, "MT":30, "NE":31, "NV":32,
                                      "NH":33, "NJ":34, "NM":35, "NY":36, "NC":37, "ND":38, "OH":39, 
                                      "OK":40, "OR":41, "PA":42, "PR":72, "RI":44, "SC":45, "SD":46, 
                                      "TN":47, "TX":48, "UT":49, "VT":50, "VA":51, "VI":78, "WA":53,
                                      "WV":54, "WI":55, "WY":56 };

    function setMposToMap(geojson, clicked_state, selectedLayer) {
      var geojson_mpo_boundaries_layer = L.geoJSON(geojson, {
        style: function (feature) {
          var state_of_mpo = feature.properties.STATE_ID;
          // console.log("state_of_mpo", state_of_mpo);
          if (clicked_state == "NONE") {
            return {
              color: "red",
              weight: 1,
              opacity: 0.5,
              clickable: true
            };
          } else {
            if (state_of_mpo == clicked_state) {
              return {
                color: "red",
                weight: 1,
                opacity: 0.5,
                clickable: true
              };
            } else {
              return {
                color: "#555555",
                fillColor: "#555555",
                weight: 1,
                // opacity: 0.5,
                opacity: 0.0,
                fillOpacity: 0.0,
                // clickable: true
                clickable: false
              };
            }
          }
        },
        onEachFeature: function (feature, layer) {
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
            var state_of_mpo = feature.properties.STATE_ID;
            if (clicked_state == "NONE") {
              this.setStyle({
                'fillColor': 'red'
              });
            } else {
              if (state_of_mpo == clicked_state) {
                this.setStyle({
                  'fillColor': 'red'
                });
              } else {
                this.setStyle({
                  'fillColor': '#555555'
                });
              }
            }
            this.closePopup(); 
          });

          layer.on('click', function (event) {
            var state_of_mpo = feature.properties.STATE_ID;
            console.log("state_of_mpo", state_of_mpo);
            console.log("clicked feature", feature);

            map.fitBounds(this.getBounds());
            map.removeLayer(mpo_boundaries); // makes states transition to mpo/county

            // // if (map_state_codes_to_nums[state_of_mpo] != clicked_state) {
            // // TODO: what to do here for map navigation. For now do exact same as if state is highlighted
            var mpo_name = this.feature.properties.MPO_NAME;
            var mpo_id = this.feature.properties.MPO_ID;
            var mpo_not_county_bool = true;

            //show in the tab what county the users clicked
            document.querySelector('.after-state').style.display = 'none';
            document.querySelector('.back-button').style.display = 'none';

            document.querySelector('.region-click').style.display = 'block';
            document.querySelector('.after-region').style.display = 'block';
            var x = document.querySelectorAll('.button-group button');
            x[0].style.display = 'inline-block';
            x[1].style.display = 'inline-block';

            region.innerText = mpo_name ? `You clicked mpo: ${mpo_name}` : `You haven't selected any mpo`;
            afterregion.innerText = "You chose a region! Go to HIN tab to start generating HIN for your region.";

            // Get the geojson for the selected MPO
            $.getJSON("/get_mpo_boundaries_by_state_id_and_mpo_name/"+clicked_state+mpo_name, function(obj) {
              const mpogeojson = obj;
              setSelectionToMap(mpo_name, mpo_id, mpo_not_county_bool, mpogeojson, selectedLayer, clicked_state);
              console.log("mpo boundaries for state", clicked_state, "loaded");
            });

            map.addLayer(selection_boundaries); // makes states transition to mpo/county
            map.removeControl(layerControl); 
          });
        },
      }); 
      mpo_boundaries.addLayer(geojson_mpo_boundaries_layer);
      return geojson_mpo_boundaries_layer;
    }

    // -----------------------------------------------------------------------------------------
    // LOAD GEOJSON OF COUNTIES

    function setCountiesToMap(geojson, clicked_state, selectedLayer) {
      var geojson_county_boundaries_layer = L.geoJSON(geojson, {
        style: function (feature) {
          var state_of_county = feature.properties.STATE_ID;
          if (clicked_state == "NONE") {
            return {
              color: "red",
              weight: 1,
              opacity: 0.5,
              clickable: true
            };
          } else {
            if (state_of_county == clicked_state) {
              return {
                color: "red",
                weight: 1,
                opacity: 0.5,
                clickable: true
              };
            } else {
              return {
                color: "#555555",
                weight: 1,
                opacity: 0.5,
                clickable: true
              };
            }
          }
        },
        onEachFeature: function (feature, layer) {
          // const coordinates = feature.geometry.coordinates.toString();
          // const coordinate_string = coordinates.match(/[^,]+,[^,]+/g);
          const county_name = feature.properties.COUNTY_NAME.toString();
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
            if (clicked_state == "NONE") {
              this.setStyle({
                'fillColor': 'red'
              });
            } else {
              if (feature.properties.STATE_ID == clicked_state) {
                this.setStyle({
                  'fillColor': 'red'
                });
              } else {
                this.setStyle({
                  'fillColor': '#555555'
                });
              }
            }
            this.closePopup(); 
          });

          layer.on('click', function (event) {
            var state_of_county = feature.properties.STATE_ID;
            console.log("state_of_county", state_of_county);
            console.log("clicked feature", feature);

            console.log("layer", layer);

            map.fitBounds(this.getBounds());
            map.removeLayer(county_boundaries); // makes states transition to mpo/county

            // if (state_of_county != clicked_state) {
            // // TODO: what to do here for map navigation. For now do exact same as if state is highlighted
            var county_name = this.feature.properties.COUNTY_NAME;
            var county_id = this.feature.properties.COUNTY_ID;
            var mpo_not_county_bool = false;

            //show in the tab what county the users clicked
            document.querySelector('.after-state').style.display = 'none';
            document.querySelector('.back-button').style.display = 'none';

            document.querySelector('.region-click').style.display = 'block';
            document.querySelector('.after-region').style.display = 'block';
            var x = document.querySelectorAll('.button-group button');
            x[0].style.display = 'inline-block';
            x[1].style.display = 'inline-block';

            region.innerText = county_name ? `You clicked county: ${county_name}` : `You haven't selected any county`;
            afterregion.innerText = "You chose a region! Click the region one more time to confirm that this is the region you want to create HIN.";

            // TODO: (JACKIE) something wierd here, not showing just one county boundary
            // Get the geojson for the selected MPO/county
            $.getJSON("/get_county_boundaries_by_state_id_and_county_name/"+clicked_state+county_name, function(obj) {
              const county_geojson = obj;
              setSelectionToMap(county_name, county_id, mpo_not_county_bool, county_geojson, selectedLayer, clicked_state);
              console.log("county boundaries for state", county_name, "loaded");
            });
            
            map.addLayer(selection_boundaries); // makes states transition to mpo/county
            map.removeControl(layerControl); 
          });

          
        },

      });

      // CODE WHEN BACK BUTTON IS CLICKED
      function backButtonStateClicked() {
        const backbtn = document.querySelector('#back');        
        backbtn.addEventListener("click", () => {
          map.setView([35, -108], 4);
          map.removeLayer(county_boundaries);
          map.removeLayer(mpo_boundaries);
          map.addLayer(state_boundaries);
          map.removeControl(layerControl); 
          county_boundaries.removeLayer(geojson_county_boundaries_layer);

          document.querySelector('.state-click').style.display = 'none'; 
          document.querySelector('.back-button').style.display = 'none';
          document.querySelector('.after-state').style.display = 'none';
        });
      }

      backButtonStateClicked();


      county_boundaries.addLayer(geojson_county_boundaries_layer);
      return geojson_county_boundaries_layer;
    }


    // -----------------------------------------------------------------------------------------
    // LOAD LAYER HIGHLIGHTING THE SELECTED AREA

    function setSelectionToMap(selected_feature_name, selected_feature_id, mpo_not_county_bool, geojson, thisLayer, clicked_state) {
      console.log("checking the id is right", selected_feature_id);

      var geojson_selection_boundaries_layer = L.geoJSON(geojson, {
        style: function (feature) {
          if (mpo_not_county_bool) {
            var bool_selected = feature.properties.MPO_NAME == selected_feature_name;
          } else {
            var bool_selected = feature.properties.COUNTY_NAME == selected_feature_name;
          }
          if (!bool_selected) {
            return {
              color: "red",
              //fillColor : "#555555",
              weight: 5,
              opacity: 1.0,
              clickable: true
            };
          } else {
            return {
              color: "#555555",
              opacity: 1,
              fillOpacity: 0.0,
              // fillOpacity: 0.0L,
              clickable: true
            };
          }
        },
        // onEachFeature: function (feature, layer) {
        //   // console.log(selected_feature_name, feature.properties.GEOID);
        //   layer.on('mouseover', function () {
        //     this.setStyle({
        //       'fillColor': 'yellow',
        //     });
        //     this.openPopup();
        //   });
        
        //   layer.on('mouseout', function () {
        //     this.setStyle({
        //       'fillColor': '#555555',
        //     });
        //     this.closePopup(); 
        //   });

        //   layer.on('click', function (event) {
        //     map.addControl(startLayer);
        //     map.fitBounds(this.getBounds());

        //     this.setStyle({
        //       'color': '#555555',
        //       'fillOpacity': 0.0,
        //     });

        //     document.querySelector('.back-button2').style.display = 'none';
        //     document.querySelector('.after-region').style.display = 'none';
        //     // document.querySelector('.confirmation').style.display = 'block';
        //     // confirmation.innerText = "Go to the HIN tab to generate the HIN map!";

        //     if (mpo_not_county_bool){
        //       $.getJSON("/get_census_tract_boundaries_by_state_id_and_mpo_name/"+clicked_state+feature.properties.MPO_NAME, function(obj) {
        //         const mpo_census = obj;
        //         censusToMap(mpo_census);
        //         console.log("mpo census for ", feature.properties.MPO_NAME, "loaded");
        //         // map.addLayer(census_boundaries);
        //       });
        //     }
        //     else {
        //       $.getJSON("/get_census_tract_boundaries_by_state_id_and_county_name/"+clicked_state+feature.properties.COUNTY_NAME, function(obj) {
        //         const county_census = obj;
        //         censusToMap(county_census);
        //         console.log("county census for ", feature.properties.COUNTY_NAME, "loaded");
        //         // map.addLayer(census_boundaries);
        //       });
        //     }

            
        //     // Can't figure out how to dynamically restyle all the features in the feature group, tried many 
        //     // things, resorted to clearing the layer and remaking it when the user clicks a new boundary
        //     //setSelectionToMap(selected_feature_name, mpo_not_county_bool, geojson, thisLayer); 
        //   });
        // },
      });

      // CODE WHEN BACK BUTTON IS CLICKED
      function backButtonRegionClicked() {
        const backbtn2 = document.querySelector('#back2');        
        backbtn2.addEventListener("click", () => {
          map.fitBounds(thisLayer.getBounds());
          map.removeLayer(selection_boundaries);
          map.addLayer(county_boundaries);
          map.addControl(layerControl); 
          selection_boundaries.removeLayer(geojson_selection_boundaries_layer);

          document.querySelector('.region-click').style.display = 'none'; 
          document.querySelector('.back-button2').style.display = 'none';
          document.querySelector('.btn-confirm').style.display = 'none';
          document.querySelector('.after-region').style.display = 'none';

          document.querySelector('.after-state').style.display = 'block';
          document.querySelector('.back-button').style.display = 'block';
        });
      }

      backButtonRegionClicked();
      confirmClicked(mpo_not_county_bool, selected_feature_name, selected_feature_id, clicked_state);

      // console.log("geojson_selection_boundaries_layer", geojson_selection_boundaries_layer);
      selection_boundaries.addLayer(geojson_selection_boundaries_layer);
      return geojson_selection_boundaries_layer;
    }



    //------------------------------------------------------------------------------------------
    // CODE WHEN CONFIRM IS CLICKED
    function confirmClicked(mpo_not_county_bool, selected_feature_name, selected_feature_id, clicked_state){
      const conf = document.querySelector('#btnconfirm');
      conf.addEventListener("click", () => {
        document.querySelector('.back-button2').style.display = 'none';
        document.querySelector('.after-region').style.display = 'none';
        document.querySelector('.btn-confirm').style.display = 'none';

        if (mpo_not_county_bool){
          console.log("clicked state", clicked_state)
          $.getJSON("/get_census_tract_boundaries_by_state_id_and_mpo_name/"+clicked_state+ selected_feature_name, function(obj) {
            const mpo_census = obj;
            censusToMap(mpo_census);
            console.log("mpo census for ", selected_feature_name, "loaded");
          });
          $.getJSON("/get_fars_data_by_mpo/"+clicked_state+selected_feature_name, function(obj) {
            const mpo_fars = obj;
            fars_layer = farsToMap(mpo_fars);
            console.log("fars for ", selected_feature_name, "loaded");
          });
          if (clicked_state == 6 || clicked_state == 25){
            $.getJSON("/get_sds_data_by_mpo/"+clicked_state+selected_feature_name, function(obj) {
              const mpo_sds = obj;
              console.log(mpo_sds);
              sds_layer = sdsToMap(mpo_sds);
              console.log("sds for ", selected_feature_name, "loaded");
            });

            document.getElementById("sds").disabled = false;
          }
        }
        else {
          $.getJSON("/get_census_tract_boundaries_by_state_id_and_county_name/"+clicked_state+selected_feature_name, function(obj) {
            const county_census = obj;
            censusToMap(county_census);
            console.log("county census for ", selected_feature_name, "loaded");
          });
          $.getJSON("/get_fars_data_by_county/"+clicked_state+selected_feature_name, function(obj) {
            const county_fars = obj;
            fars_layer = farsToMap(county_fars);
            console.log("fars for ", selected_feature_name, "loaded");
          });
          //If it's california or massachusetts, load sds crashes
          if (clicked_state == 6 || clicked_state == 25){
            $.getJSON("/get_sds_data_by_county/"+clicked_state+selected_feature_name, function(obj) {
              const county_sds = obj;
              sds_layer = sdsToMap(county_sds);
              console.log("sds for ", selected_feature_name, "loaded");
            });
            document.getElementById("sds").disabled = false;
          }
        }

        let filter_btn = document.querySelectorAll('.filter-btn');
        let tab_items = document.querySelectorAll('.tab-item');

        for (let j = 0; j < filter_btn.length; j++) {
          filter_btn[j].classList.remove('active');
          tab_items[j].classList.remove('select_tab');
        }
        filter_btn[1].classList.add('active');
        tab_items[1].classList.add('select_tab');

        generateHIN(clicked_state, selected_feature_id);

      })
    }

    // -----------------------------------------------------------------------------------------
    // LOAD FARS DATA
    function farsToMap(fars_data){

      var markers = fars_data.data.map(function(arr) {
        return L.circleMarker([arr[0], arr[1]], {radius: 2, color: 'red'}).bindPopup("Coordinates:<br>" + [arr[0], arr[1]]);
      });

      layer = L.layerGroup(markers);

      //fars_points.addLayer(layer);
      return layer;
    }

    // -----------------------------------------------------------------------------------------
    // LOAD SDS DATA
    function sdsToMap(sds_data){

      var markers = sds_data.data.map(function(arr) {
        return L.circleMarker([arr[0], arr[1]], {radius: 2, color: 'CadetBlue'}).bindPopup("Coordinates:<br>" + [arr[0], arr[1]]);
      });

      layer = L.layerGroup(markers);

      //sds_points.addLayer(layer);
      return layer;
    }


    // -----------------------------------------------------------------------------------------
    // LOAD GEOJSON OF CENSUS BOUNDARIES
    function censusToMap(geojson){
      var geojson_census_layer = L.geoJSON(geojson, {
        style: function (feature) {
          return {
            color: "blue",
            weight: 1,
            opacity: 0.5,
            clickable: true
          };
        }
      });

      census_boundaries.addLayer(geojson_census_layer);
      return geojson_census_layer;
    }


    // -----------------------------------------------------------------------------------------
    // LOAD GEOJSON OF STATES


    function setStatesToMap(geojson){
      var geojson_state_boundaries_layer = L.geoJSON(geojson, {
        style: function (feature) {
          return {
            color: "red",
            weight: 1,
            opacity: 0.5,
            clickable: true
          };
        },
        onEachFeature: function (feature, layer) {
          var state_name = feature.properties.STATE_NAME.toString();
          layer.bindPopup(
            "<span>State Name:<br>" + state_name + "</span>"
          );

          layer.on('mouseover', function () {
            this.setStyle({
              'fillColor': 'yellow'
            });
            this.openPopup();
          });
          
          layer.on('mouseout', function () {
            this.setStyle({
              'fillColor': 'red'
            });
            this.closePopup(); 
          });

          layer.on('click', function (event) {
            var clicked_state = feature.properties.STATE_ID;
            var state_name = feature.properties.STATE_NAME.toString();
            console.log("Clicked state name and number: ", state_name, clicked_state);

            //show in the tab what state the users clicked
            document.querySelector('.state-click').style.display = 'block'; 
            document.querySelector('.after-state').style.display = 'block';
            document.querySelector('.back-button').style.display = 'block'; 
            state.innerText = clicked_state ? `You clicked state: ${state_name}` : `You haven't selected any state`;
            afterstate.innerText = "Now, you can either choose your county or mpo boundaries. To switch to mpo boundaries, click the radio button on the right side of the map.";


            map.fitBounds(this.getBounds());
            map.removeLayer(state_boundaries); // makes states transition to mpo/county

            $.getJSON("/get_mpo_boundaries_by_state_id/"+clicked_state, function(obj) {
              const geojson = obj;
              var geojson_mpo_boundaries_layer = setMposToMap(geojson, clicked_state, layer);
              console.log("mpo boundaries for state", clicked_state, "loaded");
            });

            $.getJSON("/get_county_boundaries_by_state_id/"+clicked_state, function(obj) {
              const geojson = obj;
              var geojson_county_boundaries_layer = setCountiesToMap(geojson, clicked_state, layer);
              console.log("county boundaries for state", clicked_state, "loaded");
            });

            map.addLayer(county_boundaries); // makes states transition to mpo/county
            map.addControl(layerControl); 
          });
        },
      }); 
      state_boundaries.addLayer(geojson_state_boundaries_layer);
      return geojson_state_boundaries_layer;
    }

    state_boundaries.addTo(map); // makes states always show up on first load of the web app

    // LOAD UP STATES LAYER ONTO THE MAP INITIALLY
    $.getJSON("/get_all_state_boundaries/", function(obj) {
      const geojson = obj;
      setStatesToMap(geojson);
      console.log("state boundaries loaded");
    });


    // ----------------------------------------------------------------------------------------------------
    // CODE TO CHECK WHAT DATABASE IS CLICKED
    function generateHIN(clicked_state, selected_feature_id) {
      const btn = document.querySelector('#rd-btn');        
      const radioButtons = document.querySelectorAll('input[name="database"]');
      var slider = document.getElementById("myRange");
      var sliderVal = document.getElementById("slidervalue");
      var toggle = document.getElementById("toggle");

      sliderVal.innerHTML = slider.value; 

      slider.oninput = function() {
        sliderVal.innerHTML = this.value;
      }

      btn.addEventListener("click", () => {
        map.addControl(startLayer);
        let selectedData;
        for (const radioButton of radioButtons) {
            if (radioButton.checked) {
              selectedData = radioButton.value;
                break;
            }
        }
        //choose what crash data to display
        if (selectedData == "fars"){
          crash_points.addLayer(fars_layer);
        }
        else if (selectedData == "sds"){
          crash_points.addLayer(sds_layer);
        }
        // show the output:
        output.innerText = selectedData ? `You selected ${selectedData} and ${slider.value}` : `You haven't selected any database`;
      
        console.log("IDDDDD", selected_feature_id);

        let threshold;
        if (slider.value == 0){
          threshold = parseFloat(0).toFixed(1);
        }
        else if (slider.value == 1){
          threshold = 0.0005;
        }
        else if (slider.value == 2){
          threshold = 0.001;
        }
        else if (slider.value == 3){
          threshold = 0.002;
        }


        $.getJSON({
          url: "/get_hin_by_county_id_and_properties", 
          data: {state_id: clicked_state, county_id: selected_feature_id, threshold: threshold}, 
          success: function(obj) {
          var hin_geojson = obj;
          console.log('HIN GEOJSON INSIDE', hin_geojson);
          hinToMap(hin_geojson);
          }
        });


        $.getJSON("/get_hin_properties/"+clicked_state+selected_feature_id+threshold, function(obj) {
          var hin_properties = obj;
          console.log('HIN PROPERTIES', hin_properties);
        });

        // get hin from the output
        // d3.json(hin_geojson, function(data) { 
        //   let percent_road = data.properties.percent_length.toFixed(2);
        //   let percent_crash = data.properties.percent_crashes.toFixed(2);
        //   console.log("percent_road", percent_road);
        //   console.log("percent_crash", percent_crash);

        //   var statVal = document.getElementById("stats");
        //   var statHeader = document.getElementById("stat-header");
        //   statHeader.innerText = "Statistics";
        //   statVal.innerText = `${percent_crash}% of the fatal traffic crashes occur on just ${percent_road}% of the Alameda streets`;

        //   const feature = L.geoJSON(data, {
        //     style: function (feature) {
        //       return {
        //         color: "blue",
        //         weight: 5,
        //         opacity: 0.5,
        //       };
        //     },
        //     onEachFeature: function (feature, layer) {
        //       roadHighlight_polylineLayer.addLayer(layer);
        //       const coordinates = feature.geometry.coordinates.toString();
        //     },
        //   });
        //   map.addLayer(roadHighlight_polylineLayer);
        // }); 

      });
    }

    function hinToMap(geojson){
      var geojson_hin_layer = L.geoJSON(geojson, {
        style: function (feature) {
          return {
            color: "darkblue",
            weight: 4,
            opacity: 0.5,
            clickable: true
          };
        }
      });

      roadHighlight_polylineLayer.addLayer(geojson_hin_layer);
      map.addLayer(roadHighlight_polylineLayer);

      return geojson_hin_layer;
    }
 
    // ------------------------------------------------------------------------------------
    // Map behaviour
    
    // centering a group of markers
    map.on("layeradd layerremove", function () {
      // Create new empty bounds
      let bounds = new L.LatLngBounds();
      // Check if bounds are valid (could be empty)
      if (bounds.isValid()) {
        // Valid, fit bounds
        map.flyToBounds(bounds);
      }
    });

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

    // // generate random color
    // function randomColor() {
    //   return `#${Math.floor(Math.random() * 16777215).toString(16)}`;
    // }

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
    // Normal map controls

    // object with layers
    const overlayMaps = {
      //"Circle Example": pA,
      //"Pin Example": pB,
      "Crash Points": crash_points,
      //"Heatmap Example": heatmapLayer,
      "Census Boundaries": census_boundaries,
      "HIN": roadHighlight_polylineLayer,
    };

    // Makes base layer and overlay controls inside default box instead of in new separate box
    var startLayer = L.control.layers(null, overlayMaps, {collapsed:false}).addTo(map);
    map.removeControl(startLayer);

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
    // Custom map controls

    var groupedOverlays = {
      "Geographic Boundaries":{
          //"State Boundaries":state_boundaries,
          "County Boundaries":county_boundaries,
          "MPO Boundaries":mpo_boundaries,
          //"Selected Boundaries":selection_boundaries,
      },
    }
    var options = {
      // Make the overlay group is exclusive (use radio inputs)
      exclusiveGroups: ["Geographic Boundaries"],
      // Show a checkbox next to non-exclusive group labels for toggling all:
      groupCheckboxes: true,
      collapsed: false,
    };

    // HAVE BEEN USING THIS ONE, EXCEPT THAT IT DOESN'T WORK WHEN LAYERS FOR MPO AND COUNTY AREN'T PRE-LOADED AND HAVEN'T FIGURED 
    // OUT HOW TO STYLE AFTER LOADING WITHOUT REDRAWING WHICH IS CALLED FROM INSIDE "click" METHOD
    // Use grouped layer plugin instead of "L.control.layers" to create radio boxes instead of checkboxes for overlays
    var layerControl = L.control.groupedLayers(null, groupedOverlays, options);
    //map.addControl(layerControl); 



    // // Makes separate controls box with a custom button to toggle between county or MPO
    // var custom_toggle_control = new L.Control.CustomToggle(null, null, { collapsed: false }).addTo(map);

    // // Makes separate overlay controls box with checkboxes
    // var custom_buttons_control = new L.Control.CustomButtons(baseLayers, overlayMaps, { collapsed: false }).addTo(map);



    return map;
}

var layer = L.layerGroup();

/*
This function gets the FARS data by state by querying the python file
It also plots the fars data on the map. 
*/

function getStateBoundariesByState(state_id) {
  $.getJSON("/get_state_boundaries_by_state_id/" + state_id, function(obj) {
     console.log ("state boundaries: ", obj)
      // var markers = obj.data.map(function(arr) {
      //     return L.circleMarker([arr[0], arr[1]], {radius: 2, color: 'red'}).bindPopup("Coordinates:<br>" + [arr[0], arr[1]]);
      // });
      // map.removeLayer(layer);
      // layer = L.layerGroup(markers);
      // map.addLayer(layer);
  });
}



// ----------------------------------------------------------------------------------------------------


// ----------------------------------------------------------------------------------------------------
// CODE TO CREATE TAB BAR
function make_tab() {
  let filter_btn = document.querySelectorAll('.filter-btn');
  let tab_items = document.querySelectorAll('.tab-item');

  for (let i = 0; i < filter_btn.length; i++) {
    filter_btn[i].addEventListener('click', function () {
      for (let j = 0; j < filter_btn.length; j++) {
        filter_btn[j].classList.remove('active');
      }
      let select_tab = filter_btn[i].getAttribute('data-tab');
      filter_btn[i].classList.add('active');
      for (let t = 0; t < tab_items.length; t++) {
        if (filter_btn[t].classList.contains('active')) {
          tab_items[t].classList.add('select_tab');
        } else {
          tab_items[t].classList.remove('select_tab');
        }
      }
      console.log(tab_items);
    });
  }
}


$(function() {
    map = makeMap();
    // make_sidebar();
    make_tab();
    //getFarsDataByState('0');

    // $('#statesel').change(function() {
    //     var val = $('#statesel option:selected').val();
    //     getFarsDataByState(val);
    //     getStateBoundariesByState(val);

    // });
})
