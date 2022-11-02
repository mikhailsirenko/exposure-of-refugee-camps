import json
import pandas as pd
import geopandas as gpd
from tqdm import tqdm

def getFeatures(gdf):
    """Function to parse features from GeoDataFrame in such a manner that rasterio wants them"""
    return [json.loads(gdf.to_json())['features'][0]['geometry']]

def convert_to_geodataframe(ds):
    # Get time
    time = ds.time.values

    # Get unique grid cells
    lat = ds.latitude.values
    lon = ds.longitude.values
    pairs = []
    for i in lat:
        for j in lon:
            pairs.append((i, j))

    # Prepare resulting data frame
    df = pd.DataFrame(index=[str(pair) for pair in pairs], columns=time)

    # Fill the data frame
    for i in tqdm(pairs):
        for j in time:
            df.loc[str(i), j] = float(ds.t2m.sel(latitude=i[0], longitude=i[1], time=j).values)

    # Convert Kelvin to Celsius
    df = df.apply(lambda x: x - 273.15)
    x = [i.split(',')[0].split('(')[1] for i in df.index]
    y = [i.split(',')[1].split(')')[0][1:] for i in df.index]
    gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(y, x))
    return gdf