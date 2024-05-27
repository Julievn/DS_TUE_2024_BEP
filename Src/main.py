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

    old_municipalities_lists = [
        ["Aalburg", "Werkendam", "Woudrichem"], [
            "Bedum", "De Marne", "Eemsmond", "Winsum"], ["Beemster"],
        ["Bellingwedde", "Vlagtwedde"], ["het Bildt", "Franekeradeel",
                                         "Menameradiel"], ["Binnenmaas", "Cromstrijen", "Korendijk", "Oud-Beijerland", "Strijen"], ["Ten Boer"],
        ["Boxmeer", "Cuijk", "Sint Anthonis", "Mill en Sint Hubert", "Grave"],
        ["Dongeradeel", "Ferwerderadiel", "Kollumerland en Nieuwkruisland"],
        ["Geldermalsen", "Neerijnen", "Lingewaal"],
        ["Grootegast", "Marum", "Leek", "Zuidhorn"],
        ["Heerhugowaard", "Langedijk"],
        ["Hoogezand-Sappemeer", "Slochteren", "Menterwolde"],
        ["Landerd", "Uden"],
        ["Leerdam", "Vianen", "Zederik"],
        ["Appingedam", "Delfzijl", "Loppersum"],
        ["Giessenlanden", "Molenwaard"],
        ["Nuth", "Onderbanken", "Schinnen"],
        ["Schijndel", "Veghel", "Sint-Oedenrode"],
        ["Groesbeek"]]
    new_municipality_list = ["Altena", "Het Hogeland", "Purmerend", "Westerwolde", "Waadhoeke", "Hoeksche Waard", "Groningen", "Land van Cuijk",
                             "Noardeast-Fryslân", "West Betuwe", "Westerkwartier", "Dijk en Waard", "Midden-Groningen", "Maashorst", "Vijfheerenlanden", "Eemsdelta", "Molenlanden", "Beekdaelen", "Meierijstad", "Berg en Dal"]
    merged_year_list = [2019, 2019, 2022, 2018, 2018, 2019, 2019, 2022,
                        2019, 2019, 2019, 2022, 2018, 2022, 2019, 2021, 2019, 2019, 2017, 2016]
    merge_mode = 's'

    # Processing house prices
    path_to_house_prices_csv_file = args[3]
    path_to_shape_file = args[5]
    # processHousePrices(path_to_house_prices_csv_file, municipality_name_code_mapping, path_to_shape_file, ignored_municipalities)

    # Processing immigration
    path_to_immigration_csv_file = args[7]
    processImmigration(path_to_immigration_csv_file,
                       municipality_name_code_mapping, path_to_shape_file, ignored_municipalities, old_municipalities_lists, new_municipality_list, merged_year_list, merge_mode)


if __name__ == "__main__":
    main()
