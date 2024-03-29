"""Generates a HIN map for a single state and county. Main function is `generate_hin_single_county`.

NOTE: Not all of the functions have docstrings because I ran out of time. The no docstrings functions are not intended to be used externally.
"""

## Installs and Imports


# NOTE: sqlalchemy version <2 is required
import argparse
import os

import geojson
import numpy as np
import pandas as pd
import geopandas as gpd
import osmnx as ox
import pyproj
import scipy.stats as st
import sqlalchemy as db
from sqlalchemy import text
from geojson import FeatureCollection, dump
from shapely.geometry import LineString, Point
from shapely.ops import transform, unary_union

import preprocess_utils

# Connect to database:
sqlalchemy_conn, metadata, engine = preprocess_utils.connect_to_sqlalchemy(
    include_metadata=True, include_engine=True)
print("Connected to database")

# The data parameters must be defined globally because they aren't passed through functions. Many of them are overwritten in other parts of the code.
# Data parameters:
start_year = 2016
datasource_name = ["SDS", "FARS"]

# HIN parameters:
bandwidth = 0.24
# TODO: choose better values based on standard deviation of the crash weight distribution
threshold_settings = [0.002, 0.001, 0.0005]

# Geographic parameters:
state_ids = [6]	
county_ids = [1]
table_name = 'SDS_California'
from_crs = 'EPSG:4269' # Assumes SDS crash data table CRS is always EPSG:4269 


""" Getting county information """

def get_county_boundaries_from_rds(state_id: int, county_id: int = None, mpo_id: int = None) -> gpd.GeoDataFrame:
    """Pulls county boundaries with specified parameters from the RDS and returns as a `gpd.GeoDataFrame`.

    Args:
        state_id: an integer specifying the state to pull county info from
        county_id: an integer specifying the county id (within the state) to pull
        mpo_id: an integer specifying the MPO area to pull. Ignored if county_id is not None

    Returns:
        A `gpd.GeoDataFrame` containing the county boundary

    NOTE: This function will probably break/give unexpected results if you pass a county_id or mpo_id without a state_id
    """
    if county_id is not None:
        sql = text(
            """ SELECT * FROM "boundaries_county" WHERE "STATE_ID" = {} AND "COUNTY_ID" = '{}' """.format(state_id, county_id))
    elif mpo_id is not None:
        sql = text(
            """ SELECT * FROM "boundaries_county" WHERE "STATE_ID" = {} AND "MPO_ID" = '{}' """.format(state_id, mpo_id))
    elif state_id is None:
        sql = text(""" SELECT * FROM "boundaries_county" """)
    else:
        sql = text(
            """ SELECT * FROM "boundaries_county" WHERE "STATE_ID" = {} """.format(state_id))

    gdf = gpd.read_postgis(sql, con=sqlalchemy_conn, crs='EPSG:4326')
    return gdf


def get_graph_from_county(county_bounds: gpd.GeoDataFrame):
    """Generates road network graph for the area in `county_bounds` and returns that information.

    Args:
        county_bounds: a `gpd.GeoDataFrame` specifying an area.

    Returns:
        A `networkx.MultiDiGraph` of the road network
        A `networkx.MultiDiGraph` of the road network, projected to the proper CRS
        A `gpd.GeoDataFrame` of nodes of the road network
        A `gpd.GeoDataFrame` of edges of the road network
    """

    combined_multipolygon = unary_union(county_bounds.geometry)
    G = ox.graph.graph_from_polygon(
        combined_multipolygon, network_type='drive')

    graph_proj = ox.project_graph(G, to_crs="EPSG:2805")
    nodes, edges = ox.graph_to_gdfs(graph_proj)

    return G, graph_proj, nodes, edges


""" Defining and creating Bins, Windows, and Corridors """
# Bin, Window, and Corridor could probably inherit from one of them or something to clean them up, but it's the end of the semester so no.

class Bin:
    """Bin class holds information for each road segment.

    Attributes:
        ids: a tuple of edge identifiers
        shape_points: a `shapely.geometry.linestring.LineString` with points that define the shape of this bin
        times_counted: an integer number of times this bin will get counted by sliding windows
        multiplier: a float multiplier to correct for undercounting122
    """

    def __init__(self, ids, shape_points, times_counted):
        self.ids = ids  # edge identifier tuple
        self.shape_points = shape_points  # points that define the shape of this bin
        # number of times this bin will get counted by sliding windows
        self.times_counted = times_counted
        self.multiplier = 5/times_counted  # multiplier to correct for undercounting
        self.crash_points = []
        self.crash_weights = []

    def make_buffer(self, radius):
        """Make the buffer area around the road, points inside this buffer will be matched to this road segment"""
        self.buffer = self.shape_points.buffer(
            radius, cap_style=2)  # square off ends of buffer
        return self.buffer

    def add_crash(self, crash_point, crash_weight):
        """Add a crash to this road"""
        self.crash_points.append(crash_point)
        self.crash_weights.append(crash_weight)

    def clear_crashes(self):
        """Clear crashes from this road"""
        self.crash_points = []
        self.crash_weights = []

    def get_crashes(self):
        """Get the crashes from this road.

        Returns:
            A list of crash points
            A list of crash weights (the crash_weight provided to add_crash times the multiplier)
            The sum of the multiplied crash weights
        """
        self.multiplied_weights = self.multiplier * \
            np.array(self.crash_weights)
        self.total_weight = sum(self.multiplied_weights)

        # location and weight of each crash to use in sliding window:
        return self.crash_points, self.multiplied_weights, self.total_weight


class Window:
    """Window class holds the information for each sliding window section

    Attributes:
        ids: a tuple of edge identifiers
        bins: a list of bins that make up this window
        shape_points: a `shapely.geometry.linestring.LineString` with points that define this bin
    """
    def __init__(self, ids, bins, shape_points):
        self.ids = ids  # edge identifier tuple
        self.bins = bins  # bins that make up this window
        self.shape_points = shape_points  # points that define the shape of this window

        self.crash_points = []
        self.crash_weights = []
        self.total_weight = 0

    def make_buffer(self, radius):
        """Make the buffer area around the window, points inside this buffer will be matched to this window"""
        self.buffer = self.shape_points.buffer(
            radius, cap_style=2)  # square off ends of buffer
        return self.buffer

    def get_crashes(self):
        """Get the crashes from this window.

        Returns:
            A list of crash points
            A list of crash weights (the crash_weight provided to add_crash times the multiplier)
            The sum of the multiplied crash weights
        """
        self.crash_points = []
        self.crash_weights = []
        self.total_weight = 0

        # Count up crash weight within that window
        for bin in self.bins:
            crash_points, crash_weights, total_weight = bin.get_crashes()
            self.crash_points.append(crash_points)
            self.crash_weights.append(crash_weights)
            self.total_weight += total_weight

        return self.crash_points, self.crash_weights, self.total_weight

    def get_center(self):
        """Get the center point of this window"""
        # Get center point of this window (linearly interpolated from points)
        center_point = self.shape_points.interpolate(
            self.shape_points.length/2)
        return center_point


class Corridor:
    """Corridor class holds information for each corridor. A corridor is made up of multiple windows.

    Attributes:
        ids: a tuple of edge identifiers
        shape_points: a `shapely.geometry.linestring.LineString` with points that define the shape of this corridor
    """
    def __init__(self, ids, shape_points, bins, windows):
        self.ids = ids  # edge identifier tuple
        self.bins = bins  # the bins on this road corridor
        # points that define the shape of this road corridor
        self.shape_points = shape_points
        self.windows = windows  # the windows along this road corridor

        self.crash_weights = []
        self.center_points = []

    def get_crashes(self):
        """Get the crashes from this corridor.

        Returns:
            A list of crash points
            A list of crash weights (the crash_weight provided to add_crash times the multiplier)
            The sum of the multiplied crash weights
        """
        self.crash_weights = []
        self.center_points = []

        for window in self.windows:
            crash_points, crash_weights, total_weight = window.get_crashes()
            center_point = window.get_center()
            self.crash_weights.append(total_weight)
            self.center_points.append(center_point)

        return self.crash_weights, self.center_points

    def run_kde(self, bandwidth):
        """Runs KDE on the sliding window.

        I do not understand this code, I'm just the person with time to add docstrings. Hopefully the existing comments are good enough for you. Sorry.

        Args:
            bandwidth: an int, passed to `scipy.stats.gaussian_kde(...,bw_method=bandwidth)`

        Returns:
            TODO: I don't understand the code so I don't understand the returns
        """
        # Run kde on sliding window counts - use st.gaussian_kde(data, weights)
        #    'data' argument allows placing crash_weights at the correct locations/spacings

        # Get initial crash weight info
        self.get_crashes()
        # print("crash_weights", self.crash_weights)
        # print("center_points", self.center_points)

        self.modified_crash_weights = self.crash_weights
        self.modified_center_points = self.center_points

        if sum([i > 0 for i in self.crash_weights]) >= 1:  # Case 1: can run KDE

            # Constructs an array of the 1D linear distance between the center points of
            #     windows, which will be used in kde function to place weights at correct locations:
            national_survey_foot = 1.000002
            feet_per_mile = 5280
            national_survey_feet_per_tenth_mile = feet_per_mile/national_survey_foot/10
            arr = [0] + [self.windows[i].shape_points.length/2 + i *
                         national_survey_feet_per_tenth_mile for i in range(len(self.windows))]
            arr.append(self.windows[-1].shape_points.length +
                       (len(self.windows)-1)*national_survey_feet_per_tenth_mile)
            center_points_1d = arr[1:-1]

            # Edge case: need to distribute crash weight in order to make KDE work
            if len(self.modified_crash_weights) == 1:
                # TODO: think about whether spreading out crash weight like this is valid
                self.modified_crash_weights = [self.modified_crash_weights[0]*0.1,
                                               self.modified_crash_weights[0]*0.8, self.modified_crash_weights[0]*0.1]
                self.modified_center_points = [Point(self.windows[0].shape_points.coords[0]), self.modified_center_points[0], Point(
                    self.windows[0].shape_points.coords[-1])]

                center_points_1d = [
                    0, self.windows[0].shape_points.length/2, self.windows[0].shape_points.length]

            # Edge case: need to distribute crash weights in order to run KDE
            elif sum([i > 0 for i in self.modified_crash_weights]) == 1:
                if self.modified_crash_weights[0] > 0:
                    self.modified_crash_weights[0] = self.modified_crash_weights[0] - 1
                    self.modified_crash_weights[1] = 1
                elif self.modified_crash_weights[-1] > 0:
                    self.modified_crash_weights[-1] = self.modified_crash_weights[-1] - 1
                    self.modified_crash_weights[-2] = 1
                else:
                    idx = None
                    for i in range(len(self.modified_crash_weights)):
                        if self.modified_crash_weights[i] > 0:
                            idx = i
                    self.modified_crash_weights[idx] = self.modified_crash_weights[idx]*0.8
                    self.modified_crash_weights[idx +
                                                1] = self.modified_crash_weights[idx]*0.1
                    self.modified_crash_weights[idx -
                                                1] = self.modified_crash_weights[idx]*0.1

            # kde = st.gaussian_kde(center_points_1d, weights=self.modified_crash_weights, bw_method="silverman") # TODO: is silverman the right bandwidth?
            # based on experiments, bandwidth 0.24 worked fairly well
            kde = st.gaussian_kde(
                center_points_1d, weights=self.modified_crash_weights, bw_method=bandwidth)

            # makes 100 points along road length
            x = np.linspace(0, self.shape_points.length, num=100)

            # TODO: sample equidistant points rather than 100 pts/corridor, so that you get better and more constant resolution for drawing on map
            # x = np.arange(0, self.points.length, 50) # make 1 point every 50 US survey feet
            # if self.points.length % 50 != 0.0:
            #   x = np.append(x, self.points.length) # add final point caused by remainder

            y = kde(x)

            hin_points = [self.shape_points.interpolate(
                distance) for distance in x]

            self.x = x
            self.y = y
            self.hin_points = hin_points
            self.center_points_1d = center_points_1d
            return x, y, hin_points, center_points_1d

        elif sum([i > 0 for i in self.modified_crash_weights]) == 0:  # Case 2A: can't run KDE
            # print("Can't run KDE on all zero crash weights")
            return None, None, None, None

        else:  # Case 3: It should not be possible to have zero windows on a corridor
            print("crash_weights     ", (self.modified_crash_weights))
            print("It should not be possible to have zero windows on a corridor")
            return None, None, None, None


def create_bins(edges):
    """Create bin objects for each edge

    NOTE: I don't actually know the difference between original points and points in the returns

    Args:
        edges: a list of edges from the road graph

    Returns:
        A dictionary containing a tuple of edge ids as keys and a bin object as values \n
        A dictionary containing a tuple of edge ids as keys and a `shapely.geometry.linestring.LineString` of the original points defining the bin as values \n
        A dictionary containing a tuple of edge ids as keys and a `shapely.geometry.linestring.LineString` of more granular points defining the bin as values \n
        A dictionary containing a tuple of edge ids as keys and a `shapely.geometry.linestring.LineString` of points defining the bin as values \n
        A dictionary containing a tuple of edge ids as keys and a dictionary of the information of that edge as values \n
    """
    original_points_by_edge = {}
    points_granular_by_edge = {}
    points_by_edge = {}
    bins_by_edge = {}
    edges_by_id_tuple = {}
    edge_id = 0

    national_survey_foot = 1.000002
    feet_per_mile = 5280
    national_survey_feet_per_tenth_mile = feet_per_mile/national_survey_foot/10
    distance_delta = national_survey_feet_per_tenth_mile

    scale_factor = 100

    for edge in edges.iterfeatures():
        ids = edge["id"][1:-1].split()
        edges_by_id_tuple[tuple(ids)] = edge
        length = edge["properties"]["length"]
        coords = edge["geometry"]["coordinates"]
        line = LineString(coords)
        original_points_by_edge[tuple(ids)] = line

        distances = np.arange(0, line.length, distance_delta)
        distances_granular = np.arange(
            0, line.length, distance_delta/scale_factor)

        if not line.boundary.is_empty:
            points = [line.interpolate(
                distance) for distance in distances] + [line.boundary.geoms[1]]
            points_granular = [line.interpolate(
                distance) for distance in distances_granular] + [line.boundary.geoms[1]]
        else:
            points = [line.interpolate(
                distance) for distance in distances] + [edge["geometry"]["coordinates"][0]]
            points_granular = [line.interpolate(
                distance) for distance in distances_granular] + [edge["geometry"]["coordinates"][0]]
        points_linestring = LineString(points)
        points_granular_linestring = LineString(points_granular)

        for i in range(len(points)-1):
            if len(points) > 1:
                bin_linestring = LineString(points[i:i+1+1])
                bin_granular_linestring = LineString(
                    points_granular[i*scale_factor:(i+1)*scale_factor+1])

            if i < 5 and i <= (len(points)-1)/2:
                times_counted = i+1
            elif i > len(points)-1-5:
                times_counted = (len(points)-1-i)

            bin = Bin(ids, bin_granular_linestring, times_counted)

            if tuple(ids) in bins_by_edge:
                bins_by_edge[tuple(ids)].append(bin)
            else:
                bins_by_edge[tuple(ids)] = [bin]

        points_by_edge[tuple(ids)] = points_linestring
        points_granular_by_edge[tuple(ids)] = points_granular_linestring

        edge_id += 1

    return bins_by_edge, original_points_by_edge, points_granular_by_edge, points_by_edge, edges_by_id_tuple


def create_windows(edges, bins_by_edge, points_by_edge, points_granular_by_edge):
    """Create window objects for each edge

    Args:
        edges: a list of edges from the road graph
        bins_by_edge: a dictionary containing a tuple of edge ids as keys and a bin object as values
        points_by_edge: a dictionary containing a tuple of edge ids as keys and a `shapely.geometry.linestring.LineString` of points defining the bin as values
        points_granular_by_edge: a dictionary containing a tuple of edge ids as keys and a `shapely.geometry.linestring.LineString` of more granular points defining the bin as values

    Returns:
        A dictionary containing a tuple of edge ids as keys and a window object as values
    """
    bins_per_window = 5
    scale_factor = 100
    windows_by_edge = {}

    for edge in edges.iterfeatures():
        ids = edge["id"][1:-1].split()

        num_windows = 1
        if len(bins_by_edge[tuple(ids)])-bins_per_window+1 > 0:
            num_windows = len(bins_by_edge[tuple(ids)])-bins_per_window+1

        for j in range(num_windows):
            bins = bins_by_edge[tuple(ids)][j:j+bins_per_window]

            linestring = LineString(
                points_by_edge[tuple(ids)].coords[j:j+bins_per_window+1])
            linestring_granular = LineString(points_granular_by_edge[tuple(
                ids)].coords[j*scale_factor:(j+bins_per_window)*scale_factor+1])

            window = Window(ids, bins, linestring_granular)

            if tuple(ids) in windows_by_edge:
                windows_by_edge[tuple(ids)].append(window)
            else:
                windows_by_edge[tuple(ids)] = [window]

    return windows_by_edge


def create_corridors(edges, bins_by_edge, points_by_edge, points_granular_by_edge, windows_by_edge):
    """Create corridor objects for each edge

    Args:
        edges: a list of edges from the road graph
        bins_by_edge: a dictionary containing a tuple of edge ids as keys and a bin object as values
        points_by_edge: a dictionary containing a tuple of edge ids as keys and a `shapely.geometry.linestring.LineString` of points defining the bin as values
        points_granular_by_edge: a dictionary containing a tuple of edge ids as keys and a `shapely.geometry.linestring.LineString` of more granular points defining the bin as values
        windows_by_edge: a dictionary containing a tuple of edge ids as keys and a window object as values

    Returns:
        A dictionary containing a tuple of edge ids as keys and a window object as values
    """
    corridors_by_edge = {}
    for edge in edges.iterfeatures():
        ids = edge["id"][1:-1].split()
        corridor = Corridor(ids, points_by_edge[tuple(
            ids)], bins_by_edge[tuple(ids)], windows_by_edge[tuple(ids)])
        corridors_by_edge[tuple(ids)] = corridor

    return corridors_by_edge


# Get the FARS and SDS crash data


def get_fars_crashes(state_id, county_id, start_year):
    """Returns FARS crashes for given state + county for years later than start_year.

    Args:
        state_id: the integer ID of the state to pull
        county_id: the integer ID of the county (within the state specified by state_id) to pull
        start_year: the integer year to pull all data during or after

    Returns:
        A `pd.DataFrame` with only geometry and SEVERITY columns of the FARS data matching the parameters
    """

    FARS = db.Table('FARS', metadata, autoload=True, autoload_with=engine)
    fars_query = db.select([FARS]).where(db.and_(FARS.columns.STATE_ID == state_id,
                                                 FARS.columns.COUNTY_ID == county_id, 
                                                 FARS.columns.YEAR >= start_year))
    ResultProxy = sqlalchemy_conn.execute(fars_query)
    fars_crashes = ResultProxy.fetchall()
    fars_pdf = pd.DataFrame(fars_crashes)
    # display(fars_pdf[0:5])

    # Transform into national survey feet from lat/lon:
    proj = pyproj.Transformer.from_crs(pyproj.CRS(
        'EPSG:4326'), pyproj.CRS('EPSG:2805'), always_xy=True)
    x2, y2 = proj.transform(fars_pdf['LON'], fars_pdf['LAT'])
    fars_df_nsf = pd.DataFrame({'LON': x2, 'LAT': y2, 'espg': pyproj.CRS(
        'EPSG:2805'), 'SEVERITY': fars_pdf['SEVERITY']}, index=fars_pdf['LAT'].index)

    # Turn LAT, LON into Point():
    fars_gdf = gpd.GeoDataFrame(fars_df_nsf, geometry=gpd.points_from_xy(
        fars_df_nsf['LON'], fars_df_nsf['LAT']), crs="EPSG:2805")

    # Narrow down columns:
    fars_df = pd.concat([fars_gdf['geometry'], fars_gdf['SEVERITY']], axis=1)
    return fars_df


def get_sds_crashes(table_name, county_id, start_year, from_crs):
    """Return SDS crashes for given state + county for years later than 'start_year'.

    Different states' SDS data may have different coordinate reference systems (CRS) therefore the original CRS of the input data is needed.
    TODO: In the future, the SDS data should be transformed to a consistent CRS rather than doing that here. We didn't realize that so it's here now.

    Args:
        table_name: which table to pull. The database has a different table for each state. For example, California SDS data is in the SDS_California table.
        county_id: the integer ID of the county (within the state specified by table_name) to pull
        start_year: the integer year to pull all data during or after
        from_crs: a string specifying the coordinate reference system (crs) of the source data

    Returns:
        a `pd.DataFrame` with only geometry and SEVERITY columns of the SDS data matching the parameters
    """

    SDS_table = db.Table(table_name, metadata,
                         autoload=True, autoload_with=engine)

    sds_query = db.select([SDS_table]).where(db.and_(SDS_table.columns.COUNTY_ID ==
                                                     county_id, SDS_table.columns.YEAR > start_year, 
                                                     SDS_table.columns.SEVERITY > 0))
    ResultProxy = sqlalchemy_conn.execute(sds_query)
    sds_crashes = ResultProxy.fetchall()
    sds_pdf = pd.DataFrame(sds_crashes)
    # display(sds_pdf[0:5])

    # Transform into national survey feet from lat/lon:
    proj = pyproj.Transformer.from_crs(pyproj.CRS(
        from_crs), pyproj.CRS('EPSG:2805'), always_xy=True)
    x2, y2 = proj.transform(sds_pdf['LON'], sds_pdf['LAT'])
    sds_df_nsf = pd.DataFrame({'LON': x2, 'LAT': y2, 'espg': pyproj.CRS(
        'EPSG:2805'), 'SEVERITY': sds_pdf['SEVERITY']}, index=sds_pdf['LAT'].index)

    # Turn LAT, LON into Point():
    sds_gdf = gpd.GeoDataFrame(sds_df_nsf, geometry=gpd.points_from_xy(
        sds_df_nsf['LON'], sds_df_nsf['LAT']), crs="EPSG:2805")

    # Narrow down columns:
    sds_gdf = pd.concat([sds_gdf['geometry'], sds_gdf['SEVERITY']], axis=1)
    return sds_gdf


""" Crash matching and processing """

def get_nearest_edges_to_crashes(crash_df, graph_proj):
    """Finds the nearest edge to each crash by shortest linear distance.

    Args:
        crash_df: a `pd.DataFrame` of each crash
        graph_proj: the CRS projection of the graph

    Returns:
        A tuple with the IDs of the nearest edges as keys and the ID of the nearest edge as values

    TODO: Check types
    """

    # Get the nearest edge to each crash point:
    crash_xs = []
    crash_ys = []
    for index, crash in crash_df.iterrows():
        crash_xs.append(crash["geometry"].x)
        crash_ys.append(crash["geometry"].y)

    # nearest_edge_ids = ox.distance.nearest_edges(graph_proj, crash_xs, crash_ys) #, interpolate=None)
    [nearest_edge_ids, returned_dist] = ox.distance.nearest_edges(
        graph_proj, crash_xs, crash_ys, return_dist=True)
    nearest_edge_ids_tuple = [
        tuple([str(ne[0])+",", str(ne[1])+",", str(ne[2])]) for ne in nearest_edge_ids]
    return nearest_edge_ids_tuple


def move_crashes_to_edges(crash_df, edges_by_id_tuple, nearest_edge_ids_tuple):

    """Moves crashes to the nearest location on the nearest road edge.

    Args:
        crash_df: a `pd.DataFrame` of crashes
        edges_by_id_tuple: a dictionary containing a tuple of edge ids as keys and a dictionary of the information of that edge as values
        nearest_edge_ids_tuple: ignoreme

    Returns:
        A modified `pd.DataFrame` of the `crash_df` with the added column `corrected_geometry`
    """

    crash_df['corrected_geometry'] = None

    for index, crash in crash_df.iterrows():

        nearest_edge = edges_by_id_tuple[nearest_edge_ids_tuple[index]]
        # print("nearest_edge found") #, nearest_edge)
        coords = nearest_edge["geometry"]["coordinates"]
        nearest_edge_line = LineString(coords)

        # Compute the closest point on the nearest road to the crash location
        nearest_point = nearest_edge_line.interpolate(
            nearest_edge_line.project(crash[0]))
        # print("nearest_point found") #, nearest_point)
        # print("correction amount", crash[0].x-nearest_point.x, crash[0].y-nearest_point.y)

        # Update the geometry column with the corrected location
        crash_df['corrected_geometry'][index] = Point(
            nearest_point.x, nearest_point.y)

    return crash_df


def clear_crashes_from_bins(bins_by_edge):

    for idx in bins_by_edge:
        for bin in bins_by_edge[tuple(idx)]:
            bin.clear_crashes()


def put_crashes_into_bins(crash_df, bins_by_edge, edges_by_id_tuple, nearest_edge_ids_tuple):
    """
    Puts crashes into the nearest bin by going through each bin on the nearest 
    edge and finding the one with the shortest linear distance.

    edges_by_id_tuple: A dictionary containing a tuple of edge ids as keys and a dictionary of the information of that edge as values
    """

    # crashes_by_edge = {}
    for index, crash in crash_df.iterrows():

        nearest_edge = edges_by_id_tuple[nearest_edge_ids_tuple[index]]
        nearest_edge_id = nearest_edge["id"][1:-1].split()
    
        # Compute the closest point on the nearest road to the crash location
        nearest_point = crash_df['corrected_geometry'][index]
        # print(crash[0], nearest_point)
        # print("correction amount", crash[0].x-nearest_point.x, crash[0].y-nearest_point.y)

        min_distance = float('inf')
        nearest_bin = None
        for bin in bins_by_edge[tuple(nearest_edge_id)]:
            distance = bin.shape_points.distance(nearest_point)
            if distance < min_distance:
                min_distance = distance
                nearest_bin = bin

        crash_weight = 1
        if crash["SEVERITY"] == 1:
            crash_weight = 4
        elif crash["SEVERITY"] == 2:
            crash_weight = 3
        elif crash["SEVERITY"] == 3:
            crash_weight = 2
        elif crash["SEVERITY"] == 4:
            crash_weight = 1

        nearest_bin.add_crash(nearest_point, crash_weight)

    # print("crashes_by_edge", crashes_by_edge)


""" Calculate HIN """

def calculate_unthresholded_hin(bandwidth, corridors_by_edge):
    """
    Calculate an unthresholded HIN with the equity multiplier given. Returns 
    'features' which can be later written to a json file then plotted on map.  
    """

    projector = pyproj.Transformer.from_crs(pyproj.CRS(
        'EPSG:2805'), pyproj.CRS('EPSG:4326'), always_xy=True).transform

    features = []
    road_length_unthr_hin = 0

    for idx in corridors_by_edge:

        corr = corridors_by_edge[idx]
        corr_crash_weights, corr_center_points = corr.get_crashes()

        if len(corr.crash_weights) > 0:

            x, y, hin_points, center_points_1d = corr.run_kde(bandwidth)

            hin_points_by_corridor = []
            hin_weights_by_corridor = []

            if hin_points != None:
                hin_points_linestring = LineString(hin_points)
                road_length_unthr_hin += hin_points_linestring.length

                hin_points_latlon = []
                for pt in hin_points:
                    pt_latlon = transform(projector, pt)
                    hin_points_latlon.append(pt_latlon)

                hin_points_by_corridor = [
                    [hin_points_latlon[j].x, hin_points_latlon[j].y] for j in range(len(hin_points_latlon))]
                hin_weights_by_corridor = list(y)

                features.append(geojson.Feature(properties={"type": "polyline"},
                                                weight=hin_weights_by_corridor,
                                                geometry=LineString(hin_points_by_corridor)))
    return road_length_unthr_hin, features


def calculate_thresholds(corridors_by_edge, original_points_by_edge, threshold_settings):

    num_points_along_edge = 100  # This has to match the value used in 'run_kde()'
    crash_pt_dist_thr = 0.1  # TODO: figure out better value than arbitrarily setting this

    projector = pyproj.Transformer.from_crs(pyproj.CRS(
        'EPSG:2805'), pyproj.CRS('EPSG:4326'), always_xy=True).transform

    features_by_thr = {}
    length_by_thr = {}
    num_crashes_by_thr = {}

    for thr_set in threshold_settings:
        features_by_thr[thr_set] = []
        length_by_thr[thr_set] = 0
        num_crashes_by_thr[thr_set] = 0

    for idx in corridors_by_edge:
        corr = corridors_by_edge[idx]
        hin_points_by_corridor = []
        hin_weights_by_corridor = []

        if hasattr(corr, "hin_points"):  # checks that run_kde() ran and hin_points was not None
            y = corr.y
            hin_points = corr.hin_points

            corr_crash_points = []

            for bin in corr.bins:
                # print(bin, bin.ids, bin.crash_points, bin.shape_points)
                corr_crash_points = corr_crash_points + bin.crash_points

            for thr_set in threshold_settings:
                num_crashes_on_thresholded_corridor = 0
                weights_buffer = []
                points_buffer = []
                length_buffer = 0

                for i in range(len(y)):
                    if y[i] > thr_set:
                        weights_buffer.append(y[i])
                        points_buffer.append(hin_points[i])
                    else:
                        if len(weights_buffer) > 0:

                            if len(weights_buffer) == 1:  # In case this edge case becomes a problem
                                original_edge_geometry_line = original_points_by_edge[tuple(
                                    corr.ids)]
                                length_buffer = original_edge_geometry_line.length / \
                                    (num_points_along_edge-1)
                                points_buffer = [original_edge_geometry_line.interpolate(length_buffer*i-length_buffer/2),
                                                 points_buffer[0],
                                                 original_edge_geometry_line.interpolate(length_buffer*i+length_buffer/2)]
                                weights_buffer = [
                                    weights_buffer[0], weights_buffer[0], weights_buffer[0]]
                                points_buffer_linestring = LineString(
                                    points_buffer)

                            else:
                                points_buffer_linestring = LineString(
                                    points_buffer)
                                length_buffer = points_buffer_linestring.length

                            # Calculate crashes on this points_buffer and add to final crash count
                            for crash_pt in corr_crash_points:
                                # crash_pt_dist = points_buffer_linestring.distance(crash_pt)
                                points_buffer_shape = points_buffer_linestring.buffer(
                                    6, cap_style=2)  # square off ends of buffer
                                bool_iswithin = points_buffer_shape.contains(
                                    crash_pt)
                                # print(bool_iswithin, crash_pt_dist < crash_pt_dist_thr)

                                # if crash_pt_dist < crash_pt_dist_thr:
                                if bool_iswithin:
                                    num_crashes_on_thresholded_corridor += 1

                            num_crashes_by_thr[thr_set] = num_crashes_by_thr[thr_set] + \
                                num_crashes_on_thresholded_corridor
                            # Clear out crashes after they are added to not double-count
                            num_crashes_on_thresholded_corridor = 0

                            # Do coordinate transform and create feature
                            points_buffer_latlon = []
                            for pt in points_buffer:
                                pt_latlon = transform(projector, pt)
                                points_buffer_latlon.append(pt_latlon)

                            # Save length and feature to dictionaries
                            ftr = geojson.Feature(properties={
                                                  "type": "polyline"}, weight=weights_buffer, geometry=LineString(points_buffer_latlon))
                            features_by_thr[thr_set].append(ftr)
                            # purely keeps track of total length, not broken down by corridor
                            length_by_thr[thr_set] += length_buffer
                            length_buffer = 0

                        weights_buffer = []
                        points_buffer = []

                if len(weights_buffer) > 0:
                    # Get length of this points_buffer

                    if len(weights_buffer) == 1:  # In case this edge case becomes a problem
                        original_edge_geometry_line = original_points_by_edge[tuple(
                            corr.ids)]
                        length_buffer = original_edge_geometry_line.length / \
                            (num_points_along_edge-1)
                        points_buffer = [original_edge_geometry_line.interpolate(length_buffer*i-length_buffer/2),
                                         points_buffer[0],
                                         original_edge_geometry_line.interpolate(length_buffer*i+length_buffer/2)]
                        weights_buffer = [weights_buffer[0],
                                          weights_buffer[0], weights_buffer[0]]
                        points_buffer_linestring = LineString(points_buffer)

                    else:
                        points_buffer_linestring = LineString(points_buffer)
                        length_buffer = points_buffer_linestring.length

                    # Calculate crashes on this points_buffer and add to final crash count
                    for crash_pt in corr_crash_points:
                        # crash_pt_dist = points_buffer_linestring.distance(crash_pt)
                        points_buffer_shape = points_buffer_linestring.buffer(
                            6, cap_style=2)  # square off ends of buffer
                        bool_iswithin = points_buffer_shape.contains(crash_pt)
                        # print(bool_iswithin, crash_pt_dist < crash_pt_dist_thr)

                        # if crash_pt_dist < crash_pt_dist_thr:
                        if bool_iswithin:
                            num_crashes_on_thresholded_corridor += 1

                    num_crashes_by_thr[thr_set] = num_crashes_by_thr[thr_set] + \
                        num_crashes_on_thresholded_corridor
                    # Clear out crashes after they are added to not double-count
                    num_crashes_on_thresholded_corridor = 0

                    # Do coordinate transform and create feature
                    points_buffer_latlon = []
                    for pt in points_buffer:
                        pt_latlon = transform(projector, pt)
                        points_buffer_latlon.append(pt_latlon)

                    # Save length and feature to dictionaries
                    ftr = geojson.Feature(properties={
                                          "type": "polyline"}, weight=weights_buffer, geometry=LineString(points_buffer_latlon))
                    features_by_thr[thr_set].append(ftr)
                    # purely keeps track of total length, not broken down by corridor
                    length_by_thr[thr_set] += length_buffer
                    length_buffer = 0

    return features_by_thr, length_by_thr, num_crashes_by_thr


""" Statistics"""

def calculate_total_road_length(edges):

    total_road_length = 0

    for edge in edges.iterfeatures():

        # Get the index, length, and coordinates of this edge
        ids = edge["id"][1:-1].split()
        coords = edge["geometry"]["coordinates"]
        line = LineString(coords)
        line_length = line.length
        total_road_length += line_length

    return total_road_length


def calculate_hin_statistics(crash_df, edges, road_length_unthr, length_by_thr, num_crashes_by_thr, threshold_settings):
    results = {}

    total_road_length = calculate_total_road_length(edges)
    results['total_road_length'] = total_road_length
    results['road_length'] = {}
    results['percent_road_length'] = {}
    for thr_set in threshold_settings:
        length = length_by_thr[thr_set]
        results['road_length'][thr_set] = length
        results['percent_road_length'][thr_set] = length/total_road_length*100
    results['road_length'][0.0] = road_length_unthr
    results['percent_road_length'][0.0] = road_length_unthr / \
        total_road_length*100

    total_crash_count = len(crash_df)
    results['total_crash_count'] = total_crash_count
    results['num_crashes'] = {}
    results['percent_crashes'] = {}
    for thr_set in threshold_settings:
        num_crashes = num_crashes_by_thr[thr_set]
        results['num_crashes'][thr_set] = num_crashes
        results['percent_crashes'][thr_set] = num_crashes/total_crash_count*100
    results['num_crashes'][0.0] = total_crash_count
    results['percent_crashes'][0.0] = 100.0

    return results


def get_census_tract_boundaries_from_rds(state_id: int, county_id: int = None, mpo_id: int = None):

    if county_id is not None:
        sql = text(
            """ SELECT * FROM "boundaries_census_tract_v3" WHERE "STATE_ID" = {} AND "COUNTY_ID" = '{}' """.format(state_id, county_id))
    elif mpo_id is not None:
        sql = text(
            """ SELECT * FROM "boundaries_census_tract_v3" WHERE "STATE_ID" = {} AND "MPO_ID" = '{}' """.format(state_id, mpo_id))
    elif state_id is None:
        sql = text(""" SELECT * FROM "boundaries_census_tract_v3" """)
    else:
        sql = text(
            """ SELECT * FROM "boundaries_census_tract_v3" WHERE "STATE_ID" = {} """.format(state_id))

    gdf = gpd.read_postgis(sql, con=sqlalchemy_conn, crs='EPSG:4326')
    # print(type(gdf))
    # test = gdf.to_json()

    return gdf


def calculate_joined_features(features_by_thr, j40_bounds):
    j40_bounds = j40_bounds.to_crs("EPSG:2805")
    j40_bounds = j40_bounds.set_geometry('geom')
    # print("len(j40_bounds)", len(j40_bounds))

    joined_features_by_thr = {}

    for key in features_by_thr.keys():
        features_gdf = gpd.GeoDataFrame(features_by_thr[key], crs="EPSG:4326")
        features_gdf = features_gdf.to_crs("EPSG:2805")
        features_gdf = features_gdf.set_geometry('geometry')
        # print("len(features_gdf)", len(features_gdf))

        joined_gdf = gpd.sjoin(features_gdf, j40_bounds,
                               how="inner", predicate="intersects")
        joined_gdf = joined_gdf.drop(columns=[
                                     'index_right', 'STATE_ID', 'STATE_NAME', 'COUNTY_ID', 'COUNTY_NAME', 'MPO_NAME', 'CENSUS_TRACT_ID'])
        joined_gdf = joined_gdf.rename(
            columns={'IDENTIFIED_AS_DISADVANTAGED': 'IN_J40'})
        joined_gdf = joined_gdf.to_crs("EPSG:4326")

        # Convert from geodataframe back to array of individual geojson features,
        # preserving original geojson feature formatting.
        # TODO: There is probably a better way to do this
        joined_features = []
        for row in joined_gdf.iterfeatures():
            f = geojson.Feature(type=row["properties"]["type"],
                                properties=row["properties"]["properties"],
                                IN_J40=row["properties"]["IN_J40"],
                                weight=row["properties"]["weight"],
                                geometry=row["geometry"])
            joined_features.append(f)

        joined_features_by_thr[key] = joined_features
        # print("joined_features_by_thr[key] ", joined_features_by_thr[key] )
        # print("len(joined_features_by_thr[",key,"])", len(joined_features_by_thr[key]))

    return joined_features_by_thr


""" Save to files """

def save_feature_collections(state_id, county_id, crash_data_source, threshold_settings, joined_features_by_thr, results):	
    main_folder = "HIN_Outputs"	
    os.makedirs(main_folder, exist_ok=True)

    state_folder = f'state_{state_id}'
    os.makedirs(os.path.join(main_folder, state_folder), exist_ok=True)

    total_road_length = results['total_road_length']
    total_crash_count = results['total_crash_count']

    summary = ["Total:\t\t\t" + str(round(total_road_length)) +
               " national survey feet\t\t" + str(total_crash_count) + " crashes"]

    for thr_set in results['road_length']:
        road_length = results['road_length'][thr_set]
        num_crashes = results['num_crashes'][thr_set]

        summary.append(str(thr_set) + " threshold HIN:\t" +
                       str(round(road_length)) + " national survey feet\t" +
                       str(round(road_length/total_road_length*100, 3)) + "%\t" +
                       str(num_crashes) + " crashes\t" +
                       str(round(num_crashes/total_crash_count*100, 3)) + "%")

        feature_collection = FeatureCollection(properties={"state_id": state_id,
                                                           "county_id": county_id,
                                                           "data_source": crash_data_source,
                                                           "threshold": thr_set,
                                                           "length": road_length,
                                                           "num_crashes": num_crashes,
                                                           "total_length": total_road_length,
                                                           "total_crashes": total_crash_count,
                                                           "percent_length": road_length/total_road_length*100,
                                                           "percent_crashes": num_crashes/total_crash_count*100},
                                               features=joined_features_by_thr[thr_set])

        hin_filename = f'hin_state_{state_id}_county_{county_id}_source_{crash_data_source}_threshold_{str(thr_set)[2:]}.geojson'
        with open(os.path.join(main_folder, state_folder, hin_filename), 'w') as f:
            dump(feature_collection, f)

    summary_filename = f'hin_summary_state_{state_id}_county_{county_id}_source_{crash_data_source}.txt'
    with open(os.path.join(main_folder, state_folder, summary_filename), 'w') as f:
        for line in summary:
            f.write(f"{line}\n")

    return "\n".join(summary)


def generate_hin_single_county(state_id=6, county_id=1, dataset='SDS', table_name='California'):
    """Generates the HIN files for a single county.

    All this code is wrapped in a try/except loop. Most of the HINs generate correctly, but there are edge cases that we haven't had time to investigate.

    Args:
        state_id: an integer specifying the state where the county is contained. State numbers correspond to US FIPS codes. Defaults to 6 (California)
        county_id: an integer specifying the county to generate a HIN for. County numbers correspond to US FIPS codes. Defaults to 1 (Alameda County, CA)
        dataset: a string specifying the dataset to use to generate the HIN. If the dataset is 'FARS' or if the table name is invalid, then FARS data will be used. Defaults to 'SDS'.
        table_name: a string specifying the table name for the SDS data. If the table name is 'California' or 'Massachusetts' and the dataset is not 'FARS', then the SDS data for that state is used. Defaults to 'California'

    Returns:
        None

    NOTE: The dataset and table name parameter behaviors could probably be cleaned up and maybe combined into one parameter.
    """

    try:

        # Data parameters:
        start_year = 2016
        if table_name == 'California':
            table_name = 'SDS_California'
        elif table_name == "Massachusetts":
            table_name = 'SDS_Massachusetts'
        else:
            table_name = 'NONE'
        from_crs = 'EPSG:4269'
        if table_name == 'NONE' or dataset == 'FARS':
            datasource_name = ["FARS"]
        else:
            datasource_name = ["SDS", "FARS"]

        # Geographic parameters:
        # state_ids = [i for i in range(40,56)]
        # state_ids = [6]
        # county_ids = [i for i in range(0,1000)]
        state_ids = [state_id]
        county_ids = [county_id]
        for state_id in state_ids:
            for county_id in county_ids:
                print("State ID:", state_id, "County ID:", county_id)

                # Get county boundary:
                county_bounds = get_county_boundaries_from_rds(
                    state_id, county_id)
                if type(county_bounds) == type(None) or len(county_bounds) == 0:
                    print(f"Skipped county: state {state_id}, county {county_id}")
                    continue
                print("Got county boundary")

                # Get graph of road network:
                G, graph_proj, nodes, edges = get_graph_from_county(
                    county_bounds)
                print("Loaded graph of road network")

                # Create bins, windows, and corridors:
                bins_by_edge, original_points_by_edge, points_granular_by_edge, points_by_edge, edges_by_id_tuple = create_bins(
                    edges)
                windows_by_edge = create_windows(
                    edges, bins_by_edge, points_by_edge, points_granular_by_edge)
                # TODO: Cleanup
                corridors_by_edge = create_corridors(
                    edges, points_granular_by_edge=points_granular_by_edge, points_by_edge=points_by_edge, bins_by_edge=bins_by_edge, windows_by_edge=windows_by_edge)
                print("Created bins, windows, and corridors")

                # Get crash data:
                fars_df = get_fars_crashes(state_id, county_id, start_year)
                if table_name != 'NONE':
                    sds_df = get_sds_crashes(
                        table_name, county_id, start_year, from_crs)
                    datasource = [sds_df, fars_df]
                else:
                    datasource = [fars_df]
                print("Loaded crash data")

                # Get Justice40 data:
                j40_bounds = get_census_tract_boundaries_from_rds(
                    state_id, county_id=county_id)

                # Set crash data source:
                for idx in range(len(datasource)):
                    crash_df = datasource[idx]
                    crash_data_source = datasource_name[idx]
                    print("\tCalculating for", crash_data_source)

                    # Find nearest edge to each crash:
                    nearest_edge_ids_tuple = get_nearest_edges_to_crashes(
                        crash_df, graph_proj)
                    print("\tFound nearest edge to each crash")

                    # Move crashes onto edges:
                    crash_df = move_crashes_to_edges(
                        crash_df, edges_by_id_tuple, nearest_edge_ids_tuple)
                    print("\tMoved crashes onto edges")

                    # Bin crashes (this is where crash weighting based on severity happens):
                    clear_crashes_from_bins(bins_by_edge)
                    put_crashes_into_bins(
                        crash_df, bins_by_edge, edges_by_id_tuple, nearest_edge_ids_tuple)
                    print("\tBinned crashes")

                    # Calculate unthresholded HIN:
                    road_length_unthr, features = calculate_unthresholded_hin(
                        bandwidth, corridors_by_edge)
                    print("\tGenerated HIN")

                    # Calculate thresholds:
                    features_by_thr, length_by_thr, num_crashes_by_thr = calculate_thresholds(
                        corridors_by_edge, original_points_by_edge, threshold_settings)
                    print("\tCalculated thresholds")

                    # Calculate statistics:
                    features_by_thr[0.0] = features
                    results = calculate_hin_statistics(
                        crash_df, edges, road_length_unthr, length_by_thr, num_crashes_by_thr, threshold_settings)
                    print("\tCalculated statistics")

                    # Run spatial join on J40 bounds:
                    joined_features_by_thr = calculate_joined_features(
                        features_by_thr, j40_bounds)
                    print("\tAdded IN_J40 column")

                    # Save to files and produce summary:
                    summary = save_feature_collections(
                        state_id, county_id, crash_data_source, threshold_settings, joined_features_by_thr, results)
                    print(summary)
                    print("\tSaved to files\n")
    except Exception as e:
        print(f"Something went psychiatrically concerning in State {state_id}, County {county_id}")
        print(e)



""" Main """

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Generate HIN for a specified state, county, and dataset.')
    parser.add_argument('--state_id', type=int, required=False,
                        default=6, help='State ID for HIN generation')
    parser.add_argument('--county_id', type=int, required=False,
                        default=1, help='County ID for HIN generation')
    parser.add_argument('--dataset', type=str, required=False, choices=[
                        'FARS', 'SDS'], default='FARS', help='Dataset to use (FARS or SDS)')
    parser.add_argument('--table_name', type=str, required=False, choices=[
                        'California', 'Massachusetts'], help='Table name for SDS dataset (California or Massachusetts)')

    args = parser.parse_args()
    generate_hin_single_county(
        args.state_id, args.county_id, args.dataset, args.table_name)
    # generate_hin()
