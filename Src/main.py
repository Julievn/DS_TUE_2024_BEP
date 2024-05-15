
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
from moran_calculation import *
from utility import *

def showCitiesInMap(cities_polygons_with_data, data_name, output_folder, year):
    print(type(cities_polygons_with_data))
    print(cities_polygons_with_data.columns.tolist())

    # Print first 2 cities
    print(cities_polygons_with_data.head(2))
    print(cities_polygons_with_data.crs)

    important_cities_df = pd.DataFrame(
        {
            "City": ["Amsterdam"],
            "Latitude": [487197.871781],  
            "Longitude": [121488.689806] 
        }
    )

    important_cities_gdf = gpd.GeoDataFrame(
        important_cities_df, geometry=gpd.points_from_xy(important_cities_df.Longitude, important_cities_df.Latitude), crs="EPSG:28992" #Amersfoort coordinate system
    )

    # We can now plot our ``GeoDataFrame``.
    base = cities_polygons_with_data.plot()
    important_cities_gdf.plot(ax=base, color="red")

    save_plot_file_name = "cities_polygon_" + str(year)
    plt.savefig(output_folder + '/' + save_plot_file_name)

    ax = cities_polygons_with_data.boundary.plot()
    ax.set_axis_off()
    save_plot_file_name = "cities_polygon_boundaries_" + str(year) 
    #plt.show()
    plt.savefig(output_folder + '/' + save_plot_file_name)

    # Plot by data
    fig, ax = plt.subplots(1, 1)
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("bottom", size="5%", pad=0.1)
    base = cities_polygons_with_data.plot(
        column=data_name, 
        ax=ax,
        legend=True,
        cax=cax,
        legend_kwds={"label": "House prices in " + str(year), "orientation": "horizontal"}
    )

    important_cities_gdf.plot(ax=base, color="red")

    save_plot_file_name = "choropleth_map_" + data_name + "_" + str(year) 
    plt.savefig(output_folder + '/' + save_plot_file_name)

def processHousePrices(path_to_house_prices_csv_file, path_to_shape_file):
    # Load house prices from csv file
    print("Loading ", path_to_house_prices_csv_file)
    house_prices_years = readCsvHousePrice(path_to_house_prices_csv_file)
    print("Successfully loaded ", path_to_house_prices_csv_file)

    start_year = 2013
    for year_idx in range(1):    
        house_prices_per_year = house_prices_years[year_idx]
        year = start_year + year_idx
        print("--------{}".format(year))

        # Prepare output housing price folder
        output_housing_price_folder = "Output/Housing_Prices/" + str(year)
        data_name = "House_Price"
        CreateOutputFolderIfNeeded(output_housing_price_folder)

        # Export data to file
        exportDataToFile(house_prices_per_year, data_name, output_housing_price_folder + "/" + data_name + "_" + str(year))

        # Export cities with most expensive house prices
        most_expensive_cities = {key:val for key, val in house_prices_per_year.items() if val >= 500000}
        exportDataToFile(most_expensive_cities, data_name, output_housing_price_folder + "/most_expensive_" + data_name + "_" + str(year))

        # Keep only cities with housing prices 
        cities_polygons_with_house_prices = getCitiesPolygonsWithData(path_to_shape_file, year, house_prices_per_year, data_name, output_housing_price_folder)
        print("Successfully loaded ", path_to_shape_file)

        # Show cities in map. Only cities with housing prices will be shown.
        showCitiesInMap(cities_polygons_with_house_prices, data_name, output_housing_price_folder, year)

        # Main part: calculate Global Moran I value
        calculateGlobalMoranI(cities_polygons_with_house_prices, data_name, output_housing_price_folder, year)

        # Main part: calculate local Moran I value
        calculateLocalMoranI(cities_polygons_with_house_prices, data_name, output_housing_price_folder, year)

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