import csv

# local libraries
from map_visualization import *
from moran_calculation import *
from utility import *

import numpy as np

import matplotlib.pyplot as plt
from scipy import stats

# Read a csv file containing house prices for all cities in the Netherlands.
# Return a list of dictionaries. Each element is a dictionary. Each dictionary is a list of cities with house prices.
def readCsvHousePrice(path_to_house_prices_file, output_folder):
    # create a list of dictionaries. Each element is a dictionary which is a list of cities with house prices for a particular year.
    house_prices_years = [] 
    start_year = 2013

    # Creating an empty dictionary wich each element is a list of housing prices of a municipality for all years.
    house_prices_municipalities = {}

    special_municipality_mapping = {"'s-Gravenhage (municipality)": "'s-Gravenhage",
                                    "Groningen (municipality)": "Groningen",
                                    "Utrecht (municipality)" : "Utrecht",
                                    "Laren (NH.)" : "Laren",
                                    "Rijswijk (ZH.)" : "Rijswijk",
                                    "Beek (L.)" : "Beek",
                                    "Stein (L.)" : "Stein",
                                    "Hengelo (O.)" : "Hengelo"}

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
                if (len(house_prices_years) == year_idx):
                    house_prices_per_year = {current_city: current_price}
                    house_prices_years.append(house_prices_per_year)
                else:
                    house_prices_per_year = house_prices_years[current_year -start_year]
                    house_prices_per_year[current_city] = current_price

                if current_city in house_prices_municipalities:
                    house_price_per_municipality = house_prices_municipalities[current_city]
                    year_with_housing_price = {current_year: current_price}
                    house_price_per_municipality.append(year_with_housing_price)
                else:
                    year_with_housing_price = {current_year: current_price}
                    house_prices_municipalities[current_city] = [year_with_housing_price]   

    output_housing_price_regression_model_folder = output_folder + 'RegressionModel/'
    CreateOutputFolderIfNeeded(output_housing_price_regression_model_folder)
    for municipality in house_prices_municipalities:
        # This municipality does not have complete housing prices. So can use regression models to replace missing house prices with
        # reasonable guesses
        num_house_prices_in_this_municipality = len(house_prices_municipalities[municipality])
        if num_house_prices_in_this_municipality < 11 and num_house_prices_in_this_municipality > 3:
            print ("{} do not have complete housing prices. Running regression model to calculate guessed housing prices".format(municipality))
            house_prices = []
            years_with_missing_house_prices = [2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023]
            years_with_house_prices = []
            for year_with_housing_price in house_prices_municipalities[municipality]:
                year = list(year_with_housing_price.keys())[0]
                house_prices.append(year_with_housing_price[year])
                years_with_house_prices.append(year)
                years_with_missing_house_prices.remove(year)
                print ("Years with housing prices = {}".format(years_with_house_prices))
                print ("Years with missing housing prices = {}".format(years_with_missing_house_prices))

            slope, intercept, r, p, std_err = stats.linregress(years_with_house_prices, house_prices)

            def calculateHousePriceForYear(year):
                return slope * year + intercept

            mymodel = list(map(calculateHousePriceForYear, years_with_house_prices))
            plt.scatter(years_with_house_prices, house_prices)
            plt.plot(years_with_house_prices, mymodel)
            plt.savefig(output_housing_price_regression_model_folder + "regression_model_" + municipality)

            fig, ax = plt.subplots()
            ax.scatter(years_with_house_prices, house_prices, c='blue', label='existing housing prices',
                        alpha=0.7, edgecolors='none')

            colors = np.full((11), ["blue"], dtype=str)
            guessed_house_prices = []
            for year_with_missing_house_price in years_with_missing_house_prices:
                print ("calculateHousePriceForYear for year {}".format(year_with_missing_house_price))
                guessed_house_price = calculateHousePriceForYear(year_with_missing_house_price)
                house_prices_per_year = house_prices_years[year_with_missing_house_price - start_year]
                house_prices_per_year[municipality] = guessed_house_price
                years_with_house_prices.append(year_with_missing_house_price)
                house_prices.append(guessed_house_price)
                guessed_house_prices.append(guessed_house_price)
                colors[year_with_missing_house_price - start_year] = 'red'

            ax.scatter(years_with_house_prices, house_prices, c='red', label='guessed housing prices',
                        alpha=0.7, edgecolors='none')
            

            mymodel = list(map(calculateHousePriceForYear, years_with_house_prices))
            ax.scatter(years_with_house_prices, house_prices, c=colors)
            plt.legend()
            plt.title("Regression model to substitute missing housing prices for " + municipality)
            plt.xlabel("Years", size=15)
            plt.ylabel("Housing prices", size=15)
            plt.tight_layout()
            ax.plot(years_with_house_prices, mymodel)
            plt.savefig(output_housing_price_regression_model_folder + '/' + "data_substitution_use_regression_model_" + municipality)
    return house_prices_years

def processHousePrices(path_to_house_prices_csv_file, path_to_shape_file):
    # Load house prices from csv file
    print("Loading ", path_to_house_prices_csv_file)

    output_housing_price_folder = "Output/Housing_Prices/"
    CreateOutputFolderIfNeeded(output_housing_price_folder)
    
    house_prices_years = readCsvHousePrice(path_to_house_prices_csv_file, output_housing_price_folder)
    print("Successfully loaded ", path_to_house_prices_csv_file)

    start_year = 2013
    for year_idx in range(1):    
        house_prices_per_year = house_prices_years[year_idx]
        year = start_year + year_idx
        print("--------{}".format(year))

        # Prepare output housing price folder
        output_housing_price_folder_per_year = "Output/Housing_Prices/" + str(year)
        CreateOutputFolderIfNeeded(output_housing_price_folder_per_year)

        # Export data (i.e house price per municipality) to file
        data_name = "House Price (in euros)"
        field_names = ['Regions', data_name]
        exportDataToCSVFile(house_prices_per_year.items(), field_names, output_housing_price_folder_per_year + "/" + data_name + "_" + str(year) + ".csv")

        # Export municipalities with most expensive house prices
        most_expensive_municipalities = {key:val for key, val in house_prices_per_year.items() if val >= 500000}
        exportDataToCSVFile(most_expensive_municipalities.items(), field_names, output_housing_price_folder_per_year + "/most_expensive_" + data_name + "_" + str(year) + ".csv")

        top_ten_least_expensive_municipalities = sorted(house_prices_per_year.items(), key=lambda item: item[1])[:5]
        exportDataToCSVFile(top_ten_least_expensive_municipalities, field_names, output_housing_price_folder_per_year + "/top_five_least_expensive_" + data_name + "_" + str(year) + ".csv")

        top_ten_most_expensive_municipalities = sorted(house_prices_per_year.items(), key=lambda item: item[1], reverse = True)[:5]
        exportDataToCSVFile(top_ten_most_expensive_municipalities, field_names, output_housing_price_folder_per_year + "/top_five_most_expensive_" + data_name + "_" + str(year) + ".csv")

        # Keep only cities with housing prices 
        municipalities_polygons_with_house_prices = getMunicipalitiesPolygonsWithData(path_to_shape_file, year, house_prices_per_year, data_name, output_housing_price_folder)
        print("Successfully loaded ", path_to_shape_file)

        # Show municipalities in map. Only municipalities with housing prices will be shown.
        showMunicipalitiesInMap(municipalities_polygons_with_house_prices, data_name, output_housing_price_folder_per_year, year)

        # Main part: calculate Global Moran I value
        calculateGlobalMoranI(municipalities_polygons_with_house_prices, data_name, output_housing_price_folder, year)

        # Main part: calculate local Moran I value
        calculateLocalMoranI(municipalities_polygons_with_house_prices, data_name, output_housing_price_folder, year)