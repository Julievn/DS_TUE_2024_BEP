import csv
import fiona
import geopandas as gpd
import glob
import os
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

def exportDataToFile(data, data_name, file_path):
    field_names = ['Regions', data_name]
    with open(file_path, 'w') as csvfile:
        writer = csv.writer(csvfile)

        # writing the fields
        writer.writerow(field_names)

        # writing the data rows
        print(type(data))
        writer.writerows(data.items())

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

def getListOfArguments():
    args = sys.argv[1:]
    if len(args) <= 0 or args[0] != '-house_price_csv' or args[2] != '-path_to_shape_file' or args[4] != '-immigration_csv':
        print("Please use -house_price_csv and -path_to_shape_file as parameters.")
        exitProgram()

    print("Running program {} with value {}; {} with value {} ".format(args[0], args[1], args[2], args[3]))
    return args