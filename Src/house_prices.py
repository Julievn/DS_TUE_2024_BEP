import csv

# local libraries
from map_visualization import *
from moran_calculation import *
from utility import *


def processHousePrices(path_to_house_prices_csv_file, municipality_name_code_mapping, path_to_shape_file, ignored_municipalities, old_municipalities_lists, merged_municipality_list, merged_year_list, merge_mode):
    # Load house prices from csv file
    print("Loading ", path_to_house_prices_csv_file)

    output_housing_price_folder = "Output/Housing_Prices/"
    CreateOutputFolderIfNeeded(output_housing_price_folder)

    # Can contain missing data
    csv_delimeter = ','
    start_year = getStartYear()
    house_prices_years = readCsvFile(
        path_to_house_prices_csv_file, start_year, output_housing_price_folder, ignored_municipalities, csv_delimeter)
    print("Successfully loaded ", path_to_house_prices_csv_file)

    # Handle old municipalities which are merged into new or existing ones.
    # Can be more than one old municipality merged into one new or existing ones
    data_name = "House Price (in euros)"
    end_year = 2023
    house_prices_years = handleOldMunicipalities(
        house_prices_years, data_name, old_municipalities_lists, merged_municipality_list, merged_year_list, merge_mode, start_year, end_year)

    # Substitude missing data with guessed ones
    house_prices_years = substituteMissingDataWithGuessedOne(
        house_prices_years, data_name, municipality_name_code_mapping, output_housing_price_folder, start_year, end_year)

    min_house_price = house_prices_years[0][list(
        house_prices_years[0].keys())[0]]
    max_house_price = house_prices_years[0][list(
        house_prices_years[0].keys())[0]]
    for house_prices_per_year in house_prices_years:
        for house_price in house_prices_per_year.values():
            min_house_price = min(min_house_price, house_price)
            max_house_price = max(max_house_price, house_price)
    print("During {} years, minimum house price is {} while maximum is {}".format(
        len(house_prices_years), min_house_price, max_house_price))

    local_moran_results_list = []
    municipality_labeled_with_quadrants_list = []
    municipalities_polygons_with_house_prices_list = []
    for year_idx in range(end_year - start_year + 1):
        house_prices_per_year = house_prices_years[year_idx]
        year = start_year + year_idx
        print("--------{}".format(year))

        # Prepare output housing price folder
        output_housing_price_folder_per_year = "Output/Housing_Prices/" + \
            str(year)
        CreateOutputFolderIfNeeded(output_housing_price_folder_per_year)

        # Export data (i.e house price per municipality) to file
        field_names = ['Regions', data_name]
        exportDataToCSVFile(house_prices_per_year.items(
        ), field_names, output_housing_price_folder_per_year + "/" + data_name + "_" + str(year) + ".csv", 'w')

        # Export municipalities with most expensive house prices
        most_expensive_municipalities = {
            key: val for key, val in house_prices_per_year.items() if val >= 500000}
        exportDataToCSVFile(most_expensive_municipalities.items(
        ), field_names, output_housing_price_folder_per_year + "/most_expensive_" + data_name + "_" + str(year) + ".csv", 'w')

        top_ten_least_expensive_municipalities = sorted(
            house_prices_per_year.items(), key=lambda item: item[1])[:5]
        exportDataToCSVFile(top_ten_least_expensive_municipalities, field_names, output_housing_price_folder_per_year +
                            "/top_five_least_expensive_" + data_name + "_" + str(year) + ".csv", 'w')

        top_ten_most_expensive_municipalities = sorted(
            house_prices_per_year.items(), key=lambda item: item[1], reverse=True)[:5]
        exportDataToCSVFile(top_ten_most_expensive_municipalities, field_names, output_housing_price_folder_per_year +
                            "/top_five_most_expensive_" + data_name + "_" + str(year) + ".csv", 'w')

        # Keep only municipalities with housing prices
        municipalities_polygons_with_house_prices = getMunicipalitiesPolygonsWithData(
            path_to_shape_file, year, house_prices_per_year, data_name, output_housing_price_folder, True)
        print("Successfully loaded ", path_to_shape_file)

        # Show municipalities in map. Only municipalities with housing prices will be shown.
        showMunicipalitiesInMap(municipalities_polygons_with_house_prices,
                                data_name, output_housing_price_folder_per_year, year,
                                min_house_price, max_house_price)

        id_variable = "GM_CODE"
        islands = getIslandFromQueenWeightMatrix(
            municipalities_polygons_with_house_prices, id_variable, output_housing_price_folder, year)
        print("Islands found in Queen spatial matrix {}. Removing islands from the geometry.".format(islands))
        municipalities_polygons_with_house_prices_without_islands = municipalities_polygons_with_house_prices.drop(
            islands).reset_index(drop=True)
        municipalities_polygons_with_house_prices_list.append(
            municipalities_polygons_with_house_prices_without_islands)

        # Main part: calculate Global Moran I value
        queen_spatial_weight_matrix = calculateQueenWeightMatrix(
            municipalities_polygons_with_house_prices_without_islands, data_name, id_variable, output_housing_price_folder, year)
        calculateGlobalMoranI(municipalities_polygons_with_house_prices_without_islands,
                              queen_spatial_weight_matrix, data_name, output_housing_price_folder, year)

        # Main part: calculate local Moran I value
        local_moran_result, municipality_labeled_with_quadrants = calculateLocalMoranI(municipalities_polygons_with_house_prices_without_islands,
                                                                                       queen_spatial_weight_matrix, data_name, output_housing_price_folder, year)
        local_moran_results_list.append(local_moran_result)

        print("municipality_labeled_wtih_quadrants is {} with size {}".format(
            type(municipality_labeled_with_quadrants), len(municipality_labeled_with_quadrants)))
        municipality_labeled_with_quadrants_list.append(
            municipality_labeled_with_quadrants)

        exportFoliumLisaMap(municipalities_polygons_with_house_prices_without_islands,
                            data_name, local_moran_result, output_housing_price_folder_per_year, year)

    exportChoroplethMapsAllYears(
        municipalities_polygons_with_house_prices_list, data_name, output_housing_price_folder, min_house_price, max_house_price)

    exportScatterPlotsAllYears(municipalities_polygons_with_house_prices_list,
                               data_name, local_moran_results_list, output_housing_price_folder)

    exportLisaHotColdSpotsAllYears(municipalities_polygons_with_house_prices_list,
                                   data_name, local_moran_results_list, output_housing_price_folder)
    exportAllQuadrantsAllYearsToCSVFile(
        municipality_labeled_with_quadrants_list, data_name, output_housing_price_folder)
