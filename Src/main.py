import sys

def main():
    print("----Correlation and Similarities for spatiotemporal data - Housing Prices in the Netherlands-----")
    print("**************************************************************************************************")
    args = sys.argv[1:]
    # args is a list of the command line args
    if len(args) > 0 and args[0] == '-house_price_csv':
        print("Loading ", args[1])
    else:
        print("Please use -house_price_csv as a parameter")

if __name__ == "__main__":
    main()



    