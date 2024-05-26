import csv
import fiona
import geopandas as gpd
import glob
import os
import shutil
import sys
from scipy import stats
import matplotlib.pyplot as plt
import numpy as np

# data is a list with each element is a row in the csv file. Each element can contain more than 1 column
# field_names are the column names
def exportDataToCSVFile(data, field_names, file_path, mode):
    # Opening the file with newline='' on all platforms to disable universal newlines translation
    with open(file_path, mode, newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile, delimiter=',') # Excel supports ',' and not tab
        if mode == 'w':
            writer.writerow(field_names)

        writer.writerows(data)

def CreateOutputFolderIfNeeded(output_folder):
    if os.path.exists(output_folder):
        shutil.rmtree(output_folder)
    try:
        os.makedirs(output_folder)
        print("Directory '%s' created" % output_folder)
    except OSError as error:
        print("Directory '%s' can not be created" % output_folder)

def getMunicipalitiesPolygonsWithData(path_to_shape_file, year, data_per_year, data_name, output_folder, is_set_index):    
    # kwargs in Python is a special syntax that allows you to pass a keyworded, variable-length argument dictionary to a function. 
    # It is short for "keyword arguments". When defining a function, you can use the ** in front of a parameter to indicate that 
    # it should accept any number of keyword arguments.
    def records(filename, usecols, year, data_per_year, **kwargs):
        municipalities_with_polygons_and_not_data_file_name_path = output_folder + "/municipalties_with_polygons_and_not_" + data_name + "_" + str(year) + ".txt" 
        with fiona.open(filename, **kwargs) as source:
            for feature in source:
                f = {k: feature[k] for k in ['id', 'geometry']}
                f['properties'] = {k: feature['properties'][k] for k in usecols}
                municipality_name = f['properties']['GM_NAAM']

                # dictionary with key, value pair. For example, Aa en Hunze -> 213176
                if municipality_name in data_per_year and f['properties']['H2O'] == "NEE": # only display cities with housing prices and not water boundaries
                    f['properties']['Year'] = year
                    f['properties'][data_name] = data_per_year[municipality_name]
                    yield f
                else:
                    #print("SKIp city '%s' as DOES NOT have data or it's just water boundary" % municipality_name)
                    #print (f)
                    open_file = open(municipalities_with_polygons_and_not_data_file_name_path, "a")
                    if f['properties']['H2O'] == "NEE":
                        open_file.write(municipality_name  + "              " + f['id']  + "        " + f['properties']['GM_CODE'] + "      " + "LAND")
                    else:    
                        open_file.write(municipality_name  + "              " + f['id']  + "        " + f['properties']['GM_CODE'] + "      " + "WATER")
                    
                    open_file.write("\n")
                    open_file.close()

    # https://epsg.io/28992
    # Use GM code as the index so that spatial weight matrix can conviniently use GM code to query neighbor. Otherwise, it's still ok but id 0, 1 is used. 
    # drop=False will make exporting to Folium map fail.
    if is_set_index:
        cities_polygons = gpd.GeoDataFrame.from_features(records(path_to_shape_file, ['GM_CODE', 'GM_NAAM', 'H2O'], year, data_per_year)).set_crs('epsg:28992').set_index('GM_CODE', drop=False)
    else:
        cities_polygons = gpd.GeoDataFrame.from_features(records(path_to_shape_file, ['GM_CODE', 'GM_NAAM', 'H2O'], year, data_per_year)).set_crs('epsg:28992')
    print (cities_polygons.crs)
    return cities_polygons

def exitProgram():
    print("Exiting the program...")
    sys.exit(1)

def getListOfArguments():
    args = sys.argv[1:]
    if len(args) <= 0 or args[0] != '-house_price_csv' or args[2] != '-path_to_shape_file' or args[4] != '-immigration_csv':
        print("Please use -house_price_csv and -path_to_shape_file as parameters.")
        exitProgram()

    print("Running program {} with value {}; {} with value {} ".format(args[0], args[1], args[2], args[3]))
    return args

def substituteMissingDataWithGuessedOne(data_all_years, data_name, output_folder, start_year, end_year):
    print("data_all_years has {} years".format(len(data_all_years)))
    # Creating an empty dictionary wich each element is a list of housing prices of a municipality for all years.
    data_municipalities = {}
    current_year = start_year
    year_idx = 0
    for data_per_year in data_all_years: # data_per_year is a dictionary with each element: muncipality -> data
        current_year = start_year + year_idx
        for municipality_name, current_data in data_per_year.items():
            year_with_data = {current_year: current_data}
            if municipality_name in data_municipalities:
                data_per_municipality = data_municipalities[municipality_name] 
                data_per_municipality.append(year_with_data)
            else:
               data_municipalities[municipality_name] = [year_with_data]   
        year_idx += 1

    output_data_regression_model_folder = output_folder + 'RegressionModel/'
    CreateOutputFolderIfNeeded(output_data_regression_model_folder)
    year_period = (end_year - start_year + 1)
    for municipality in data_municipalities:
        # This municipality does not have complete housing prices. So can use regression models to replace missing house prices with
        # reasonable guesses
        num_data_in_this_municipality = len(data_municipalities[municipality])
        if num_data_in_this_municipality < 11 and num_data_in_this_municipality > 3:
            #print ("{} do not have complete housing prices. Running regression model to calculate guessed housing prices".format(municipality))
            house_prices = []
            years_with_missing_data = list(range(start_year, end_year + 1))
            years_with_data = []
            for year_with_data in data_municipalities[municipality]:
                year = list(year_with_data.keys())[0]
                #print("year {}".format(year))
                house_prices.append(year_with_data[year])
                years_with_data.append(year)
                years_with_missing_data.remove(year)
                #print ("housing prices = {}".format(house_prices))
                #print ("Years with housing prices = {}".format(years_with_data))
                #print ("Years with missing housing prices = {}".format(years_with_missing_data))

            # Linear regression models using existing data
            slope, intercept, r, p, std_err = stats.linregress(years_with_data, house_prices)

            def calculateDataForYear(year):
                return slope * year + intercept

            mymodel = list(map(calculateDataForYear, years_with_data))
            plt.scatter(years_with_data, house_prices)
            plt.plot(years_with_data, mymodel)
            plt.savefig(output_data_regression_model_folder + "regression_model_" + municipality)

            fig, ax = plt.subplots()
            ax.scatter(years_with_data, house_prices, c='blue', label='existing housing prices',
                        alpha=0.7, edgecolors='none')

            colors = np.full((11), ["blue"], dtype=str)
            guessed_house_prices = []
            for year_with_missing_data in years_with_missing_data:
                # Substitude missing data with guessed one
                # print ("calculate " + data_name + " for year {}".format(year_with_missing_data))
                guessed_house_price = calculateDataForYear(year_with_missing_data)
                data_per_year = data_all_years[year_with_missing_data - start_year]
                data_per_year[municipality] = guessed_house_price

                years_with_data.append(year_with_missing_data)
                house_prices.append(guessed_house_price)
                guessed_house_prices.append(guessed_house_price)
                colors[year_with_missing_data - start_year] = 'red'

            ax.scatter(years_with_data, house_prices, c='red', label='guessed ' + data_name,
                        alpha=0.7, edgecolors='none')
            
            mymodel = list(map(calculateDataForYear, years_with_data))
            ax.scatter(years_with_data, house_prices, c=colors)
            plt.legend()
            plt.title("Regression model " + data_name + " for " + municipality)
            plt.xlabel("Years", size=15)
            plt.ylabel(data_name, size=15)
            plt.tight_layout()
            ax.plot(years_with_data, mymodel)
            plt.savefig(output_data_regression_model_folder + '/' + "data_substitution_use_regression_model_" + municipality)
    return data_all_years

# Read a csv file containing data for all municipalities in the Netherlands.
# The csv must contain 3 columns: Period, Municipality, Data using ',' as the delimiter
# Return a list of dictionaries. Each element is a dictionary. Each dictionary is a list of cities with house prices.
def readCsvFile(path_to_csv_file, start_year, output_folder):
    # create a list of dictionaries. Each element is a dictionary which is a list of cities with house prices for a particular year.
    data_years = [] 
    special_municipality_mapping = {"'s-Gravenhage (municipality)": "'s-Gravenhage",
                                    "Groningen (municipality)": "Groningen",
                                    "Utrecht (municipality)" : "Utrecht",
                                    "Laren (NH.)" : "Laren",
                                    "Rijswijk (ZH.)" : "Rijswijk",
                                    "Beek (L.)" : "Beek",
                                    "Stein (L.)" : "Stein",
                                    "Hengelo (O.)" : "Hengelo"}

    with open(path_to_csv_file, newline='', encoding='utf-8') as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=';', quotechar='|')
        next(csv_reader, None)  # skip the headers
        for row in csv_reader:     
            if ((len(row) == 3) and (row[2].isdigit())):
                current_year = int(row[0].replace('"', ''))
                current_municipality = row[1].replace('"', '')
                current_price = int(row[2])

                # Some names in the geographical file and the housing price file are not the same. So we need to do this mapping.
                if current_municipality in special_municipality_mapping:
                    current_municipality = special_municipality_mapping[current_municipality]

                year_idx = current_year -start_year
                if (len(data_years) == year_idx):
                    data_per_year = {current_municipality: current_price}
                    data_years.append(data_per_year)
                else:
                    data_per_year = data_years[current_year -start_year]
                    data_per_year[current_municipality] = current_price  
    return data_years