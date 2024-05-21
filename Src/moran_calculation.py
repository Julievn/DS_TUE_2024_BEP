import numpy as np

from libpysal.weights import Queen

# Glocal Moran
from esda.moran import Moran

# Local Moran
from esda.moran import Moran_Local 

from splot.esda import moran_scatterplot
from splot.esda import lisa_cluster

from utility import *

from matplotlib import colors

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

def exportFoliumLisaMap(cities_polygons_with_data, moran_local, output_folder_per_year, year):
    # The epsg:28992 crs is a Amersfoort coordinate reference system used in the Netherlands. 
    # As folium (i.e. leaflet.js) by default accepts values of latitude and longitude (angular units) as input, 
    # we need to project the geometry to a geographic coordinate system first.
    print ("showFoliumLisaMap cities_polygons_with_data with crs {}".format(cities_polygons_with_data.crs))
    cities_polygons_with_data = cities_polygons_with_data.copy()
    cities_polygons_with_geographic_coordianate = cities_polygons_with_data.to_crs(epsg=4326) # Use WGS 84 (epsg:4326) as the geographic coordinate system
    print(cities_polygons_with_geographic_coordianate.crs)
    print(cities_polygons_with_geographic_coordianate.head())

    cities_polygons_with_geographic_coordianate['quadrant'] = moran_local.q
    print("output_folder_per_year is {}".format(output_folder_per_year))
    print("There is total {} quadrants".format(len(cities_polygons_with_geographic_coordianate['quadrant'])))

    cities_polygons_with_geographic_coordianate['p_sim'] = moran_local.p_sim

    # Convert all non-significant quadrants to zero
    cities_polygons_with_geographic_coordianate['quadrant'] = np.where(cities_polygons_with_geographic_coordianate['p_sim'] > 0.05, 0, cities_polygons_with_geographic_coordianate['quadrant'])

    # Get more informative descriptions
    # With: 1 HH, 2 LH, 3 LL, 4 HL
    cities_polygons_with_geographic_coordianate['quadrant'] = cities_polygons_with_geographic_coordianate['quadrant'].replace(
    to_replace = {
            0: "Insignificant",
            1: "High-High",
            2: "Low-High",
            3: "Low-Low",
            4: "High-Low"
        }
    )

    print(cities_polygons_with_geographic_coordianate.head())
    print(type(cities_polygons_with_geographic_coordianate))

    for pos, row in cities_polygons_with_geographic_coordianate.iterrows():
        if row[2] == "Eindhoven":
            print(row)
    def my_colormap(value):  # scalar value defined in 'column'
        if value == 0:
            return "lightgrey"
        elif value == 1:
            return "red"
        elif value == 2:
            return "darkblue"
        elif value == 3:
            return "blue"
        return "orange"

    colors5_mpl = {
        "High-High": "#d7191c",
        "Low-High": "#89cff0",
        "Low-Low": "#2c7bb6",
        "High-Low": "#fdae61",
        "Insignificant": "lightgrey",
    }

    x = cities_polygons_with_geographic_coordianate["quadrant"].values
    y = np.unique(x)
    colors5 = [colors5_mpl[i] for i in y]  # for mpl
    hmap = colors.ListedColormap(colors5)

    # Build a LISA cluster map 
    lisa_folium_map = cities_polygons_with_geographic_coordianate.explore(column = "quadrant", 
                 cmap = hmap,
                 legend = True, 
                 tiles = "CartoDB positron", 
                 style_kwds = {"weight": 0.5}, 
                 legend_kwds = { "caption": "LISA quadrant"}, 
                 tooltip = False, 
                 popup = True,
                 popup_kwds = {
                    "aliases": ["Municipality code", "Municipality", "Water", "Year", "House price", "LISA quadrant", "Pseudo p-value"]
                 })
    
    lisa_folium_map.save(output_folder_per_year + "/folium_lisa_map_" + str(year) + ".html")


def calculateLocalMoranI(cities_polygons_with_data, data_name, output_folder, year):
     # Calculate weight matrix from the GeoDataFrame using Queen approach
    queen_weight_matrix = Queen.from_dataframe(cities_polygons_with_data)

    print(type(cities_polygons_with_data))
    print(type(cities_polygons_with_data['GM_NAAM'].values))
    print("There is total {} cities".format(len(cities_polygons_with_data['GM_NAAM'].values)))
    print(cities_polygons_with_data['GM_NAAM'].values)

    # <class 'pandas.core.series.Series'> when used inside this function.
    # Outside this function is numpy array    
    # Variable of interest. Can be house price or immigration.
    print(type(cities_polygons_with_data[data_name]))
    print("There is total {} data".format(len(cities_polygons_with_data[data_name].values)))
    #print(cities_polygons_with_data[data_name].values)

    moran_loc = Moran_Local(cities_polygons_with_data[data_name].values, queen_weight_matrix)
    print("Local Moran spatial autocorrelation for {} between cities".format(data_name))
    print(dir(moran_loc))
    #print(moran_loc)
    #print(moran_loc.__dict__)

    # for each municipality, there is a relating Local Moran’s I value, 
    # as well as its own variance, z value, expected I, and variance of I
    print("There is total {} Local Moran EI value".format(len(moran_loc.EI)))
    #print("Local Moran EI value{}!".format(moran_loc.EI))

    fig, ax = moran_scatterplot(moran_loc, p=0.05)
    ax.set_xlabel('Housing prices in ' + str(year))
    ax.set_ylabel('Spatial Lag of Housing prices')
    #plt.show()

    save_plot_file_name = "moran_scatterplot_" + str(year)
    output_folder_per_year = output_folder + '/' + str(year)
    plt.savefig(output_folder_per_year + '/' + save_plot_file_name)

    # Let's now visualize the areas we found to be significant on a map:
    # hotspot cold spot
    fig, ax = lisa_cluster(moran_loc, cities_polygons_with_data, p=0.05, figsize = (9,9))
    ax.set_title(str(year))
    save_plot_file_name = "moran_hotspot_" + str(year)
    plt.savefig(output_folder_per_year + '/' + save_plot_file_name)
    #plt.show()

    exportFoliumLisaMap(cities_polygons_with_data, moran_loc, output_folder_per_year, year)

    # We can extract the LISA quadrant along with the p-value from the lisa object
    # Convert all non-significant quadrants to zero
    quadrants = np.where(moran_loc.p_sim > 0.05, 0, moran_loc.q)

    municipality_labeled_wtih_quadrants = dict(zip(cities_polygons_with_data['GM_NAAM'].values, quadrants))

    # Export Low High 
    # With: 1 HH, 2 LH, 3 LL, 4 HL
    data_name = "Low_High"
    field_names = ['Municipality', data_name]
    low_high_spots = {k: v for k, v in municipality_labeled_wtih_quadrants.items() if v == 2}

    exportDataToFile(low_high_spots, field_names, output_folder_per_year + "/" + data_name + "_" + str(year) + ".txt")

    # Export High Low - 1 HH, 2 LH, 3 LL, 4 HL
    data_name = "High_Low"
    field_names = ['Municipality', data_name]
    low_high_spots = {k: v for k, v in municipality_labeled_wtih_quadrants.items() if v == 4}

    exportDataToFile(low_high_spots, field_names, output_folder_per_year + "/" + data_name + "_" + str(year) + ".txt")