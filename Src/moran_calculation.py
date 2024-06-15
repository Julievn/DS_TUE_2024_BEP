import numpy as np

from libpysal.weights import Queen

# Glocal Moran
from esda.moran import Moran

# Local Moran
from esda.moran import Moran_Local

from splot.esda import moran_scatterplot
from splot.esda import lisa_cluster

from utility import *
from map_visualization import *


import matplotlib.pyplot as plt


def getIslandFromQueenWeightMatrix(municipalities_polygons_with_data, id_variable, output_folder, year):
    if id_variable != "":
        queen_weight_matrix = Queen.from_dataframe(
            municipalities_polygons_with_data, idVariable=id_variable)
    else:
        queen_weight_matrix = Queen.from_dataframe(
            municipalities_polygons_with_data)

    # Visualize the queen matrix
    output_folder = output_folder + '/' + str(year)
    print("Exporting queen spatial weight matrix visualization for year {} to {} ".format(
        year, output_folder))
    fig, axs = plt.subplots(1, 2, figsize=(16, 8))
    for i in range(2):
        ax = municipalities_polygons_with_data.plot(
            edgecolor="k", facecolor="w", ax=axs[i]
        )
        ax.set_axis_off()
        # Plot graph connections
        queen_weight_matrix.plot(
            municipalities_polygons_with_data,
            ax=axs[i],
            edge_kws=dict(color="r", linestyle=":", linewidth=1),
            node_kws=dict(marker=""),
        )

    # Remove the axis
    axs[i].set_axis_off()
    axs[1].axis([-13040000, -13020000, 3850000, 3860000])
    save_plot_file_name = "queen_matrix_visualization_" + str(year)
    plt.savefig(output_folder + '/' + save_plot_file_name)
    plt.cla()
    plt.close(fig)

    print('GM0088 is an island but it has following neighbours {}'.format(
        queen_weight_matrix.neighbors['GM0088']))  # Schiermonnikoog
    print('GM0993 is an island but it has following neighbours {}'.format(
        queen_weight_matrix.neighbors['GM0093']))
    print('GM0996 is an island but it has following neighbours {}'.format(
        queen_weight_matrix.neighbors['GM0096']))
    print('GM0448 is an island but it has following neighbours {}'.format(
        queen_weight_matrix.neighbors['GM0448']))

    print("The following island(s) {} are detected {} ".format(
        type(queen_weight_matrix.islands), queen_weight_matrix.islands))
    queen_weight_matrix.islands.append('GM0088')  # Schiermonnikoog
    queen_weight_matrix.islands.append('GM0096')
    queen_weight_matrix.islands.append('GM0093')
    queen_weight_matrix.islands.append('GM0448')

    print("The following island(s) {} are returned {} ".format(
        type(queen_weight_matrix.islands), queen_weight_matrix.islands))
    return queen_weight_matrix.islands


def calculateQueenWeightMatrix(municipalities_polygons_with_data, data_name, id_variable, output_folder, year):
    # Calculate weight matrix from the GeoDataFrame using Queen approach
    if (id_variable != ""):
        queen_weight_matrix = Queen.from_dataframe(
            municipalities_polygons_with_data, idVariable=id_variable)
    else:
        queen_weight_matrix = Queen.from_dataframe(
            municipalities_polygons_with_data)

    print("Calculate weight matrix for {} with results {} ".format(
        data_name, queen_weight_matrix))

    print(queen_weight_matrix.neighbors)
    # We transform our weights to be row-standardized.
    # Each weight is divided by its row sum (the sum of the weights of all neighboring features).
    # Row standardized weighting is often used with fixed distance neighborhoods and almost always used for neighborhoods
    # based on polygon contiguity.
    queen_weight_matrix.transform = 'r'

    return queen_weight_matrix


def calculateGlobalMoranI(municipalities_polygons_with_data, queen_spatial_weight_matrix, data_name, output_folder, year):
    print("Calculating Global Moran I with {} for the following municipalities".format(
        type(municipalities_polygons_with_data)))
    print(municipalities_polygons_with_data['GM_NAAM'].values)

    # <class 'pandas.core.series.Series'> when used inside this function.
    # Outside this function is numpy array
    print(type(municipalities_polygons_with_data[data_name]))
    print(data_name + " values for year {}".format(year))
    print(municipalities_polygons_with_data[data_name].values)

    # house_prices = cities_polygons_with_house_prices['Average_House_Price'].to_numpy()
    # print(type(house_prices))

    num_permutations = 999
    moran_global = Moran(
        municipalities_polygons_with_data[data_name].values, queen_spatial_weight_matrix, 'R', num_permutations)
    print("Glocal Moran spatial autocorrelation for {} between municipalities".format(data_name))
    print(moran_global)

    # For all municipalities, there is only one average Global Moran’s I value,
    dataset_size = len(municipalities_polygons_with_data['GM_NAAM'].values)
    expect_moran_value = round(-1/(dataset_size - 1), 3)
    print("Expected value of Moran (manual calculation) is {}!".format(
        expect_moran_value))

    # EI (float): expected value under normality assumption
    expected_moran_value_pysal = round(moran_global.EI, 3)
    print("Expected value of Moran (EI) is {}!".format(
        expected_moran_value_pysal))
    print("Global Moran I value = {}!".format(round(moran_global.I, 3)))
    print("Our observed value p = {}, z = {}. So the global I Moran value can be statistically or NOT significant".format(
        moran_global.p_sim, moran_global.z_sim))

    spatial_correlation = None
    if moran_global.I > expect_moran_value:
        spatial_correlation = 'Positve spatial correlations'
        print("Positve spatial correlations!")
    else:
        spatial_correlation = 'Negative spatial correlations'
        print("Negative spatial correlations!")

    moran_file_path = output_folder + 'Global_Moran_I.csv'
    field_names = ['Period', 'Expected Moran Value (self-calculation)', 'Expect Moran Value (from framework)',
                   'Moral Global I', 'Spatial correlation', 'p-value', 'z-score']
    global_moran_i_results = [[year, expect_moran_value, expected_moran_value_pysal, round(moran_global.I, 3), str(
        spatial_correlation), round(moran_global.p_sim, 3), round(moran_global.z_sim, 3)]]
    print(type(global_moran_i_results))

    if year == getStartYear():
        exportDataToCSVFile(global_moran_i_results,
                            field_names, moran_file_path, 'w')
    else:
        exportDataToCSVFile(global_moran_i_results,
                            field_names, moran_file_path, 'a')

    print("Moran EI value{}!".format(moran_global.EI))


def calculateLocalMoranI(municipalities_polygons_with_data, queen_spatial_weight_matrix, data_name, output_folder, year):
    print("municipalities_polygons_with_data is type {}".format(
        type(municipalities_polygons_with_data)))
    print(type(municipalities_polygons_with_data['GM_NAAM'].values))
    print("There is total {} municipalities".format(
        len(municipalities_polygons_with_data['GM_NAAM'].values)))
    print(municipalities_polygons_with_data['GM_NAAM'].values)

    # <class 'pandas.core.series.Series'> when used inside this function.
    # Outside this function is numpy array
    # Variable of interest. Can be house price or immigration.
    print(type(municipalities_polygons_with_data[data_name]))
    print("There is total {} data".format(
        len(municipalities_polygons_with_data[data_name].values)))

    num_permutations = 999
    moran_loc = Moran_Local(
        municipalities_polygons_with_data[data_name].values, queen_spatial_weight_matrix, 'R', num_permutations)
    print("Local Moran spatial autocorrelation for {} between municipalities".format(data_name))
    print(dir(moran_loc))
    print(moran_loc)

    for pos, row in municipalities_polygons_with_data.iterrows():
        if row[2] == "Eindhoven":
            print(row)
            print("index is {}".format(pos))
            print("q (quadrant) value is {}".format(moran_loc.q[pos]))
            print("Eindhoven has p_sim {}".format(moran_loc.p_sim[pos]))

    # We can extract the LISA quadrant along with the p-value from the lisa object
    # Convert all non-significant quadrants (p_sim >= 0.05) to zero
    quadrants = np.where(moran_loc.p_sim >= 0.05, 0, moran_loc.q)

    municipality_labeled_wtih_quadrants = dict(
        zip(municipalities_polygons_with_data['GM_NAAM'].values, quadrants))
    municipality_labeled_wtih_psim = dict(
        zip(municipalities_polygons_with_data['GM_NAAM'].values, moran_loc.p_sim))

    # Export High High
    # With: 1 HH, 2 LH, 3 LL, 4 HL
    data_name = "High_High"
    field_names = ['Municipality', data_name]
    high_high_spots = {
        k: v for k, v in municipality_labeled_wtih_quadrants.items() if v == 1}
    output_folder_per_year = output_folder + '/' + str(year)
    exportDataToCSVFile(high_high_spots.items(
    ), field_names, output_folder_per_year + "/" + data_name + "_" + str(year) + ".csv", 'w')

    # Export Low High
    # With: 1 HH, 2 LH, 3 LL, 4 HL
    data_name = "Low_High"
    field_names = ['Municipality', data_name, 'p_sim']
    low_high_spots = {
        k: v for k, v in municipality_labeled_wtih_quadrants.items() if v == 2}
    low_high_spots_with_p_sims = []
    for low_high_spot in low_high_spots.items():
        municipality_name = low_high_spot[0]
        p_sim = municipality_labeled_wtih_psim[municipality_name]
        low_high_spot_with_p_sim = [municipality_name, low_high_spot[1], p_sim]
        low_high_spots_with_p_sims.append(low_high_spot_with_p_sim)
    exportDataToCSVFile(low_high_spots_with_p_sims, field_names,
                        output_folder_per_year + "/" + data_name + "_" + str(year) + ".csv", 'w')

    # Export Low Low
    # With: 1 HH, 2 LH, 3 LL, 4 HL
    data_name = "Low_Low"
    field_names = ['Municipality', data_name]
    high_high_spots = {
        k: v for k, v in municipality_labeled_wtih_quadrants.items() if v == 3}
    output_folder_per_year = output_folder + '/' + str(year)
    exportDataToCSVFile(high_high_spots.items(
    ), field_names, output_folder_per_year + "/" + data_name + "_" + str(year) + ".csv", 'w')

    # Export High Low - 1 HH, 2 LH, 3 LL, 4 HL
    data_name = "High_Low"
    field_names = ['Municipality', data_name, 'p_sim']
    high_low_spots = {
        k: v for k, v in municipality_labeled_wtih_quadrants.items() if v == 4}
    high_low_spots_with_p_sims = []
    for high_low_spot in high_low_spots.items():
        municipality_name = high_low_spot[0]
        p_sim = municipality_labeled_wtih_psim[municipality_name]
        high_low_spot_with_p_sim = [municipality_name, high_low_spot[1], p_sim]
        high_low_spots_with_p_sims.append(high_low_spot_with_p_sim)
    exportDataToCSVFile(high_low_spots_with_p_sims, field_names,
                        output_folder_per_year + "/" + data_name + "_" + str(year) + ".csv", 'w')

    return moran_loc, municipality_labeled_wtih_quadrants
