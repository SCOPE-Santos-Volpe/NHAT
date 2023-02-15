import osmnx as ox
from scipy.interpolate import interp1d
import numpy as np
np.seterr(divide='ignore', invalid='ignore')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import pandas as pd
import scipy.stats as st
from shapely.geometry import Polygon, LineString, Point
import geopandas as gpd
import glob
import os
import combine_FARS_datasets
import combine_SDS_datasets
import multiprocessing as mp
import copy

# with mp.Pool() as pool: # have the pool map each tuple onto calculate_s arguments
#         # Starmap is just unpacking the tuple into multiple arguments
#         # This will complete the operation with an optimal number of pool workers,
#         # making use of all CPU cores.
#         output_rows = pool.starmap(simulate_one, params)

class Batch():

    def __init__(self, area):

        self.area = area  #buffer area
        self.fars_gdf = [] #points within buffer
        self.minx = 0
        self.miny = 0
        self.maxx = 0
        self.maxy = 0
        self.f =0
        self.xx = 0
        self.yy = 0
    def add_point(self, point):
        self.fars_gdf.append(point)
    def calc_KDE(self):
        # self.minx, self.miny, self.maxx, self.maxy = self.area.bounds
        # dx = self.maxx-self.minx
        # dy = self.maxy-self.miny
        # self.minx = self.minx-(dx/2)
        # self.maxx = self.maxx+(dx/2)
        # self.miny = self.miny-(dx/2)
        # self.maxy = self.maxy+(dx/2)
        self.xx, self.yy = np.mgrid[self.minx:self.maxx:100j, self.miny:self.maxy:100j]
        positions = np.vstack([self.xx.ravel(), self.yy.ravel()])
        list_ver = []
        for i,j in enumerate(self.fars_gdf):
            list_ver.append([j.x, j.y])
        T_fars = np.array(list_ver).transpose()
        # print(T_fars.shape)
        # print(np.linalg.eigvalsh(T_fars))

        kernel = st.gaussian_kde(T_fars, bw_method="silverman")
        self.f = np.reshape(kernel(positions).T, self.xx.shape)
        self.f = np.divide(self.f,np.nanmax(self.f))
        return self.f, self.minx, self.miny, self.maxx, self.maxy

def get_graph_from_place(place='Alameda', buffer_m = 500):
    """Get roads and buffers from the given place

    Args:
        place: A string defining what place to get
        buffer_m: An integer defining how many meters of buffer should be used
    Returns:
        roads: (something) that holds all the roads
        buffers: (something) of all the buffers
    """
    # Get a graph from the place in args
    g = ox.graph_from_place('Alameda', network_type='drive', buffer_dist=10)
    # Project the graph (idk what that means)
    graph_proj = ox.project_graph(g, to_crs="EPSG:2805")
    # fig, ax = ox.plot_graph(graph_proj)

    # Convert graphs into geopandas dataframes
    nodes, edges = ox.graph_to_gdfs(graph_proj)

    # Get the roads, which are the edges of the geometry
    roads = edges["geometry"]

    # Calculate 500m buffers for each road
    buffers = roads.buffer(buffer_m)

    return roads, buffers


def get_fars_gpd(buffers, path='FARS/FARS CSVs'):
    """Calculate a geopandas dataframe of each FARS point

    Args:
        buffers: a (something) of all the buffers
        path: the path to look for the FARS data
    Returns:
        A geopandas geoseries of each FARS point
    """

    # Get a dataframe of all FARS data combined
    fars_df_all = combine_FARS_datasets.combine_FARS_datasets(path)
    # FARS_GDF = gpd.GeoSeries(fars_df_all.loc[:, ["lon", "lat"]].apply(Point, axis=1), crs = "epsg:4326")

    # Convert each FARS point into a point object
    fars_gdf = gpd.GeoSeries(fars_df_all.loc[:, ["LONGITUD", "LATITUDE"]].apply(Point, axis=1), crs = "epsg:4326")
    fars_gdf = fars_gdf.to_crs("EPSG:2805")

    # Get the bounds of this city's area (total bounds of all buffers)
    minx, miny, maxx, maxy = buffers.total_bounds
    ltc = Point(minx, maxy)
    rtc = Point(maxx, maxy)
    lbc = Point(minx, miny)
    rbc = Point(maxx, miny)
    box = Polygon([ltc,rtc,rbc,lbc])

    # List for all fars points within this area
    fars_holder = []

    # For each point, if within the box, append to the fars holder
    for pt in fars_gdf:
        if box.contains(pt):
            fars_holder.append(pt)

    # Make a geopandas geoseries of fars points
    fars_gpd = gpd.GeoSeries(fars_holder)

    return fars_gpd

def get_sds_gpd(buffers,path='SDS/Data/'):
    sds_dict = combine_SDS_datasets.combine_SDS_datasets(path)
    lst = []
    for key in sds_dict.keys():
        sds_df = sds_dict[key]
        print(sds_df)
        sds_df['lat'] = pd.to_numeric(sds_df['lat'], errors='coerce')
        sds_df['lon'] = pd.to_numeric(sds_df['lon'], errors='coerce')
        sds_df = sds_df.dropna(subset=['lat','lon'])
        lst.append(sds_df)
    points_df = pd.concat(lst, axis=0, ignore_index=True)
    points_gpd = gpd.GeoSeries(points_df.loc[:, ['lon', 'lat']].apply(Point, axis=1), crs = "epsg:4326")
    points_gpd = points_gpd.to_crs("EPSG:2805")

    # Get the bounds of this city's area (total bounds of all buffers)
    minx, miny, maxx, maxy = buffers.total_bounds
    ltc = Point(minx, maxy)
    rtc = Point(maxx, maxy)
    lbc = Point(minx, miny)
    rbc = Point(maxx, miny)
    box = Polygon([ltc,rtc,rbc,lbc])

    # List for all sds points within this area
    sds_holder = []

    # For each point, if within the box, append to the sds holder
    for pt in points_gpd:
        if box.contains(pt):
            sds_holder.append(pt)

    # Make a geopandas geoseries of sds points
    points_gpd = gpd.GeoSeries(sds_holder)

    return points_gpd

def batch_helper(area, buffers, points_gpd):
    batch = Batch(area) # Create a Batch

    # This sets the bounds of the KDE plot to the entire visualization bounds.
    batch.minx, batch.miny, batch.maxx, batch.maxy = buffers.total_bounds

    # For each point, if within the area, add to the batch
    for point in points_gpd:
        if(point.within(batch.area)):
            batch.add_point(point)

    if(len(batch.fars_gdf) >= 3):
        batch.calc_KDE()
        if(np.nanmax(batch.f) is np.nan):
            return None
        else:
            return batch

    return None



def make_batches(buffers, points_gpd):
    """Add all points within a given buffer to that Batch, for every Batch

    Args:
        buffers: a (something) of (somethings), with one buffer for each road segment
        points_gpd: a list of points to be checked against the buffer areas
    Returns:
        A list of Batch classes that have 3+ points
    """
    # minx, miny, maxx, maxy = buffers.total_bounds

    # Variable to store all batches
    # batches = []

    params = [(a,buffers,points_gpd) for _, a in enumerate(buffers)]

    with mp.Pool() as pool: # have the pool map each tuple onto calculate_s arguments
        # Starmap is just unpacking the tuple into multiple arguments
        # This will complete the operation with an optimal number of pool workers,
        # making use of all CPU cores.
        output = pool.starmap(batch_helper, params)
    pool.close()

    # for _, area in enumerate(buffers): # For each buffer
    #     batch = Batch(area) # Create a Batch

    #     # This sets the bounds of the KDE plot to the entire visualization bounds.
    #     batch.minx, batch.miny, batch.maxx, batch.maxy = buffers.total_bounds

    #     # For each point, if within the area, add to the batch
    #     for point in points_gpd:
    #         if(point.within(batch.area)):
    #             batch.add_point(point)

    #     # If there are enough points to calculate a KDE, then calculate KDE and add to batches
    #     if(len(batch.fars_gdf) >= 3):
    #         batch.calc_KDE()
    #         batches.append(batch)

    batches = []
    for b in output:
        if (b is None):
            pass
        else:
            batches.append(b)
    return copy.deepcopy(batches)


def transparent_cmap(N=255):
    """Create a transparent colormap

    Args:
        N: an integer specifying how many levels to have in the cmap
    Returns:
        A colormap object
    """
    # "Copy colormap and set alpha values"

    # mycmap = plt.cm.Blues
    # mycmap._init()
    # mycmap._lut[0,:] = [1,1,1,0]
    # mycmap._lut[1:-3,0] = np.linspace(1, 0, N) # R
    # mycmap._lut[1:-3,1] = np.linspace(1, 0, N) # G
    # mycmap._lut[1:-3,2] = np.linspace(1, 1, N) # B
    # mycmap._lut[1:-3,3] = np.linspace(0, 1, N) # A
    # mycmap._lut[-3:,:] = [1,0,0,1]
    # I don't remember why this matters tbh, it was a StackOverflow article fix
    # return mycmap

    "Copy colormap and set alpha values"

    mycmap = plt.cm.Blues
    mycmap._init()
    mycmap._lut[:,-1] = np.linspace(0.0, 0.9,N+4)
    return mycmap

# def transparent_cmap():
#     """https://stackoverflow.com/questions/51601272/python-matplotlib-heatmap-colorbar-from-transparent
#     """
#     ncolors = 256
#     color_array = plt.get_cmap('gist_rainbow')(range(ncolors))

#     # change alpha values
#     color_array[:,-1] = np.linspace(1.0,0.0,ncolors)

#     # create a colormap object
#     map_object = LinearSegmentedColormap.from_list(name='rainbow_alpha',colors=color_array)

#     # register this new colormap with matplotlib
#     # plt.register_cmap(cmap=map_object)
#     return map_object

#     # # show some example data
#     # f,ax = plt.subplots()
#     # h = ax.imshow(np.random.rand(100,100),cmap='rainbow_alpha')
#     # plt.colorbar(mappable=h)

def plot_hin(batches, roads, points_gpd):
    """Plot the HIN network contour map

    Args:
        batches: a list of Batch objects
        roads: a (something) of (something), which contains every road in the area
        points_gpd: a (something) of every data point
    Returns:
        none
    """
    print("started plot")

    # Make transparent colormap for the contourf plots
    # mycmap = transparent_cmap()
    plt.register_cmap(cmap=transparent_cmap(),name='mira')

    # Make new figure. Doesn't need to be 8x8, that was just for .ipynb troubleshooting
    fig = plt.figure(figsize=(8,8))

    # Get the axes
    ax = fig.gca()
    print("point 1")

    # Plot the roads
    roads.plot(ax=ax,color='Red',linewidth=0.25,alpha=0.5,zorder=5)
    # roads.plot(ax=ax,color='Red')
    print("point 2")

    # This is leftover code from when I was trying to add all the f values
    # xx = batches[0].xx
    # yy = batches[0].yy

    # Make a new array of f values
    # fs = np.zeros_like(xx, dtype=np.float_)
    # np.add()

    # Add each f value to fs.
    # for j,i in enumerate(batches):
        # np.add(fs, i.f, out=fs)
        # print(i.f[0])
        # print(type(i.f[0]))

    # Draw the contour plot for each batch with enough points
    for j,i in enumerate(batches):
        print(i.f,np.nanmax(i.f))
        ax.contourf(i.xx, i.yy, i.f, cmap = 'mira', levels = np.linspace(start=0,stop=np.nanmax(i.f),num=100),algorithm='threaded')

    # # If you replace:

    # plt.contourf(xx, yy, f, cmap=cmap, alpha=0.5)

    # # with:

    # step = 0.02
    # m = np.amax(f)
    # levels = np.arange(0.0, m, step) + step
    # plt.contourf(xx, yy, f, levels, cmap=cmap, alpha=0.5)



    # This is where I was trying to use the fs to do only one contourf call
    # ax.contourf(xx,yy,fs,cmap=mycmap,zorder=0)
    # print(fs)
    print("point 3")

    # Plot each FARS point
    points_gpd.plot(ax=ax, color="Black", markersize=10, zorder=10)
    print("done plotting")
    plt.show()

def main():
    """Run the HIN generation and display code

    Args:
        none
    Returns:
        none
    """
    print("yes you did actually start the program")

    # Get roads and buffers from a given place
    roads, buffers = get_graph_from_place()

    # Get each FARS point
    fars = get_fars_gpd(buffers)
    sds = get_sds_gpd(buffers)
    points_gpd = pd.concat([fars,sds],axis=0,ignore_index=True)
    # points_gpd = fars
    print("making batches")

    # Make batches from each buffer, categorize points
    batches = make_batches(buffers, points_gpd)
    print("done batching")

    # Plot the HIN map
    plot_hin(batches, roads, points_gpd)

if __name__ == "__main__":
    main()