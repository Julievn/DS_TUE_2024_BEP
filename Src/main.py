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

    # Processing house prices
    path_to_house_prices_csv_file = args[1]
    path_to_shape_file = args[3] 
    processHousePrices(path_to_house_prices_csv_file, path_to_shape_file)

    # Processing immigration
    path_to_immigration_csv_file = args[5]
    #processImmigration(path_to_immigration_csv_file, path_to_shape_file)
     
if __name__ == "__main__":
    main()    