import csv
import fiona
import geopandas as gpd
import glob
import os
import shutil
import sys

# data is a list
# field_names is a row with 2 columns
def exportDataToCSVFile(data, field_names, file_path):
    # Opening the file with newline='' on all platforms to disable universal newlines translation
    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile, delimiter=',') # Excel supports ',' and not tab
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
                if city_name in data_per_year and f['properties']['H2O'] == "NEE": # only display cities with housing prices and not water boundaries
                    f['properties']['Year'] = year
                    f['properties'][data_name] = data_per_year[city_name]
                    yield f
                else:
                    print("SKIp city '%s' as DOES NOT have data or it's just water boundary" % city_name)
                    print (f)
                    open_file = open(cities_with_polygons_and_not_data_file_name_path, "a")
                    if f['properties']['H2O'] == "NEE":
                        open_file.write(city_name  + "              " + f['id']  + "        " + f['properties']['GM_CODE'] + "      " + "LAND")
                    else:    
                        open_file.write(city_name  + "              " + f['id']  + "        " + f['properties']['GM_CODE'] + "      " + "WATER")
                    
                    open_file.write("\n")
                    open_file.close()

    # https://epsg.io/28992
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