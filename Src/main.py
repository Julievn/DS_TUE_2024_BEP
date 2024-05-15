
import geopandas as gpd
import matplotlib
import matplotlib.pyplot as plt
import os
import pandas as pd
import shutil 

import libpysal as lps
from libpysal.weights import Queen

from mpl_toolkits.axes_grid1 import make_axes_locatable

from shapely.geometry import Point

# local libraries
from house_prices import *
from moran_calculation import *
from utility import *

def processImmigration(path_to_immigration_csv_file, path_to_shape_file):
    # Load immigration from csv file
    print("Loading ", path_to_immigration_csv_file)
    immigration_all_years = readCsvImmigration(path_to_immigration_csv_file)
    print("Successfully loaded ", path_to_immigration_csv_file)

    start_year = 2013
    for year_idx in range(1):    
        immigration_per_year = immigration_all_years[year_idx]
        year = start_year + year_idx
        print("--------{}".format(year))

        # Prepare output immigration folder
        output_immigration_folder = "Output/Immigration/" + str(year)
        CreateOutputFolderIfNeeded(output_immigration_folder)

        # Keep only cities with immigration data
        data_name = "Immigration"
        cities_polygons_with_immigration = getCitiesPolygonsWithData(path_to_shape_file, year, immigration_per_year, data_name, output_immigration_folder)
        print("Successfully loaded ", path_to_shape_file)

        # Show cities in map. Only cities with housing prices will be shown.
        showCitiesInMap(cities_polygons_with_immigration, data_name, output_immigration_folder, year)

         # Main part: calculate Global Moran I value
        calculateGlobalMoranI(cities_polygons_with_immigration, data_name, output_immigration_folder, year)

         # Main part: calculate local Moran I value
        calculateLocalMoranI(cities_polygons_with_immigration, data_name, output_immigration_folder, year)

def main():
    print("\n----Correlation and Similarities for spatiotemporal data - Housing Prices in the Netherlands-----")
    print("**************************************************************************************************")
    
    # args is a list of the command line args
    args = getListOfArguments()

    # Processing house prices
    path_to_house_prices_csv_file = args[1]
    path_to_shape_file = args[3] 
    processHousePrices(path_to_house_prices_csv_file, path_to_shape_file)

    # Processing immigration
    path_to_immigration_csv_file = args[5]
    processImmigration(path_to_immigration_csv_file, path_to_shape_file)
     
if __name__ == "__main__":
    main()    