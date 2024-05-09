# DS_TUE_2024_BEP

# Introduction
This repo contains the source code to load housing prices in the Netherlands from the csv file and calculate the Moran's I values during 11 year period (from 2013 to 2023)

## Table of Contents
- [Features](#features)
- [Prerequisites](#prerequisites)

## Features
- Download housing prices for cities in the Netherland using: https://opendata.cbs.nl/#/CBS/en/dataset/83625ENG
- Download geographic data for cities in the Netherland using: https://www.cbs.nl/nl-nl/dossier/nederland-regionaal/geografische-data/wijk-en-buurtkaart-2023
- Run program with parameters: -house_price_csv and -shapefile pointing to local paths of these downloaded files
```
 python main.py -house_price_csv local_path_to_csv_file -path_to_shape_file local_path_to_geographic_data_folder
```

## Prerequisites
- Python3 installed
- Pysal, pandas and geopandas installed