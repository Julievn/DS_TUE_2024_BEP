import csv

# local libraries
from map_visualization import *
from moran_calculation import *
from utility import *


def processHousePrices(path_to_house_prices_csv_file, path_to_shape_file):
    # Load house prices from csv file
    print("Loading ", path_to_house_prices_csv_file)

    output_housing_price_folder = "Output/Housing_Prices/"
    CreateOutputFolderIfNeeded(output_housing_price_folder)
    
    # Can contain missing data
    start_year = 2013
    house_prices_years = readCsvFile(path_to_house_prices_csv_file, start_year, output_housing_price_folder)
    print("Successfully loaded ", path_to_house_prices_csv_file)

    # Substitude missing data with guessed ones
    end_year = 2023
    data_name = "House Price (in euros)"
    house_prices_years = substituteMissingDataWithGuessedOne(house_prices_years, data_name, output_housing_price_folder, start_year, end_year)

    for year_idx in range(1):    
        house_prices_per_year = house_prices_years[year_idx]
        year = start_year + year_idx
        print("--------{}".format(year))

        # Prepare output housing price folder
        output_housing_price_folder_per_year = "Output/Housing_Prices/" + str(year)
        CreateOutputFolderIfNeeded(output_housing_price_folder_per_year)

        # Export data (i.e house price per municipality) to file
        field_names = ['Regions', data_name]
        exportDataToCSVFile(house_prices_per_year.items(), field_names, output_housing_price_folder_per_year + "/" + data_name + "_" + str(year) + ".csv", 'w')

        # Export municipalities with most expensive house prices
        most_expensive_municipalities = {key:val for key, val in house_prices_per_year.items() if val >= 500000}
        exportDataToCSVFile(most_expensive_municipalities.items(), field_names, output_housing_price_folder_per_year + "/most_expensive_" + data_name + "_" + str(year) + ".csv", 'w')

        top_ten_least_expensive_municipalities = sorted(house_prices_per_year.items(), key=lambda item: item[1])[:5]
        exportDataToCSVFile(top_ten_least_expensive_municipalities, field_names, output_housing_price_folder_per_year + "/top_five_least_expensive_" + data_name + "_" + str(year) + ".csv", 'w')

        top_ten_most_expensive_municipalities = sorted(house_prices_per_year.items(), key=lambda item: item[1], reverse = True)[:5]
        exportDataToCSVFile(top_ten_most_expensive_municipalities, field_names, output_housing_price_folder_per_year + "/top_five_most_expensive_" + data_name + "_" + str(year) + ".csv", 'w')

        # Keep only municipalities with housing prices 
        municipalities_polygons_with_house_prices = getMunicipalitiesPolygonsWithData(path_to_shape_file, year, house_prices_per_year, data_name, output_housing_price_folder, True)
        print("Successfully loaded ", path_to_shape_file)

        # Show municipalities in map. Only municipalities with housing prices will be shown.
        showMunicipalitiesInMap(municipalities_polygons_with_house_prices, data_name, output_housing_price_folder_per_year, year)

        id_variable = "GM_CODE"
        islands = getIslandFromQueenWeightMatrix(municipalities_polygons_with_house_prices, id_variable)
        print ("Islands found in Queen spatial matrix {}. Removing islands from the geometry.".format(islands))
        municipalities_polygons_with_house_prices_without_islands = municipalities_polygons_with_house_prices.drop(islands).reset_index(drop=True)

        # Main part: calculate Global Moran I value
        queen_spatial_weight_matrix = calculateQueenWeightMatrix(municipalities_polygons_with_house_prices_without_islands, data_name, id_variable, output_housing_price_folder, year)
        calculateGlobalMoranI(municipalities_polygons_with_house_prices_without_islands, queen_spatial_weight_matrix, data_name, id_variable, output_housing_price_folder, year)

        # Main part: calculate local Moran I value
        local_moran_result = calculateLocalMoranI(municipalities_polygons_with_house_prices_without_islands, queen_spatial_weight_matrix, data_name, id_variable, output_housing_price_folder, year)

        #municipalities_polygons_with_house_prices_for_folium_map = getMunicipalitiesPolygonsWithData(path_to_shape_file, year, house_prices_per_year, data_name, output_housing_price_folder, False)
        #islands_using_default_index = getIslandFromQueenWeightMatrix(municipalities_polygons_with_house_prices_without_islands, "", "", year)

        #municipalities_polygons_with_house_prices_for_folium_map_without_islands = municipalities_polygons_with_house_prices_for_folium_map.drop(islands_using_default_index)
        exportFoliumLisaMap(municipalities_polygons_with_house_prices_without_islands, data_name, local_moran_result, output_housing_price_folder_per_year, year)