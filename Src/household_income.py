import csv

# local libraries
from map_visualization import *
from moran_calculation import *
from utility import *

import numpy as np

import matplotlib.pyplot as plt
from scipy import stats


def processHouseholdIncome(path_to_household_incomes_csv_file, municipality_name_code_mapping, path_to_shape_file, ignored_municipalities, old_municipalities_lists, merged_municipality_list, merged_year_list, merge_mode):
    # Load house prices from csv file
    print("Loading ", path_to_household_incomes_csv_file)

    output_household_incomes_folder = "Output/Household_Incomes/"
    CreateOutputFolderIfNeeded(output_household_incomes_folder)

    # Can contain missing data
    csv_delimeter = ';'
    start_year = getStartYear()
    household_incomes_years = readCsvFile(
        path_to_household_incomes_csv_file, start_year, output_household_incomes_folder, ignored_municipalities, csv_delimeter)
    print("Successfully loaded {} with {} years".format(
        path_to_household_incomes_csv_file, len(household_incomes_years)))

    for household_incomes_per_year in household_incomes_years:
        for municipality, household_income in household_incomes_per_year.items():
            household_incomes_per_year[municipality] = household_income * 1000

    # Handle old municipalities which are merged into new or existing ones.
    # Can be more than one old municipality merged into one new or existing ones
    data_name = "Household Income (in euros)"
    end_year = 2022
    household_incomes_years = handleOldMunicipalities(
        household_incomes_years, data_name, old_municipalities_lists, merged_municipality_list, merged_year_list, merge_mode, start_year, end_year)

    # Substitude missing data with guessed ones
    household_incomes_years = substituteMissingDataWithGuessedOne(
        household_incomes_years, data_name, municipality_name_code_mapping, output_household_incomes_folder, start_year, end_year)

    min_household_income = household_incomes_years[0][list(
        household_incomes_years[0].keys())[0]]
    max_household_income = household_incomes_years[0][list(
        household_incomes_years[0].keys())[0]]
    for household_income_per_year in household_incomes_years:
        for household_income in household_income_per_year.values():
            min_household_income = min(min_household_income, household_income)
            max_household_income = max(max_household_income, household_income)
    print("During {} years, minimum household income is {} while maximum is {}".format(
        len(household_incomes_years), min_household_income, max_household_income))

    local_moran_results_list = []
    municipality_labeled_with_quadrants_list = []
    municipalities_polygons_with_household_incomes_list = []

    for year_idx in range(end_year - start_year + 1):
        household_incomes_per_year = household_incomes_years[year_idx]
        year = start_year + year_idx
        print("-------- Processing {} household income for {} municipalities for year {}".format(
            len(household_incomes_per_year), len(household_incomes_per_year), year))

        # Prepare output household income folder
        output_household_incomes_folder_per_year = output_household_incomes_folder + \
            str(year)
        CreateOutputFolderIfNeeded(output_household_incomes_folder_per_year)

        # Export data (i.e house price per municipality) to file
        field_names = ['Regions', data_name]
        exportDataToCSVFile(household_incomes_per_year.items(
        ), field_names, output_household_incomes_folder_per_year + "/" + data_name + "_" + str(year) + ".csv", 'w')

        # Export municipalities with most expensive house prices
        most_expensive_municipalities = {
            key: val for key, val in household_incomes_per_year.items() if val >= 500000}
        exportDataToCSVFile(most_expensive_municipalities.items(
        ), field_names, output_household_incomes_folder_per_year + "/most_incomes_" + data_name + "_" + str(year) + ".csv", 'w')

        top_ten_least_expensive_municipalities = sorted(
            household_incomes_per_year.items(), key=lambda item: item[1])[:5]
        exportDataToCSVFile(top_ten_least_expensive_municipalities, field_names, output_household_incomes_folder_per_year +
                            "/top_five_least_income_" + data_name + "_" + str(year) + ".csv", 'w')

        top_ten_most_expensive_municipalities = sorted(
            household_incomes_per_year.items(), key=lambda item: item[1], reverse=True)[:5]
        exportDataToCSVFile(top_ten_most_expensive_municipalities, field_names, output_household_incomes_folder_per_year +
                            "/top_five_most_income_" + data_name + "_" + str(year) + ".csv", 'w')

        # Keep only municipalities with housing prices
        municipalities_polygons_with_household_incomes = getMunicipalitiesPolygonsWithData(
            path_to_shape_file, year, household_incomes_per_year, data_name, output_household_incomes_folder, True)
        print("Successfully loaded ", path_to_shape_file)

        # Show municipalities in map. Only municipalities with housing prices will be shown.
        showMunicipalitiesInMap(municipalities_polygons_with_household_incomes,
                                data_name, output_household_incomes_folder_per_year, year, min_household_income, max_household_income)

        id_variable = "GM_CODE"
        islands = getIslandFromQueenWeightMatrix(
            municipalities_polygons_with_household_incomes, id_variable, output_household_incomes_folder, year)
        print("Islands found in Queen spatial matrix {}. Removing islands from the geometry.".format(islands))
        municipalities_polygons_with_house_prices_without_islands = municipalities_polygons_with_household_incomes.drop(
            islands).reset_index(drop=True)

        municipalities_polygons_with_household_incomes_list.append(
            municipalities_polygons_with_house_prices_without_islands)

        # Main part: calculate Global Moran I value
        queen_spatial_weight_matrix = calculateQueenWeightMatrix(
            municipalities_polygons_with_house_prices_without_islands, data_name, id_variable, output_household_incomes_folder, year)
        calculateGlobalMoranI(municipalities_polygons_with_house_prices_without_islands,
                              queen_spatial_weight_matrix, data_name, output_household_incomes_folder, year)

        # Main part: calculate local Moran I value
        local_moran_result, municipality_labeled_with_quadrants = calculateLocalMoranI(municipalities_polygons_with_house_prices_without_islands,
                                                                                       queen_spatial_weight_matrix, data_name, output_household_incomes_folder, year)
        local_moran_results_list.append(local_moran_result)
        municipality_labeled_with_quadrants_list.append(
            municipality_labeled_with_quadrants)
        exportFoliumLisaMap(municipalities_polygons_with_house_prices_without_islands,
                            data_name, local_moran_result, output_household_incomes_folder_per_year, year)

    exportChoroplethMapsAllYears(
        municipalities_polygons_with_household_incomes_list, data_name, output_household_incomes_folder, min_household_income, max_household_income)

    exportScatterPlotsAllYears(municipalities_polygons_with_household_incomes_list,
                               data_name, local_moran_results_list, output_household_incomes_folder)

    exportLisaHotColdSpotsAllYears(municipalities_polygons_with_household_incomes_list,
                                   data_name, local_moran_results_list, output_household_incomes_folder)

    exportAllQuadrantsAllYearsToCSVFile(
        municipality_labeled_with_quadrants_list, data_name, output_household_incomes_folder)
