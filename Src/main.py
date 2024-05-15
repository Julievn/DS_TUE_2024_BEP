import csv
import fiona
import geopandas as gpd
import glob
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd

import libpysal as lps
from libpysal.weights import Queen


from mpl_toolkits.axes_grid1 import make_axes_locatable

from shapely.geometry import Point

from moran_calculation import *

import os
import shutil 
import sys

# Read a csv file containing house prices for all cities in the Netherlands.
# Return a list of dictionaries. Each element is a dictionary. Each dictionary is a list of cities with house prices.
def readCsvHousePrice(path_to_house_prices_file):
    # create a list of dictionaries. Each element is a dictionary. Each dictionary is a list of cities with house prices.
    average_house_prices_years = [] 
    start_year = 2013

    special_municipality_mapping = {"'s-Gravenhage (municipality)": "'s-Gravenhage",
                                    "Groningen (municipality)": "Groningen",
                                    "Utrecht (municipality)" : "Utrecht",
                                    "Laren (NH.)" : "Laren",
                                    "Rijswijk (ZH.)" : "Rijswijk",
                                    "Beek (L.)" : "Beek",
                                    "Stein (L.)" : "Stein"}

    with open(path_to_house_prices_file, newline='', encoding='utf-8') as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=';', quotechar='|')
        next(csv_reader, None)  # skip the headers
        for row in csv_reader:     
            if ((len(row) == 3) and (row[2].isdigit())):
                current_year = int(row[0].replace('"', ''))
                current_city = row[1].replace('"', '')
                current_price = int(row[2])

                # Some names in the geographical file and the housing price file are not the same. So we need to do this mapping.
                if current_city in special_municipality_mapping:
                    current_city = special_municipality_mapping[current_city]

                year_idx = current_year -start_year
                if (len(average_house_prices_years) == year_idx):
                    average_house_prices_per_year = {current_city: current_price}
                    average_house_prices_years.append(average_house_prices_per_year)
                else:
                    average_house_prices_per_year = average_house_prices_years[current_year -start_year]
                    average_house_prices_per_year[current_city] = current_price
    return average_house_prices_years

# Read a csv file containing immigration for all cities in the Netherlands.
# Return a list of dictionaries. Each element is a dictionary. Each dictionary is a list of cities with immigration.
def readCsvImmigration(path_to_immigration_file):
    # create a list of dictionaries. Each element is a dictionary. Each dictionary is a list of cities with house prices.
    immigration_all_years = [] 
    start_year = 2013

    special_municipality_mapping = {"'s-Gravenhage (municipality)": "'s-Gravenhage",
                                    "Groningen (municipality)": "Groningen",
                                    "Utrecht (municipality)" : "Utrecht",
                                    "Laren (NH.)" : "Laren",
                                    "Rijswijk (ZH.)" : "Rijswijk",
                                    "Beek (L.)" : "Beek",
                                    "Stein (L.)" : "Stein",
                                    "Middelburg (Z.)" : "Middelburg"}

    with open(path_to_immigration_file, newline='', encoding='utf-8') as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=';', quotechar='|')
        next(csv_reader, None)  # skip the headers
        for row in csv_reader:     
            if ((len(row) == 4) and (row[3].isdigit())):
                current_year = int(row[1].replace('"', ''))
                current_city = row[2].replace('"', '')
                current_immigration = int(row[3])

                # Some names in the geographical file and the housing price file are not the same. So we need to do this mapping.
                if current_city in special_municipality_mapping:
                    current_city = special_municipality_mapping[current_city]

                year_idx = current_year -start_year
                if (len(immigration_all_years) == year_idx):
                    immigration_per_year = {current_city: current_immigration}
                    immigration_all_years.append(immigration_per_year)
                else:
                    immigration_per_year = immigration_all_years[current_year -start_year]
                    immigration_per_year[current_city] = current_immigration
    return immigration_all_years

def CreateOutputFolderIfNeeded(output_folder):
    if os.path.exists(output_folder):
        print("Directory '%s' exists. So removing its existing contents" % output_folder)
        files = glob.glob(output_folder + '/*')
        for f in files:
            print (f)
            os.remove(f)
 
    if not os.path.exists(output_folder):
        try:
            os.makedirs(output_folder)
            print("Directory '%s' created" % output_folder)
        except OSError as error:
            print("Directory '%s' can not be created" % output_folder)

def getCitiesPolygonsWithData(path_to_shape_file, year, data_per_year, data_name, output_folder):    
    # kwargs in Python is a special syntax that allows you to pass a keyworded, variable-length argument dictionary to a function. 
    # It is short for "keyword arguments". When defining a function, you can use the ** in front of a parameter to indicate that 
    # it should accept any number of keyword arguments.
    def records(filename, usecols, year, data_per_year, **kwargs):
        cities_with_polygons_and_not_data_file_name_path = output_folder + "/cities_with_polygons_and_not_" + data_name + "_" + str(year) + ".txt" 
        with fiona.open(filename, **kwargs) as source:
            for feature in source:
                f = {k: feature[k] for k in ['id', 'geometry']}
                f['properties'] = {k: feature['properties'][k] for k in usecols}
                city_name = f['properties']['GM_NAAM']

                # dictionary with key, value pair. For example, Aa en Hunze -> 213176
                if city_name in data_per_year: # only display cities with housing prices
                    f['properties']['Year'] = year
                    f['properties'][data_name] = data_per_year[city_name]
                    yield f
                else:
                    print("SKIp city '%s' as DOES NOT have data" % city_name)
                    print (f)
                    open_file = open(cities_with_polygons_and_not_data_file_name_path, "a")
                    open_file.write(city_name  + " " + f['id']  + " " + f['properties']['GM_CODE'])
                    open_file.write("\n")
                    open_file.close()

    cities_polygons = gpd.GeoDataFrame.from_features(records(path_to_shape_file, ['GM_CODE', 'H2O', 'OAD', 'STED', 'BEV_DICHTH', 'GM_NAAM'], year, data_per_year))
    print (cities_polygons.crs)
    return cities_polygons

def exitProgram():
    print("Exiting the program...")
    sys.exit(1)

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

def exportDataToFile(data, data_name, file_path):
    field_names = ['Regions', data_name]
    with open(file_path, 'w') as csvfile:
        writer = csv.writer(csvfile)

        # writing the fields
        writer.writerow(field_names)

        # writing the data rows
        print(type(data))
        writer.writerows(data.items())

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
    args = sys.argv[1:]
    
    if len(args) <= 0 or args[0] != '-house_price_csv' or args[2] != '-path_to_shape_file' or args[4] != '-immigration_csv':
        print("Please use -house_price_csv and -path_to_shape_file as parameters.")
        exitProgram()

    print("Running program {} with value {}; {} with value {} ".format(args[0], args[1], args[2], args[3]))

    # Processing house prices
    path_to_house_prices_csv_file = args[1]
    path_to_shape_file = args[3] 
    processHousePrices(path_to_house_prices_csv_file, path_to_shape_file)

    # Processing immigration
    path_to_immigration_csv_file = args[5]
    processImmigration(path_to_immigration_csv_file, path_to_shape_file)
     
if __name__ == "__main__":
    main()    