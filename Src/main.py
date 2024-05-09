import csv
import sys

# Read a csv file containing house prices for all cities in the Netherlands.
# Return a list of dictionaries. Each element is a dictionary. Each dictionary is a list of cities with house prices.
def read_csv(path_to_house_prices_file):
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

def main():
    print("----Correlation and Similarities for spatiotemporal data - Housing Prices in the Netherlands-----")
    print("**************************************************************************************************")
    args = sys.argv[1:]
    # args is a list of the command line args
    average_house_prices_years = []
    if len(args) > 0 and args[0] == '-house_price_csv':
        path_to_house_prices_csv_file = args[1]
        print("Loading ", path_to_house_prices_csv_file)
        average_house_prices_years = read_csv(path_to_house_prices_csv_file)
        print("Successfully loaded ", path_to_house_prices_csv_file)
    else:
        print("Please use -house_price_csv as a parameter")

if __name__ == "__main__":
    main()



    