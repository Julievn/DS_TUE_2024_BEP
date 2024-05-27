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


def getIslandFromQueenWeightMatrix(municipalities_polygons_with_data, id_variable):
    if id_variable != "":
        queen_weight_matrix = Queen.from_dataframe(municipalities_polygons_with_data, idVariable=id_variable)
    else:
        queen_weight_matrix = Queen.from_dataframe(municipalities_polygons_with_data)
    return queen_weight_matrix.islands

def calculateQueenWeightMatrix(municipalities_polygons_with_data, data_name, id_variable, output_folder, year):
      # Calculate weight matrix from the GeoDataFrame using Queen approach
    queen_weight_matrix = Queen.from_dataframe(municipalities_polygons_with_data, idVariable='GM_CODE')

    print("Calculate weight matrix for {} ".format(data_name, queen_weight_matrix))

    # Once we have the set of local authorities that are not an island, we need to re-calculate the weights matrix:
    queen_weight_matrix = Queen.from_dataframe(municipalities_polygons_with_data, idVariable='GM_CODE')

    # Then we transform our weights to be row-standardized.
    # Each weight is divided by its row sum (the sum of the weights of all neighboring features). 
    # Row standardized weighting is often used with fixed distance neighborhoods and almost always used for neighborhoods 
    # based on polygon contiguity.
    queen_weight_matrix.transform = 'r'

    return queen_weight_matrix

def calculateGlobalMoranI(municipalities_polygons_with_data, data_name, id_variable, output_folder, year):
    queen_weight_matrix = calculateQueenWeightMatrix(municipalities_polygons_with_data, data_name, id_variable, output_folder, year)

    print(type(municipalities_polygons_with_data))
    print(type(municipalities_polygons_with_data['GM_NAAM'].values))
    print(municipalities_polygons_with_data['GM_NAAM'].values)

    # <class 'pandas.core.series.Series'> when used inside this function.
    # Outside this function is numpy array    
    print(type(municipalities_polygons_with_data[data_name]))
    print(data_name + " values for year {}".format(year))
    print(municipalities_polygons_with_data[data_name].values)

    # house_prices = cities_polygons_with_house_prices['Average_House_Price'].to_numpy()
    #print(type(house_prices))

    moran_global = Moran(municipalities_polygons_with_data[data_name].values, queen_weight_matrix)
    print("Glocal Moran spatial autocorrelation for {} between municipalities".format(data_name))
    print(moran_global)

    # For all municipalities, there is only one average Global Moran’s I value, 
    dataset_size = len(municipalities_polygons_with_data['GM_NAAM'].values) 
    expect_moran_value = -1/(dataset_size - 1)
    print("Expected value of Moran is {}!".format(expect_moran_value))
    print("Global Moran I value = {}!".format(round(moran_global.I, 3)))
    print("Our observed value p = {}, z = {}. So the global I Moran value can be statistically or NOT significant".format(moran_global.p_sim, moran_global.z_sim))

    spatial_correlation = None
    if moran_global.I > expect_moran_value:
        spatial_correlation = 'Positve spatial correlations'
        print("Positve spatial correlations!")
    else:
        spatial_correlation = 'Negative spatial correlations'
        print("Negative spatial correlations!")

    moran_file_path = output_folder + 'Global_Moran_I.csv'
    field_names = ['Period', 'Expected Moran Value', 'Moral Global I', 'Spatial correlation', 'p-value', 'z-score']
    global_moran_i_results = [[year, expect_moran_value, round(moran_global.I, 3), str(spatial_correlation), moran_global.p_sim, moran_global.z_sim]]
    print(type(global_moran_i_results))
    exportDataToCSVFile(global_moran_i_results, field_names, moran_file_path, 'w')

    print("Moran EI value{}!".format(moran_global.EI))

def exportFoliumLisaMap(municipalities_polygons_with_data, data_name, moran_local, output_folder_per_year, year):
    # The epsg:28992 crs is a Amersfoort coordinate reference system used in the Netherlands. 
    # As folium (i.e. leaflet.js) by default accepts values of latitude and longitude (angular units) as input, 
    # we need to project the geometry to a geographic coordinate system first.
    print ("showFoliumLisaMap municipalities_polygons_with_data with crs {}".format(municipalities_polygons_with_data.crs))

    municipalities_polygons_with_data = municipalities_polygons_with_data.copy()
    municipalities_polygons_with_geographic_coordianate = municipalities_polygons_with_data.to_crs(epsg=4326) # Use WGS 84 (epsg:4326) as the geographic coordinate system
    print(municipalities_polygons_with_geographic_coordianate.crs)
    print(municipalities_polygons_with_geographic_coordianate.head())

    municipalities_polygons_with_geographic_coordianate['quadrant'] = moran_local.q
    municipalities_polygons_with_geographic_coordianate['p_sim'] = moran_local.p_sim

    # Convert all non-significant quadrants to zero
    municipalities_polygons_with_geographic_coordianate['quadrant'] = np.where(municipalities_polygons_with_geographic_coordianate['p_sim'] >= 0.05, 0, municipalities_polygons_with_geographic_coordianate['quadrant'])

    # Get more informative descriptions
    # With: 1 HH, 2 LH, 3 LL, 4 HL
    municipalities_polygons_with_geographic_coordianate['quadrant'] = municipalities_polygons_with_geographic_coordianate['quadrant'].replace(
    to_replace = {
            0: "Insignificant",
            1: "High-High",
            2: "Low-High",
            3: "Low-Low",
            4: "High-Low"
        }
    )

    print(municipalities_polygons_with_geographic_coordianate.head())

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

    x = municipalities_polygons_with_geographic_coordianate["quadrant"].values
    y = np.unique(x)
    colors5 = [colors5_mpl[i] for i in y]  # for mpl
    hmap = colors.ListedColormap(colors5)

    # Build a LISA cluster map 
    lisa_folium_map = municipalities_polygons_with_geographic_coordianate.explore(column = "quadrant", 
                 cmap = hmap,
                 legend = True, 
                 tiles = "CartoDB positron", 
                 style_kwds = {"weight": 0.5}, 
                 legend_kwds = { "caption": "LISA quadrant"}, 
                 tooltip = False, 
                 popup = True,
                 popup_kwds = {
                    "aliases": ["Municipality code", "Municipality", "Water", "Year", data_name, "LISA quadrant", "Pseudo p-value"]
                 }
                 )
    
    lisa_folium_map.save(output_folder_per_year + "/folium_lisa_map_" + str(year) + ".html")


def calculateLocalMoranI(municipalities_polygons_with_data, data_name, id_variable, output_folder, year):
    queen_weight_matrix = calculateQueenWeightMatrix(municipalities_polygons_with_data, data_name, id_variable, output_folder, year)

    print("municipalities_polygons_with_data is type {}".format(type(municipalities_polygons_with_data)))
    print(type(municipalities_polygons_with_data['GM_NAAM'].values))
    print("There is total {} municipalities".format(len(municipalities_polygons_with_data['GM_NAAM'].values)))
    print(municipalities_polygons_with_data['GM_NAAM'].values)

    # <class 'pandas.core.series.Series'> when used inside this function.
    # Outside this function is numpy array    
    # Variable of interest. Can be house price or immigration.
    print(type(municipalities_polygons_with_data[data_name]))
    print("There is total {} data".format(len(municipalities_polygons_with_data[data_name].values)))
    #print(cities_polygons_with_data[data_name].values)

    num_permutations = 99
    moran_loc = Moran_Local(municipalities_polygons_with_data[data_name].values, queen_weight_matrix, 'R', num_permutations)
    print("Local Moran spatial autocorrelation for {} between municipalities".format(data_name))
    print(dir(moran_loc))
    print(moran_loc)
    #print(moran_loc.__dict__)

    for pos, row in municipalities_polygons_with_data.iterrows():
        print("calculateLocalMoranI id = {} with code {} p_sim original {}; q quadrant original {}".format(pos, row[1], moran_loc.p_sim[pos], moran_loc.q[pos]))

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
    fig, ax = lisa_cluster(moran_loc, municipalities_polygons_with_data, p=0.05, figsize = (9,9))
    ax.set_title(str(year))
    save_plot_file_name = "moran_hotspot_" + str(year)
    plt.savefig(output_folder_per_year + '/' + save_plot_file_name)
    #plt.show()

    for pos, row in municipalities_polygons_with_data.iterrows():
        if row[2] == "Eindhoven":
            print(row)
            print("index is {}".format(pos))
            print("q (quadrant) value is {}".format(moran_loc.q[pos]))
            print ("Eindhoven has p_sim {}".format(moran_loc.p_sim[pos]))

    # We can extract the LISA quadrant along with the p-value from the lisa object
    # Convert all non-significant quadrants (p_sim >= 0.05) to zero
    quadrants = np.where(moran_loc.p_sim >= 0.05, 0, moran_loc.q)

    municipality_labeled_wtih_quadrants = dict(zip(municipalities_polygons_with_data['GM_NAAM'].values, quadrants))
    municipality_labeled_wtih_psim = dict(zip(municipalities_polygons_with_data['GM_NAAM'].values, moran_loc.p_sim))

    # Export High High 
    # With: 1 HH, 2 LH, 3 LL, 4 HL
    data_name = "High_High"
    field_names = ['Municipality', data_name]
    high_high_spots = {k: v for k, v in municipality_labeled_wtih_quadrants.items() if v == 1}
    exportDataToCSVFile(high_high_spots.items(), field_names, output_folder_per_year + "/" + data_name + "_" + str(year) + ".csv", 'w')

    # Export Low High 
    # With: 1 HH, 2 LH, 3 LL, 4 HL
    data_name = "Low_High"
    field_names = ['Municipality', data_name, 'p_sim']
    low_high_spots = {k: v for k, v in municipality_labeled_wtih_quadrants.items() if v == 2}
    low_high_spots_with_p_sims = []
    for low_high_spot in low_high_spots.items():
        municipality_name = low_high_spot[0]
        p_sim = municipality_labeled_wtih_psim[municipality_name]
        low_high_spot_with_p_sim = [municipality_name, low_high_spot[1], p_sim]
        low_high_spots_with_p_sims.append(low_high_spot_with_p_sim)
    exportDataToCSVFile(low_high_spots_with_p_sims, field_names, output_folder_per_year + "/" + data_name + "_" + str(year) + ".csv", 'w')

    # Export High Low - 1 HH, 2 LH, 3 LL, 4 HL
    data_name = "High_Low"
    field_names = ['Municipality', data_name, 'p_sim']
    high_low_spots = {k: v for k, v in municipality_labeled_wtih_quadrants.items() if v == 4}
    high_low_spots_with_p_sims = []
    for high_low_spot in high_low_spots.items():
        municipality_name = high_low_spot[0]
        p_sim = municipality_labeled_wtih_psim[municipality_name]
        high_low_spot_with_p_sim = [municipality_name, high_low_spot[1], p_sim]
        high_low_spots_with_p_sims.append(high_low_spot_with_p_sim)
    exportDataToCSVFile(high_low_spots_with_p_sims, field_names, output_folder_per_year + "/" + data_name + "_" + str(year) + ".csv", 'w')

    return moran_loc