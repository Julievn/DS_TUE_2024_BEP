from libpysal.weights import Queen

# Glocal Moran
from esda.moran import Moran

# Local Moran
from esda.moran import Moran_Local
from splot.esda import moran_scatterplot
from splot.esda import lisa_cluster

import matplotlib.pyplot as plt

def calculateGlobalMoranI(cities_polygons_with_data, data_name, output_folder, year):
     # Calculate weight matrix from the GeoDataFrame using Queen approach
    queen_weight_matrix = Queen.from_dataframe(cities_polygons_with_data)

    print(type(cities_polygons_with_data))
    print(type(cities_polygons_with_data['GM_NAAM'].values))
    print(cities_polygons_with_data['GM_NAAM'].values)

    # <class 'pandas.core.series.Series'> when used inside this function.
    # Outside this function is numpy array    
    print(type(cities_polygons_with_data[data_name]))
    print("Housing price values for year {}".format(year))
    print(cities_polygons_with_data[data_name].values)

    # house_prices = cities_polygons_with_house_prices['Average_House_Price'].to_numpy()
    #print(type(house_prices))

    moran_global = Moran(cities_polygons_with_data[data_name].values, queen_weight_matrix)
    print("Glocal Moran spatial autocorrelation for {} between cities".format(data_name))
    print(moran_global)

    # For all municipalities, there is only one average Global Moran’s I value, 
    dataset_size = len(cities_polygons_with_data['GM_NAAM'].values) 
    expect_moran_value = -1/(dataset_size - 1)
    print("Expected value of Moran is {}!".format(expect_moran_value))
    print("Global Moran I value = {}!".format(round(moran_global.I, 3)))

    spatial_correlation = None
    if moran_global.I > expect_moran_value:
        spatial_correlation = 'Positve spatial correlations'
        print("Positve spatial correlations!")
    else:
        spatial_correlation = 'Negative spatial correlations'
        print("Negative spatial correlations!")

    moran_file_path = output_folder + 'Global_Moran_I.txt'
    open_file = open(moran_file_path, "a")

    if year == 2013:
        open_file.write("Period" + "    " + "Expected Moran Value"  + "    " + "Moral Global I"  + "        " + "Spatial correlation")
        open_file.write("\n")

    open_file.write(str(year) + "     " + str(expect_moran_value)  + "    " + str(round(moran_global.I, 3))  + "    " + str(spatial_correlation))
    open_file.write("\n")
    open_file.close()

    print("Moran EI value{}!".format(moran_global.EI))


def calculateLocalMoranI(cities_polygons_with_data, data_name, output_folder, year):
     # Calculate weight matrix from the GeoDataFrame using Queen approach
    queen_weight_matrix = Queen.from_dataframe(cities_polygons_with_data)

    print(type(cities_polygons_with_data))
    print(type(cities_polygons_with_data['GM_NAAM'].values))
    print(cities_polygons_with_data['GM_NAAM'].values)

    # <class 'pandas.core.series.Series'> when used inside this function.
    # Outside this function is numpy array    
    print(type(cities_polygons_with_data[data_name]))
    print(cities_polygons_with_data[data_name].values)

    # house_prices = cities_polygons_with_house_prices['Average_House_Price'].to_numpy()
    #print(type(house_prices))

    moran_loc = Moran_Local(cities_polygons_with_data[data_name].values, queen_weight_matrix)
    print("Local Moran spatial autocorrelation for {} between cities".format(data_name))
    print(moran_loc)

    # for each municipality, there is a relating Local Moran’s I value, 
    # as well as its own variance, z value, expected I, and variance of I
    print("Local Moran EI value{}!".format(moran_loc.EI))

    fig, ax = moran_scatterplot(moran_loc)
    ax.set_xlabel('Cities')
    ax.set_ylabel('Spatial Lag of Cities')
    #plt.show()

    save_plot_file_name = "moran_scatterplot_" + str(year)
    output_folder_per_year = output_folder + '/' + str(year)
    plt.savefig(output_folder_per_year + '/' + save_plot_file_name)

    # Let's now visualize the areas we found to be significant on a map:
    # hotspot cold spot
    lisa_cluster(moran_loc, cities_polygons_with_data, p=0.05, figsize = (9,9))
    save_plot_file_name = "moran_hotspot_" + str(year)
    plt.savefig(output_folder_per_year + '/' + save_plot_file_name)
    #plt.show()