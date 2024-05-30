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
    special_municipality_mapping = {"'s-Gravenhage (municipality)": "'s-Gravenhage",
                                    "Groningen (municipality)": "Groningen",
                                    "Utrecht (municipality)": "Utrecht",
                                    "Laren (NH.)": "Laren",
                                    "Rijswijk (ZH.)": "Rijswijk",
                                    "Beek (L.)": "Beek",
                                    "Stein (L.)": "Stein",
                                    "Middelburg (Z.)": "Middelburg",
                                    "Hengelo (O.)": "Hengelo"}

    start_year = getStartYear()
    with open(path_to_immigration_file, newline='', encoding='utf-8') as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        next(csv_reader, None)  # skip the headers
        for row in csv_reader:
            if ((len(row) == 3) and (row[2].isdigit())):
                current_year = int(row[0].replace('"', ''))
                current_city = row[1].replace('"', '')
                current_immigration = int(row[2])

                # Some names in the geographical file and the housing price file are not the same. So we need to do this mapping.
                if current_city in special_municipality_mapping:
                    current_city = special_municipality_mapping[current_city]

                year_idx = current_year - start_year
                if (len(immigration_all_years) == year_idx):
                    immigration_per_year = {current_city: current_immigration}
                    immigration_all_years.append(immigration_per_year)
                else:
                    immigration_per_year = immigration_all_years[current_year - start_year]
                    immigration_per_year[current_city] = current_immigration
    return immigration_all_years


def processImmigration(path_to_immigration_csv_file, municipality_name_code_mapping, path_to_shape_file, ignored_municipalities, old_municipalities_lists, merged_municipality_list, merged_year_list, merge_mode):
    # Load immigration from csv file
    print("Loading ", path_to_immigration_csv_file)

    output_immigration_folder = "Output/Immigration/"
    CreateOutputFolderIfNeeded(output_immigration_folder)

    # Can contain missing data
    csv_delimeter = ','
    start_year = getStartYear()
    immigration_all_years = readCsvFile(
        path_to_immigration_csv_file, start_year, output_immigration_folder, ignored_municipalities, csv_delimeter)
    print("Successfully loaded {} for {} years".format(
        path_to_immigration_csv_file, len(immigration_all_years)))

    # Handle old municipalities which are merged into new ones.
    # Can be more than one old municipality merged into one new
    data_name = "Immigration"
    end_year = 2022
    immigration_all_years = handleOldMunicipalities(
        immigration_all_years, data_name, old_municipalities_lists, merged_municipality_list, merged_year_list, merge_mode, start_year, end_year)

    # Substitude missing data with guessed ones not because of merging old municipalities
    immigration_all_years = substituteMissingDataWithGuessedOne(
        immigration_all_years, data_name, municipality_name_code_mapping, output_immigration_folder, start_year, end_year)

    min_immigration = immigration_all_years[0][list(
        immigration_all_years[0].keys())[0]]
    max_immigration = immigration_all_years[0][list(
        immigration_all_years[0].keys())[0]]
    for immigration_per_year in immigration_all_years:
        for household_income in immigration_per_year.values():
            min_immigration = min(min_immigration, household_income)
            max_immigration = max(max_immigration, household_income)
    print("During {} years, minimum household income is {} while maximum is {}".format(
        len(immigration_all_years), min_immigration, max_immigration))

    municipalities_polygons_with_immigration_list = []

    for year_idx in range(end_year - start_year + 1):
        immigration_per_year = immigration_all_years[year_idx]
        year = start_year + year_idx
        print("--------{}".format(year))

        # Prepare output immigration folder
        output_immigration_folder_per_year = output_immigration_folder + \
            str(year)
        CreateOutputFolderIfNeeded(output_immigration_folder_per_year)

        # Keep only municipalities with immigration data
        municipalties_polygons_with_immigration = getMunicipalitiesPolygonsWithData(
            path_to_shape_file, year, immigration_per_year, data_name, output_immigration_folder, True)
        print("Successfully loaded {} with {} elements".format(
            path_to_shape_file, len(municipalties_polygons_with_immigration)))

        municipalities_polygons_with_immigration_list.append(
            municipalties_polygons_with_immigration)

        # Show municipalties in map. Only municipalties with housing prices will be shown.
        showMunicipalitiesInMap(municipalties_polygons_with_immigration,
                                data_name, output_immigration_folder_per_year, year, min_immigration, max_immigration)

        id_variable = "GM_CODE"
        islands = getIslandFromQueenWeightMatrix(
            municipalties_polygons_with_immigration, id_variable)
        print("Islands found in Queen spatial matrix {}. Removing islands from the geometry.".format(islands))
        municipalties_polygons_with_immigration_without_islands = municipalties_polygons_with_immigration.drop(
            islands).reset_index(drop=True)
        print("After removing islands: {} elements".format(
            len(municipalties_polygons_with_immigration_without_islands)))

        # Main part: calculate Global Moran I value
        queen_spatial_weight_matrix = calculateQueenWeightMatrix(
            municipalties_polygons_with_immigration_without_islands, data_name, id_variable, output_immigration_folder, year)
        calculateGlobalMoranI(municipalties_polygons_with_immigration_without_islands, queen_spatial_weight_matrix,
                              data_name, output_immigration_folder, year)

        # Main part: calculate local Moran I value
        local_moran_result = calculateLocalMoranI(municipalties_polygons_with_immigration_without_islands, queen_spatial_weight_matrix,
                                                  data_name, output_immigration_folder, year)
        exportFoliumLisaMap(municipalties_polygons_with_immigration_without_islands,
                            data_name, local_moran_result, output_immigration_folder_per_year, year)

    exportChoroplethMapsAllYears(
        municipalities_polygons_with_immigration_list, data_name, output_immigration_folder, min_immigration, max_immigration)
