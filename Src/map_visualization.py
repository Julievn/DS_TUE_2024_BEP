import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
from mpl_toolkits.axes_grid1 import make_axes_locatable
from utility import *

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


def exportChoroplethMapsAllYears(municipalities_polygons_with_house_prices_list, data_name, output_folder, min_house_price, max_house_price):
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
        range(len(municipalities_polygons_with_house_prices_list))))
    for idx in range(len(municipalities_polygons_with_house_prices_list)):
        row = int(idx / num_columns)
        column = idx % num_columns

        municipalities_polygons_with_data = municipalities_polygons_with_house_prices_list[
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
