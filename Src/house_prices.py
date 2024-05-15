import csv

# local libraries
from map_visualization import *
from moran_calculation import *
from utility import *

# Read a csv file containing house prices for all cities in the Netherlands.
# Return a list of dictionaries. Each element is a dictionary. Each dictionary is a list of cities with house prices.
def readCsvHousePrice(path_to_house_prices_file):
    # create a list of dictionaries. Each element is a dictionary. Each dictionary is a list of cities with house prices.
    average_house_prices_years = [] 
    start_year = 2013

    special_municipality_mapping = {"'s-Gravenhage (municipality)": "'s-Gravenhage",
                                    "Groningen (municipality)": "Gronfingen",
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

def processHousePrices(path_to_house_prices_csv_file, path_to_shape_file):
    # Load house prices from csv file
    print("Loading ", path_to_house_prices_csv_file)
    house_prices_years = readCsvHousePrice(path_to_house_prices_csv_file)
    print("Successfully loaded ", path_to_house_prices_csv_file)

    output_housing_price_folder = "Output/Housing_Prices/"
    CreateOutputFolderIfNeeded(output_housing_price_folder)

    start_year = 2013
    for year_idx in range(1):    
        house_prices_per_year = house_prices_years[year_idx]
        year = start_year + year_idx
        print("--------{}".format(year))

        # Prepare output housing price folder
        output_housing_price_folder_per_year = "Output/Housing_Prices/" + str(year)
        CreateOutputFolderIfNeeded(output_housing_price_folder_per_year)

        # Export data (i.e house price per municipality) to file
        data_name = "House_Price"
        field_names = ['Regions', data_name]
        exportDataToFile(house_prices_per_year, field_names, output_housing_price_folder_per_year + "/" + data_name + "_" + str(year))

        # Export municipalities with most expensive house prices
        most_expensive_cities = {key:val for key, val in house_prices_per_year.items() if val >= 500000}
        exportDataToFile(most_expensive_cities, field_names, output_housing_price_folder_per_year + "/most_expensive_" + data_name + "_" + str(year))

        # Keep only cities with housing prices 
        cities_polygons_with_house_prices = getCitiesPolygonsWithData(path_to_shape_file, year, house_prices_per_year, data_name, output_housing_price_folder)
        print("Successfully loaded ", path_to_shape_file)

        # Show cities in map. Only cities with housing prices will be shown.
        showCitiesInMap(cities_polygons_with_house_prices, data_name, output_housing_price_folder_per_year, year)

        # Main part: calculate Global Moran I value
        calculateGlobalMoranI(cities_polygons_with_house_prices, data_name, output_housing_price_folder, year)

        # Main part: calculate local Moran I value
        calculateLocalMoranI(cities_polygons_with_house_prices, data_name, output_housing_price_folder, year)