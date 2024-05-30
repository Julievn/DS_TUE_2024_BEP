import geopandas as gpd
from matplotlib import colors
import matplotlib.pyplot as plt
import pandas as pd
from mpl_toolkits.axes_grid1 import make_axes_locatable
from splot.esda import moran_scatterplot
from utility import *
import math

important_cities_df = pd.DataFrame(
    {
        "City": ["Amsterdam"],
        "Latitude": [487197.871781],
        "Longitude": [121488.689806]
    }
)

important_cities_gdf = gpd.GeoDataFrame(
    # Amersfoort coordinate system
    important_cities_df, geometry=gpd.points_from_xy(important_cities_df.Longitude, important_cities_df.Latitude), crs="EPSG:28992"
)


def getMoranColors(local_moran_result):
    # Convert all non-significant quadrants to zero
    moran_local_quarants = local_moran_result.q
    moran_local_quarants = np.where(
        local_moran_result.p_sim >= 0.05, 0, moran_local_quarants)

    #  1: "#d7191c", 2: "#89cff0", 3: "#2c7bb6", 4: "#fdae61", 0: "lightgrey"
    #  With: 1 HH, 2 LH, 3 LL, 4 HL
    quarants_colors_mapping = ["lightgrey",
                               "#d7191c", "#89cff0", "#2c7bb6", "#fdae61"]

    # For 2020 year there is no High Low values so the colors messed up.
    # That's why we need to explicity create this color list and assign to each local moran value
    moran_local_colors = []
    for idx in range(len(moran_local_quarants)):
        moran_local_color = quarants_colors_mapping[moran_local_quarants[idx]]
        moran_local_colors.append(moran_local_color)

    return moran_local_colors


def showMunicipalitiesInMap(municipalities_polygons_with_data, data_name, output_folder, year, min_house_price, max_house_price):
    print(type(municipalities_polygons_with_data))
    print(municipalities_polygons_with_data.columns.tolist())

    # Print first 2 cities
    print(municipalities_polygons_with_data.head(2))
    print(municipalities_polygons_with_data.crs)

    # Polygon with data but only 1 color
    base = municipalities_polygons_with_data.plot()
    important_cities_gdf.plot(ax=base, color="red")

    save_plot_file_name = "municipalities_polygon_" + str(year)
    plt.savefig(output_folder + '/' + save_plot_file_name)

    # Only polygon boundaries
    ax = municipalities_polygons_with_data.boundary.plot()
    # Hide all visual components of the x- and y-axis.
    # This sets a flag to suppress drawing of all axis decorations, i.e. axis labels, axis spines, and the axis tick component (tick markers, tick labels, and grid lines).
    ax.set_axis_off()
    save_plot_file_name = "municipalities_polygon_boundaries_" + str(year)
    plt.savefig(output_folder + '/' + save_plot_file_name)

    # Polygon with data with color scale representing different values of data
    # number of rows and columns of the subplot grid
    # Choropleth maps (maps where the color of each shape is based on the value of an associated variable).
    fig, ax = plt.subplots(1, 1)
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("bottom", size="5%", pad=0.1)
    base = municipalities_polygons_with_data.plot(  # Generate a plot of a GeoDataFrame with matplotlib. If a column is specified, the plot coloring will be based on values in that column.
        # Values are used to color the plot. Ignored if color is also set.
        column=data_name,
        vmin=min_house_price,  # Minimum value of cmap
        vmax=max_house_price,  # Maximum value of cmap
        ax=ax,
        legend=True,
        cax=cax,
        legend_kwds={"label": data_name + " in " +
                     str(year), "orientation": "horizontal"}
    )

    # color if specified, all objects will be colored uniformly.
    ax = important_cities_gdf.plot(ax=base, color="red")
    ax.set_axis_off()

    # Save the current figure
    save_plot_file_name = "choropleth_map_" + data_name + "_" + str(year)
    plt.savefig(output_folder + '/' + save_plot_file_name)
    plt.cla()
    plt.close(fig)


def exportChoroplethMapsAllYears(municipalities_polygons_with_data_list, data_name, output_folder, min_house_price, max_house_price):
    # Polygon with data with color scale representing different values of data
    # number of rows and columns of the subplot grid
    # Choropleth maps (maps where the color of each shape is based on the value of an associated variable).
    num_rows = 4
    num_columns = 3

    # figsize: The size of the entire figure containing the subplots can be adjusted using the figure
    # (figsize=(width, height)) function, where width and height are in inches.
    # This indirectly changes the size of the subplots.
    # This will create larger subplots, but they will still have the same proportions.
    fig, ax = plt.subplots(4, 3, sharex=True, sharey=True, figsize=(15, 20),
                           gridspec_kw={
                           'width_ratios': [5, 5, 5],
                           'height_ratios': [5, 5, 5, 5],
                           'wspace': 0,
                           'hspace': 0})

    row = 0
    column = 0
    print("range is {}".format(
        range(len(municipalities_polygons_with_data_list))))
    for idx in range(len(municipalities_polygons_with_data_list)):
        row = int(idx / num_columns)
        column = idx % num_columns

        municipalities_polygons_with_data = municipalities_polygons_with_data_list[
            idx]
        base = municipalities_polygons_with_data.plot(  # Generate a plot of a GeoDataFrame with matplotlib. If a column is specified, the plot coloring will be based on values in that column.
            # Values are used to color the plot. Ignored if color is also set.
            column=data_name,
            vmin=min_house_price,  # Minimum value of cmap
            vmax=max_house_price,  # Maximum value of cmap
            ax=ax[row][column],
            figsize=[20, 10]
        )
        ax[row][column].set_axis_off()
        ax[row][column].set_title(
            str(getStartYear() + idx), y=-0.01, fontsize=10)

        # mark red point as Amsterdam by puting this layer on top of housing price layer
        # color if specified, all objects will be colored uniformly.
        important_city_ax = important_cities_gdf.plot(ax=base, color="red")
        important_city_ax.set_axis_off()

    for current_row in range(row, num_rows):
        for next_removed_column in range(column + 1, num_columns):
            print("Removing current_row {}, next_column {}".format(
                current_row, next_removed_column))
            fig.delaxes(ax[current_row][next_removed_column])

      # Add a colorbar on the right of the subplots
    cbar = fig.colorbar(ax[row][column].collections[0], ax=ax,
                        orientation='vertical', fraction=0.05, pad=0.1)

    fig.suptitle(data_name + " for all years", fontsize=16)

    save_plot_file_name = "choropleth_map_" + data_name + "_all_years"
    plt.savefig(output_folder + '/' + save_plot_file_name)
    plt.cla()
    plt.close(fig)


def exportScatterPlotsAllYears(municipalities_polygons_with_data_list, data_name, local_moran_results_list, output_folder):
    # Polygon with data with color scale representing different values of data
    # number of rows and columns of the subplot grid
    # Choropleth maps (maps where the color of each shape is based on the value of an associated variable).
    num_columns = 3
    num_rows = math.ceil(
        len(municipalities_polygons_with_data_list) / num_columns)

    # figsize: The size of the entire figure containing the subplots can be adjusted using the figure
    # (figsize=(width, height)) function, where width and height are in inches.
    # This indirectly changes the size of the subplots.
    # This will create larger subplots, but they will still have the same proportions.
    width_each_sub_plot = 5
    fig, ax = plt.subplots(num_rows, num_columns, sharex=True, sharey=True, figsize=(width_each_sub_plot * num_columns, width_each_sub_plot * num_rows),
                           gridspec_kw={
                           'width_ratios': [width_each_sub_plot] * num_columns,
                           'height_ratios': [width_each_sub_plot] * num_rows,
                           'wspace': 0.05,
                           'hspace': 0})

    row = 0
    column = 0
    for year_idx in range(len(municipalities_polygons_with_data_list)):
        row = int(year_idx / num_columns)
        column = year_idx % num_columns

        municipalities_polygons_with_data = municipalities_polygons_with_data_list[year_idx]
        local_moran_result = local_moran_results_list[year_idx]

        # Convert all non-significant quadrants to zero
        moran_local_quarants = local_moran_result.q
        moran_local_quarants = np.where(
            local_moran_result.p_sim >= 0.05, 0, moran_local_quarants)

        #  1: "#d7191c", 2: "#89cff0", 3: "#2c7bb6", 4: "#fdae61", 0: "lightgrey"
        #  With: 1 HH, 2 LH, 3 LL, 4 HL
        quarants_colors_mapping = ["lightgrey",
                                   "#d7191c", "#89cff0", "#2c7bb6", "#fdae61"]

        # For 2020 year there is no High Low values so the colors messed up.
        # That's why we need to explicity create this color list and assign to each local moran value
        moran_local_colors = []
        for idx in range(len(moran_local_quarants)):
            moran_local_color = quarants_colors_mapping[moran_local_quarants[idx]]
            moran_local_colors.append(moran_local_color)

        moran_local_colors = getMoranColors(local_moran_result)

        print("Exporting scatter plots all years with local Moran quadrants size = {}, p_sim = {}, colors size = {}".format(
            len(local_moran_result.q), len(local_moran_result.p_sim), len(moran_local_colors)))
        print("Exporting scatter plots all years with local Moran quadrants = {}".format(
            moran_local_quarants))
        print("Exporting scatter plots all years with p_sim = {}".format(
            local_moran_result.p_sim))
        print("Exporting scatter plots all years with colors = {}".format(
            moran_local_colors))

        # ax: Matplotlib Axes instance, optional
        # If given, the Moran plot will be created inside this axis. Default =None.
        sub_fig, sub_ax = moran_scatterplot(
            local_moran_result, True, p=0.05, ax=ax[row][column], scatter_kwds={'c': moran_local_colors})
        if column == 0:
            sub_ax.set_ylabel('Spatial Lag of ' + data_name)
            sub_ax.set_xlabel("")
        else:
            # sub_ax.set_axis_off()
            ax[row][column].set_axis_off()

        title_sub_plot = str(getStartYear() + year_idx)
        print("year_idx {}".format(year_idx))
        print("getStartYear() {}".format(getStartYear()))
        print("getStartYear() + iyear_idxdx {}".format(getStartYear() + year_idx))
        print("title_sub_plot {}".format(title_sub_plot))
        ax[row][column].set_title(
            title_sub_plot, y=-0.05, fontsize=10)

    for current_row in range(row, num_rows):
        for next_removed_column in range(column + 1, num_columns):
            print("Removing current_row {}, next_column {}".format(
                current_row, next_removed_column))
            fig.delaxes(ax[current_row][next_removed_column])

    fig.suptitle(data_name + " for all years", fontsize=16)

    save_plot_file_name = "local_moran_scatter_plots_" + data_name + "_all_years"
    plt.savefig(output_folder + '/' + save_plot_file_name)
    plt.cla()
    plt.close(fig)


def exportFoliumLisaMap(municipalities_polygons_with_data, data_name, moran_local, output_folder_per_year, year):
    # The epsg:28992 crs is a Amersfoort coordinate reference system used in the Netherlands.
    # As folium (i.e. leaflet.js) by default accepts values of latitude and longitude (angular units) as input,
    # we need to project the geometry to a geographic coordinate system first.
    print("showFoliumLisaMap municipalities_polygons_with_data with crs {}".format(
        municipalities_polygons_with_data.crs))

    municipalities_polygons_with_data = municipalities_polygons_with_data.copy()
    municipalities_polygons_with_geographic_coordianate = municipalities_polygons_with_data.to_crs(
        epsg=4326)  # Use WGS 84 (epsg:4326) as the geographic coordinate system
    print(municipalities_polygons_with_geographic_coordianate.crs)
    print(municipalities_polygons_with_geographic_coordianate.head())

    # A column of dataframe can be assigned values of a numpy array
    # moran_local.q is a numpy array
    municipalities_polygons_with_geographic_coordianate['quadrant'] = moran_local.q
    municipalities_polygons_with_geographic_coordianate['p_sim'] = moran_local.p_sim

    # Convert all non-significant quadrants to zero
    municipalities_polygons_with_geographic_coordianate['quadrant'] = np.where(
        municipalities_polygons_with_geographic_coordianate['p_sim'] >= 0.05, 0, municipalities_polygons_with_geographic_coordianate['quadrant'])

    # Get more informative descriptions
    # With: 1 HH, 2 LH, 3 LL, 4 HL
    # pandas.DataFrame.replace
    # municipalities_polygons_with_geographic_coordianate['quadrant'] is a series in inside DataFrame
    municipalities_polygons_with_geographic_coordianate['quadrant'] = municipalities_polygons_with_geographic_coordianate['quadrant'].replace(
        to_replace={
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
    lisa_folium_map = municipalities_polygons_with_geographic_coordianate.explore(column="quadrant",
                                                                                  cmap=hmap,
                                                                                  legend=True,
                                                                                  tiles="CartoDB positron",
                                                                                  style_kwds={
                                                                                      "weight": 0.5},
                                                                                  legend_kwds={
                                                                                      "caption": "LISA quadrant"},
                                                                                  tooltip=False,
                                                                                  popup=True,
                                                                                  popup_kwds={
                                                                                      "aliases": ["Municipality code", "Municipality", "Water", "Year", data_name, "LISA quadrant", "Pseudo p-value"]
                                                                                  }
                                                                                  )

    lisa_folium_map.save(output_folder_per_year +
                         "/folium_lisa_map_" + str(year) + ".html")
