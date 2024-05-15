import csv

# local libraries
from map_visualization import *
from moran_calculation import *
from utility import *

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

def processImmigration(path_to_immigration_csv_file, path_to_shape_file):
    # Load immigration from csv file
    print("Loading ", path_to_immigration_csv_file)
    immigration_all_years = readCsvImmigration(path_to_immigration_csv_file)
    print("Successfully loaded ", path_to_immigration_csv_file)

    output_immigration_folder = "Output/Immigration/"
    CreateOutputFolderIfNeeded(output_immigration_folder)

    start_year = 2013
    for year_idx in range(1):    
        immigration_per_year = immigration_all_years[year_idx]
        year = start_year + year_idx
        print("--------{}".format(year))

        # Prepare output immigration folder
        output_immigration_folder_per_year = output_immigration_folder + str(year)
        CreateOutputFolderIfNeeded(output_immigration_folder_per_year)

        # Keep only cities with immigration data
        data_name = "Immigration"
        cities_polygons_with_immigration = getCitiesPolygonsWithData(path_to_shape_file, year, immigration_per_year, data_name, output_immigration_folder_per_year)
        print("Successfully loaded ", path_to_shape_file)

        # Show cities in map. Only cities with housing prices will be shown.
        showCitiesInMap(cities_polygons_with_immigration, data_name, output_immigration_folder_per_year, year)

         # Main part: calculate Global Moran I value
        calculateGlobalMoranI(cities_polygons_with_immigration, data_name, output_immigration_folder, year)

         # Main part: calculate local Moran I value
        calculateLocalMoranI(cities_polygons_with_immigration, data_name, output_immigration_folder, year)
