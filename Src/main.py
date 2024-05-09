import csv
import fiona
import geopandas as gpd
import sys

# Read a csv file containing house prices for all cities in the Netherlands.
# Return a list of dictionaries. Each element is a dictionary. Each dictionary is a list of cities with house prices.
def readCsv(path_to_house_prices_file):
    # create a list of dictionaries. Each element is a dictionary. Each dictionary is a list of cities with house prices.
    average_house_prices_years = [] 
    start_year = 2013

    with open(path_to_house_prices_file, newline='') as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=';', quotechar='|')
        count_house_price_year = 0
        sum_house_prices = 0
        next(csv_reader, None)  # skip the headers
        for row in csv_reader:
            print("--------")       
            if ((len(row) == 3) and (row[2].isdigit())):
                print ("Add a city with house price")
                current_year = int(row[0].replace('"', ''))
                current_city = row[1].replace('"', '')
                current_price = row[2]
                print(current_year)
                print(current_city)
                print(current_price)
                year_idx = current_year -start_year
                if (len(average_house_prices_years) == year_idx):
                    average_house_prices_per_year = {current_city: current_price}
                    average_house_prices_years.append(average_house_prices_per_year)
                else:
                    average_house_prices_per_year = average_house_prices_years[current_year -start_year]
                    average_house_prices_per_year[current_city] = current_price
    return average_house_prices_years

def getCitiesPolygonsWithHousePrices(path_to_shape_file, year, average_house_prices_per_year):
    # kwargs in Python is a special syntax that allows you to pass a keyworded, variable-length argument dictionary to a function. 
    # It is short for "keyword arguments". When defining a function, you can use the ** in front of a parameter to indicate that 
    # it should accept any number of keyword arguments.
    def records(filename, usecols, year, average_house_prices_per_year, **kwargs):
        with fiona.open(filename, **kwargs) as source:
            for feature in source:
                f = {k: feature[k] for k in ['id', 'geometry']}
                f['properties'] = {k: feature['properties'][k] for k in usecols}
                # dictionary with key, value pair. For example, Aa en Hunze -> 213176
                if f['properties']['GM_NAAM'] in average_house_prices_per_year: # only display cities with housing prices
                    print("inside records --- ")
                    city_name = f['properties']['GM_NAAM']
                    print (city_name)
                    print (f)
                    print(f['properties']['GM_NAAM'])
                    print("Keep this row as it has house price")
                    f['properties']['Year'] = year
                    f['properties']['Average_House_Price'] = average_house_prices_per_year[city_name]
                    print("With average house price")
                    print (f)
                    yield f

    cities_polygons = gpd.GeoDataFrame.from_features(records(path_to_shape_file, ['GM_NAAM'], year, average_house_prices_per_year))
    return cities_polygons

def exitProgram():
    print("Exiting the program...")
    sys.exit(1)

def main():
    print("\n----Correlation and Similarities for spatiotemporal data - Housing Prices in the Netherlands-----")
    print("**************************************************************************************************")
    
    # args is a list of the command line args
    args = sys.argv[1:]
    print("Running program {} with value {}; {} with value {} ".format(args[0], args[1], args[2], args[3]))
    if len(args) <= 0 or args[0] != '-house_price_csv' or args[2] != '-path_to_shape_file':
        print("Please use -house_price_csv and -path_to_shape_file as parameters")
        exitProgram()

    path_to_house_prices_csv_file = args[1]
    print("Loading ", path_to_house_prices_csv_file)
    
    average_house_prices_years = readCsv(path_to_house_prices_csv_file)
    print("Successfully loaded ", path_to_house_prices_csv_file)

    # Prepare housing price data per year with geographical boundaries for cities 
    path_to_shape_file = args[3] 
    start_year = 2013
    for year_idx in range(11):    
        average_house_prices_per_year = average_house_prices_years[year_idx]
        year = start_year + year_idx
        print("--------{}".format(year))

         # Only cities with housing prices 
        cities_polygons_with_house_prices = getCitiesPolygonsWithHousePrices(path_to_shape_file, year, average_house_prices_per_year)
        print("Successfully loaded ", path_to_shape_file)

        print(type(cities_polygons_with_house_prices))
        print(cities_polygons_with_house_prices.columns.tolist())

         # Print first 10 cities
        print(cities_polygons_with_house_prices.head(10))

if __name__ == "__main__":
    main()



    