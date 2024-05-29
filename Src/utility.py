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


def getStartYear():
    return 2013


# data is a list with each element is a row in the csv file. Each element can contain more than 1 column
# field_names are the column names


def readDictionaryFromCSVFile(path_to_code_name_mapping_file):
    with open(path_to_code_name_mapping_file, mode='r') as csvfile:
        reader = csv.reader(csvfile)
        return {rows[0]: rows[1] for rows in reader}


def exportDataToCSVFile(data, field_names, file_path, mode):
    # Opening the file with newline='' on all platforms to disable universal newlines translation
    with open(file_path, mode, newline='', encoding='utf-8') as csvfile:
        # Excel supports ',' and not tab
        writer = csv.writer(csvfile, delimiter=',')
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
        municipalities_with_polygons_and_not_data_file_name_path = output_folder + \
            "/" + str(year) + "/municipalties_with_polygons_and_not_" + \
            data_name + "_" + str(year) + ".txt"
        municipality_code_name_mapping = {}
        with fiona.open(filename, **kwargs) as source:
            for feature in source:
                f = {k: feature[k] for k in ['id', 'geometry']}
                f['properties'] = {k: feature['properties'][k]
                                   for k in usecols}
                municipality_name = f['properties']['GM_NAAM'].replace('"', '')
                municipality_code = f['properties']['GM_CODE']
                municipality_code_name_mapping[municipality_name] = municipality_code

                # dictionary with key, value pair. For example, Aa en Hunze -> 213176
                # only display cities with housing prices and not water boundaries
                if municipality_name in data_per_year and f['properties']['H2O'] == "NEE":
                    f['properties']['Year'] = year
                    f['properties'][data_name] = data_per_year[municipality_name]
                    yield f
                else:
                    # print("SKIp city '%s' as DOES NOT have data or it's just water boundary" % municipality_name)
                    # print (f)
                    open_file = open(
                        municipalities_with_polygons_and_not_data_file_name_path, "a")
                    if f['properties']['H2O'] == "NEE":
                        open_file.write(municipality_name + "              " +
                                        f['id'] + "        " + f['properties']['GM_CODE'] + "      " + "LAND")
                    else:
                        open_file.write(municipality_name + "              " +
                                        f['id'] + "        " + f['properties']['GM_CODE'] + "      " + "WATER")

                    open_file.write("\n")
                    open_file.close()

        export_municipality_code_name_csv_path = output_folder + \
            "/" + "municipality_name_code" + "_" + str(year) + ".csv"
        print("Exporting municipality code name mapping to csv {} with {} rows".format(
            export_municipality_code_name_csv_path, len(municipality_code_name_mapping) + 1))
        field_names = ['Municipality name', 'Municipality code']
        exportDataToCSVFile(municipality_code_name_mapping.items(
        ), field_names, export_municipality_code_name_csv_path, 'w')

    # https://epsg.io/28992
    # Use GM code as the index so that spatial weight matrix can conviniently use GM code to query neighbor. Otherwise, it's still ok but id 0, 1 is used.
    # drop=False will make exporting to Folium map fail.
    if is_set_index:
        cities_polygons = gpd.GeoDataFrame.from_features(records(path_to_shape_file, [
                                                         'GM_CODE', 'GM_NAAM', 'H2O'], year, data_per_year)).set_crs('epsg:28992').set_index('GM_CODE', drop=False)
    else:
        cities_polygons = gpd.GeoDataFrame.from_features(records(path_to_shape_file, [
                                                         'GM_CODE', 'GM_NAAM', 'H2O'], year, data_per_year)).set_crs('epsg:28992')
    print(cities_polygons.crs)
    return cities_polygons


def exitProgram():
    print("Exiting the program...")
    sys.exit(1)


def getListOfArguments():
    args = sys.argv[1:]
    if len(args) <= 0:
        if args[0] != '-name_code_csv':
            print("Please use -name_code_csv as the first parameter.")
        elif args[2] != '-house_price_csv':
            print("Please use -house_price_csv as the second parameter.")
        elif args[4] != '-path_to_shape_file':
            print("Please use -path_to_shape_file as the third paramter.")
        elif args[6] != '-immigration_csv':
            print("Please use -immigration_csv as the fourth parameter.")
        elif args[8] != '-household_income_csv':
            print("Please use -household_income_csv as the fifth parameter.")
        exitProgram()

    print("Running program {} with value {}; {} with value {} ".format(
        args[0], args[1], args[2], args[3]))
    return args


def handleOldMunicipalities(data_all_years, data_name, old_municipalities_lists, new_municipality_list, merged_year_list, merge_mode, start_year, end_year):
    idx = 0
    for new_municipality in new_municipality_list:
        merged_year = merged_year_list[idx]
        old_municipalities_list = old_municipalities_lists[idx]
        current_year = start_year

        # Fill in missing data for new municipality
        while current_year < merged_year:
            data_per_year = data_all_years[current_year - start_year]
            merged_data = 0
            count = 0
            for old_municipality in old_municipalities_list:

                merged_data += data_per_year[old_municipality]
                count += 1

            if merge_mode != 's':  # average for housing prices and incomes
                merged_data = merged_data / count

            if new_municipality in data_per_year:
                print("New municipality {} already has the value {}. Do nothing".format(
                    new_municipality, data_per_year[new_municipality]))
            else:
                print('Fill in missing data for new municipality {} in year {} with value {}. Removing old municipalities {}'.format(
                    new_municipality, current_year, merged_data, old_municipalities_list))
                data_per_year[new_municipality] = merged_data

            for old_municipality in old_municipalities_list:
                removed_municipality = data_per_year.pop(
                    old_municipality, None)

            current_year += 1
        idx += 1

    return data_all_years


def substituteMissingDataWithGuessedOne(data_all_years, data_name, municipality_name_code_mapping, output_folder, start_year, end_year):
    print("data_all_years has {} years".format(len(data_all_years)))
    # Creating an empty dictionary wich each element is a list of housing prices of a municipality for all years.
    data_municipalities = {}
    current_year = start_year
    year_idx = 0
    for data_per_year in data_all_years:  # data_per_year is a dictionary with each element: muncipality -> data
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
    municipalitiies_with_missing_datas = []
    for municipality in data_municipalities:
        # This municipality does not have complete data. So can use regression models to replace missing data with
        # reasonable guesses
        num_data_in_this_municipality = len(data_municipalities[municipality])
        if num_data_in_this_municipality < year_period and num_data_in_this_municipality > 3:
            print("{} do not have complete {}. Running regression model to calculate guessed housing prices".format(
                municipality, data_name))
            house_prices = []
            years_with_data = []
            years_with_missing_data = list(range(start_year, end_year + 1))
            for year_with_data in data_municipalities[municipality]:
                year = list(year_with_data.keys())[0]
                # print("year {}".format(year))
                house_prices.append(year_with_data[year])
                years_with_data.append(year)
                years_with_missing_data.remove(year)
                # print ("housing prices = {}".format(house_prices))
                # print ("Years with housing prices = {}".format(years_with_data))
                # print ("Years with missing housing prices = {}".format(years_with_missing_data))

            # Linear regression models using existing data
            slope, intercept, r, p, std_err = stats.linregress(
                years_with_data, house_prices)

            def calculateDataForYear(year):
                return slope * year + intercept

            mymodel = list(map(calculateDataForYear, years_with_data))
            plt.scatter(years_with_data, house_prices)
            plt.plot(years_with_data, mymodel)
            plt.savefig(output_data_regression_model_folder +
                        "regression_model_" + municipality)

            fig, ax = plt.subplots()
            ax.scatter(years_with_data, house_prices, c='blue', label='existing ' + data_name,
                       alpha=0.7, edgecolors='none')

            colors = np.full((year_period), ["blue"], dtype=str)
            guessed_data_list = []
            for year_with_missing_data in years_with_missing_data:
                # Substitude missing data with guessed one
                guessed_data = calculateDataForYear(
                    year_with_missing_data)
                print("calculate missing " + data_name +
                      " for municipality {} in year {} with value {} and start year = {}".format(municipality, year_with_missing_data, guessed_data, start_year))
                data_per_year = data_all_years[year_with_missing_data - start_year]
                data_per_year[municipality] = guessed_data

                years_with_data.append(year_with_missing_data)
                house_prices.append(guessed_data)
                guessed_data_list.append(guessed_data)
                print(
                    "year_with_missing_data - start_year = {} - len colors is {}".format(
                        (year_with_missing_data - start_year), len(colors)))
                colors[len(years_with_data) - 1] = 'red'

            print("years_with_data  length = {}".format(len(years_with_data)))
            print("guessed_data_list  length = {}".format(len(guessed_data_list)))
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
            plt.savefig(output_data_regression_model_folder + '/' +
                        "data_substitution_use_regression_model_" + municipality)

            years_with_missing_data_string = ' '.join(
                map(str, years_with_missing_data))
            municipality_code = municipality_name_code_mapping[municipality]
            municipalitiy_with_missing_data = [
                municipality, municipality_code, years_with_missing_data_string]
            municipalitiies_with_missing_datas.append(
                municipalitiy_with_missing_data)

        if num_data_in_this_municipality < year_period and num_data_in_this_municipality <= 3:
            print("Cannot run regression model for municipality {}".format(municipality))

    # Export municipalitiy with missing data
    field_names = ['Municipality name', 'Municipality code', 'Missing Years']
    print("Regression model run for {}".format(
        municipalitiies_with_missing_datas))
    exportDataToCSVFile(municipalitiies_with_missing_datas, field_names,
                        output_folder + "/missing_" + data_name + ".csv", 'w')

    return data_all_years

# Read a csv file containing data for all municipalities in the Netherlands.
# The csv must contain 3 columns: Period, Municipality, Data using ',' as the delimiter
# Return a list of dictionaries. Each element is a dictionary. Each dictionary is a list of cities with house prices.


def readCsvFile(path_to_csv_file, start_year, output_folder, ignored_municipalities, csv_delimeter):
    # create a list of dictionaries. Each element is a dictionary which is a list of cities with house prices for a particular year.
    print("Loading csv file with ignored municipality {}".format(
        ignored_municipalities))
    data_years = []
    special_municipality_mapping = {"'s-Gravenhage (municipality)": "'s-Gravenhage",
                                    "'s-Gravenhage (gemeente)": "'s-Gravenhage",
                                    "Groningen (municipality)": "Groningen",
                                    "Groningen (gemeente)": "Groningen",
                                    "Utrecht (municipality)": "Utrecht",
                                    "Utrecht (gemeente)": "Utrecht",
                                    "Laren (NH.)": "Laren",
                                    "Rijswijk (ZH.)": "Rijswijk",
                                    "Beek (L.)": "Beek",
                                    "Stein (L.)": "Stein",
                                    "Hengelo (O.)": "Hengelo",
                                    "Middelburg (Z.)": "Middelburg"}

    with open(path_to_csv_file, newline='', encoding='utf-8') as csvfile:
        # to handle "2013","Nuenen, Gerwen en Nederwetten",302982
        csv_reader = csv.reader(
            csvfile, delimiter=csv_delimeter, quotechar='"')
        next(csv_reader, None)  # skip the headers
        for row in csv_reader:
            if ((len(row) == 3) and (row[2].replace('"', '').replace('.', '', 1).replace(',', '', 1).isdigit())):
                current_year = int(row[0].replace('"', ''))
                current_municipality = row[1].replace('"', '')
                if current_municipality in ignored_municipalities:
                    print("Ignoring {}".format(current_municipality))
                else:
                    current_price = float(row[2].replace(',', '.', 1))

                    # Some names in the geographical file and the housing price file are not the same. So we need to do this mapping.
                    if current_municipality in special_municipality_mapping:
                        current_municipality = special_municipality_mapping[current_municipality]

                    year_idx = current_year - start_year
                    if (len(data_years) == year_idx):
                        data_per_year = {current_municipality: current_price}
                        data_years.append(data_per_year)
                    else:
                        data_per_year = data_years[current_year - start_year]
                        data_per_year[current_municipality] = current_price
    return data_years
