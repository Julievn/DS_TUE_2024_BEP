import csv

# local libraries
from map_visualization import *
from moran_calculation import *
from utility import *

# Read a csv file containing immigration for all cities in the Netherlands.
# Return a list of dictionaries. Each element is a dictionary. Each dictionary is a list of cities with immigration.
def readCsvImmigration(path_to_immigration_file):
    # create a list of dictionaries. Each element is a dictionar which  is a list of cities with data for that year.
    immigration_all_years = [] 
    start_year = 2013

    special_municipality_mapping = {"'s-Gravenhage (municipality)": "'s-Gravenhage",
                                    "Groningen (municipality)": "Groningen",
                                    "Utrecht (municipality)" : "Utrecht",
                                    "Laren (NH.)" : "Laren",
                                    "Rijswijk (ZH.)" : "Rijswijk",
                                    "Beek (L.)" : "Beek",
                                    "Stein (L.)" : "Stein",
                                    "Middelburg (Z.)" : "Middelburg",
                                    "Hengelo (O.)" : "Hengelo"}

    with open(path_to_immigration_file, newline='', encoding='utf-8') as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        next(csv_reader, None)  # skip the headers
        for row in csv_reader:     
            print ("Row {} with {} columns".format(row, len(row)))
            if ((len(row) == 3) and (row[2].isdigit())):
                current_year = int(row[0].replace('"', ''))
                current_city = row[1].replace('"', '')
                current_immigration = int(row[2])

                print ("Immigration current_city {}".format(current_city))

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
    print("Successfully loaded {} for {} year".format(path_to_immigration_csv_file, len(immigration_all_years)))

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
        municipalties_polygons_with_immigration = getMunicipalitiesPolygonsWithData(path_to_shape_file, year, immigration_per_year, data_name, output_immigration_folder_per_year)
        print("Successfully loaded ", path_to_shape_file)

        # Show municipalties in map. Only municipalties with housing prices will be shown.
        showMunicipalitiesInMap(municipalties_polygons_with_immigration, data_name, output_immigration_folder_per_year, year)

         # Main part: calculate Global Moran I value
        calculateGlobalMoranI(municipalties_polygons_with_immigration, data_name, output_immigration_folder, year)

         # Main part: calculate local Moran I value
        calculateLocalMoranI(municipalties_polygons_with_immigration, data_name, output_immigration_folder, year)
