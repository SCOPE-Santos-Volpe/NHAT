"""Categorizes each row of a dataframe into categories as defined by shapefiles.

The main interface function is categorize_df_to_shapefiles()
"""

from shapely.geometry import shape, Point
import pandas as pd
import utils
from collections.abc import Iterable, Callable


def build_categories_dict(shapes: Iterable, category_id_func: Callable, category_geometry_func: Callable) -> dict:
    """Takes an iterable of shapes and creates a dictionary of categories

    Args:
        shapes: an iterable of geojson objects
        category_id_func: a callable that takes in a shape (a single item from the iterable `shapes`) and a number, and returns a string that identifies that category
        category_geometry_func: a callable that takes in a shape (a single item from the iterable `shapes`) and a number, and returns the geometry of that category

    Returns:
        a dictionary with the keys being the return of category_func for each item in shapes, and the values being the return of coords_func for each item in shapes
    """

    # Start with an empty dict
    categories_dict = {}

    # For each shape
    for i in range(len(shapes)):
        category_id = category_id_func(shapes, i) # get category id
        geometry = shape(category_geometry_func(shapes, i)) # get geometry of this category
        categories_dict[category_id] = geometry # set this value in the dictionary

    return categories_dict


def categorize_df_to_shapefiles(df: pd.DataFrame, lat_column: str, lon_column: str, shapes: Iterable, 
category_col_name: str, category_id_func: Callable, category_geometry_func: Callable) -> pd.DataFrame:
    """Categorizes each row of a dataframe into categories defined by shapefiles.

    Args:
        df: the dataframe to be categorized by row, will be returned with an additional column called `category_col_name`
        lat_column: the name of the latitude column in df
        lon_column: the name of the longitude column in df
        shapes: an iterable of geojson objects
        category_col_name: the name for the column that will be added to `df`
        category_id_func: a callable that takes in a shape (a single item from the iterable `shapes`) and a number, and returns a string that identifies that category
        category_geometry_func: a callable that takes in a shape (a single item from the iterable `shapes`) and a number, and returns the geometry of that category

    Returns:
        a `pd.DataFrame` which is the argument `df` with an added column called `category_col_name`. The value of this column is the output of `category_func` for that category

    """

    categories_dict = build_categories_dict(shapes, category_id_func = category_id_func, category_geometry_func=category_geometry_func)

    # Create a new column called point, with a shapely.geometry.Point made from lon_column and lat_column
    df['point'] = df.apply(lambda x: Point(x[lon_column], x[lat_column]), axis=1)

    # Create a new columnm with the name defined by `category_col_name` argument, fill with None to start
    df[category_col_name] = None
    
    # For each category in the dictionary
    for key in categories_dict.keys():
        category_geometry = categories_dict[key] # the geometry of this category is the dictionary value
        df['point_in_category'] = df.apply(lambda x: category_geometry.contains(x['point']), axis=1) 
        # New column with boolean value of if this category's geometry contains the point
        df[category_col_name] = df.apply(lambda x: key if x['point_in_category'] else x[category_col_name], axis=1) 
        # For each row, if this category's geometry intersects with the point, then replace the value of df[category_col_name] with the category name

    df = df.drop(columns=['point','point_in_category']) # Get rid of temp columns

    return df


def demo():
    """Demonstration to show one example of calling the `categorize_df_to_shapefiles` function.
    """

    # fars = utils.load_df_from_csv(path='FARS/FARS CSVs/ACCIDENT_2020.CSV', index_col=None, encoding_errors='ignore', low_memory=False)
    fars = utils.load_df_from_csv(path='combined_FARS.csv', low_memory = False)
    states_dict = utils.load_geojson(path='Shapefiles/gz_2010_us_040_00_500k.geojson')
    #Load FARS and states JSON files

    fars_categorized = categorize_df_to_shapefiles(
        df = fars, 
        lat_column = 'LATITUDE',
        lon_column = 'LONGITUD',
        shapes = states_dict['features'], #what to iterate over to get each category
        category_col_name = 'State', #column name to categorize into
        category_id_func = lambda s, i: s[i]['properties']['NAME'], #function that takes each shape in shapes argument and an i, must return a string to identify each category
        category_geometry_func = lambda s, i: s[i]['geometry'] #function that takes each shape in shapes argument and an i, must return the geometry of that category
    )

    utils.write_dataframe_to_file(fars_categorized, filename="combined_FARS_categorized.csv")

if __name__=="__main__":
    demo()
