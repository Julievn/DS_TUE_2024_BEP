import csv
import fiona
import geopandas as gpd
import glob
import matplotlib
import matplotlib.pyplot as plt

import libpysal as lps
from libpysal.weights import Queen

from esda.moran import Moran_Local
from splot.esda import moran_scatterplot
from splot.esda import lisa_cluster

import os
import shutil 
import sys

# Read a csv file containing house prices for all cities in the Netherlands.
# Return a list of dictionaries. Each element is a dictionary. Each dictionary is a list of cities with house prices.
def readCsv(path_to_house_prices_file):
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

def getCitiesPolygonsWithHousePrices(path_to_shape_file, year, average_house_prices_per_year):    
    # kwargs in Python is a special syntax that allows you to pass a keyworded, variable-length argument dictionary to a function. 
    # It is short for "keyword arguments". When defining a function, you can use the ** in front of a parameter to indicate that 
    # it should accept any number of keyword arguments.
    def records(filename, usecols, year, average_house_prices_per_year, **kwargs):
        cities_with_polygons_and_not_prices_file_name_path = "Output/cities_with_polygons_and_not_prices_" + str(year) + ".txt" 
        if os.path.exists(cities_with_polygons_and_not_prices_file_name_path):
            os.remove(cities_with_polygons_and_not_prices_file_name_path)

        with fiona.open(filename, **kwargs) as source:
            for feature in source:
                f = {k: feature[k] for k in ['id', 'geometry']}
                f['properties'] = {k: feature['properties'][k] for k in usecols}
                city_name = f['properties']['GM_NAAM']

                # dictionary with key, value pair. For example, Aa en Hunze -> 213176
                if city_name in average_house_prices_per_year: # only display cities with housing prices
                    f['properties']['Year'] = year
                    f['properties']['Average_House_Price'] = average_house_prices_per_year[city_name]
                    yield f
                else:
                    print("SKIp city '%s' as DOES NOT have house price" % city_name)
                    print (f)
                    open_file = open(cities_with_polygons_and_not_prices_file_name_path, "a")
                    open_file.write(city_name  + " " + f['id']  + " " + f['properties']['GM_CODE'])
                    open_file.write("\n")
                    open_file.close()

    cities_polygons = gpd.GeoDataFrame.from_features(records(path_to_shape_file, ['GM_CODE', 'H2O', 'OAD', 'STED', 'BEV_DICHTH', 'GM_NAAM'], year, average_house_prices_per_year))
    return cities_polygons

def exitProgram():
    print("Exiting the program...")
    sys.exit(1)

def showCitiesInMap(cities_polygons_with_house_prices, output_folder, year):
    print(type(cities_polygons_with_house_prices))
    print(cities_polygons_with_house_prices.columns.tolist())

    # Print first 10 cities
    print(cities_polygons_with_house_prices.head(10))

    cities_polygons_with_house_prices.plot()

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

    save_plot_file_name = "cities_polygon_" + str(year)
    plt.savefig(output_folder + '/' + save_plot_file_name)

    cities_polygons_with_house_prices.boundary.plot()
    save_plot_file_name = "cities_polygon_boundaries_" + str(year) 
    #plt.show()
    plt.savefig(output_folder + '/' + save_plot_file_name)

def calculateMoranI(cities_polygons_with_house_prices, output_folder, year):
     # Calculate weight matrix from the GeoDataFrame using Queen approach
    queen_weight_matrix = Queen.from_dataframe(cities_polygons_with_house_prices)

    print(type(cities_polygons_with_house_prices))
    print(type(cities_polygons_with_house_prices['GM_NAAM'].values))
    print(cities_polygons_with_house_prices['GM_NAAM'].values)

    # <class 'pandas.core.series.Series'> when used inside this function.
    # Outside this function is numpy array    
    print(type(cities_polygons_with_house_prices['Average_House_Price']))
    print(cities_polygons_with_house_prices['Average_House_Price'].values)

    # house_prices = cities_polygons_with_house_prices['Average_House_Price'].to_numpy()
    #print(type(house_prices))

    moran_loc = Moran_Local(cities_polygons_with_house_prices['Average_House_Price'].values, queen_weight_matrix)
    print("Moran spatial autocorrelation between cities")
    print(moran_loc)

    print("Moran EI value{}!".format(moran_loc.EI))

    fig, ax = moran_scatterplot(moran_loc)
    ax.set_xlabel('Cities')
    ax.set_ylabel('Spatial Lag of Cities')
    #plt.show()

    save_plot_file_name = "moran_scatterplot_" + str(year)
    plt.savefig(output_folder + '/' + save_plot_file_name)

    # Let's now visualize the areas we found to be significant on a map:
    # hotspot cold spot
    lisa_cluster(moran_loc, cities_polygons_with_house_prices, p=0.05, figsize = (9,9))
    save_plot_file_name = "moran_hotspot_" + str(year)
    plt.savefig(output_folder + '/' + save_plot_file_name)
    #plt.show()

def main():
    print("\n----Correlation and Similarities for spatiotemporal data - Housing Prices in the Netherlands-----")
    print("**************************************************************************************************")
    
    # args is a list of the command line args
    args = sys.argv[1:]
    
    if len(args) <= 0 or args[0] != '-house_price_csv' or args[2] != '-path_to_shape_file':
        print("Please use -house_price_csv and -path_to_shape_file as parameters.")
        exitProgram()

    print("Running program {} with value {}; {} with value {} ".format(args[0], args[1], args[2], args[3]))
    path_to_house_prices_csv_file = args[1]
    print("Loading ", path_to_house_prices_csv_file)
    
    average_house_prices_years = readCsv(path_to_house_prices_csv_file)
    print("Successfully loaded ", path_to_house_prices_csv_file)

    # Prepare housing price data per year with geographical boundaries for cities 
    path_to_shape_file = args[3] 
    start_year = 2013
    for year_idx in range(11):    
        average_house_prices_per_year = average_house_prices_years[year_idx]
        year = start_year + year_idx
        print("--------{}".format(year))

        # Only cities with housing prices 
        cities_polygons_with_house_prices = getCitiesPolygonsWithHousePrices(path_to_shape_file, year, average_house_prices_per_year)
        print("Successfully loaded ", path_to_shape_file)

        # Show cities in map. Only cities with housing prices will be shown.
        output_folder = "Output/" + str(year)
        showCitiesInMap(cities_polygons_with_house_prices, output_folder, year)

        # Main part: calculate Moran I value
        calculateMoranI(cities_polygons_with_house_prices, output_folder, year)
      
if __name__ == "__main__":
    main()    