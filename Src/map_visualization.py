import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
from mpl_toolkits.axes_grid1 import make_axes_locatable

def showMunicipalitiesInMap(municipalities_polygons_with_data, data_name, output_folder, year):
    print(type(municipalities_polygons_with_data))
    print(municipalities_polygons_with_data.columns.tolist())

    # Print first 2 cities
    print(municipalities_polygons_with_data.head(2))
    print(municipalities_polygons_with_data.crs)

    important_cities_df = pd.DataFrame(
        {
            "City": ["Amsterdam"],
            "Latitude": [487197.871781],  
            "Longitude": [121488.689806] 
        }
    )

    important_cities_gdf = gpd.GeoDataFrame(
        important_cities_df, geometry=gpd.points_from_xy(important_cities_df.Longitude, important_cities_df.Latitude), crs="EPSG:28992" #Amersfoort coordinate system
    )

    # We can now plot our ``GeoDataFrame``.
    base = municipalities_polygons_with_data.plot()
    important_cities_gdf.plot(ax=base, color="red")

    save_plot_file_name = "cities_polygon_" + str(year)
    plt.savefig(output_folder + '/' + save_plot_file_name)

    ax = municipalities_polygons_with_data.boundary.plot()
    ax.set_axis_off()
    save_plot_file_name = "cities_polygon_boundaries_" + str(year) 
    #plt.show()
    plt.savefig(output_folder + '/' + save_plot_file_name)

    # Plot by data
    fig, ax = plt.subplots(1, 1)
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("bottom", size="5%", pad=0.1)
    base = municipalities_polygons_with_data.plot(
        column=data_name, 
        ax=ax,
        legend=True,
        cax=cax,
        legend_kwds={"label": "House prices in " + str(year), "orientation": "horizontal"}
    )

    important_cities_gdf.plot(ax=base, color="red")

    save_plot_file_name = "choropleth_map_" + data_name + "_" + str(year) 
    plt.savefig(output_folder + '/' + save_plot_file_name)