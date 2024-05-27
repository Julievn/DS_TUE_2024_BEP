# local libraries
from house_prices import *
from immigration import *
from moran_calculation import *
from utility import *


def main():
    print("\n----Correlation and Similarities for spatiotemporal data - Housing Prices in the Netherlands-----")
    print("**************************************************************************************************")

    # args is a list of the command line args
    args = getListOfArguments()

    # get municipality code and name mapping
    path_to_name_code_mapping_file = args[1]
    municipality_name_code_mapping = readDictionaryFromCSVFile(
        path_to_name_code_mapping_file)

    # Ignore old muncipalities that parts of them are merged into new ones as the new ones already contain the data
    ignored_municipalities = ["Haaren", "Haarlemmerliede en Spaarnwoude",
                              "Haren", "Leeuwarderadeel", "Littenseradiel", "Noordwijkerhout", "Rijnwaarden", "Weesp", "Millingen aan de Rijn", "Ubbergen"]

    # Processing house prices
    path_to_house_prices_csv_file = args[3]
    path_to_shape_file = args[5]
    # processHousePrices(path_to_house_prices_csv_file, municipality_name_code_mapping, path_to_shape_file, ignored_municipalities)

    # Processing immigration
    path_to_immigration_csv_file = args[7]
    processImmigration(path_to_immigration_csv_file,
                       municipality_name_code_mapping, path_to_shape_file, ignored_municipalities)


if __name__ == "__main__":
    main()
