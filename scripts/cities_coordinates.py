import pandas as pd

data = pd.read_csv('../../data/DE/DE.txt', sep='\t', names = ['geonameid', 'name', 'asciiname', 'alternatenames', 'latitude', 'longitude', \
                                                              'featureclass', 'featurecode', 'countrycode', 'alternatecountrycode', \
                                                              'admin1code', 'admin2code', 'admin3code', 'admin4code', \
                                                              'population', 'elevation', 'dem', 'timezone', 'modification date'])

# feature classes:
# A: country, state, region,...
# H: stream, lake, ...
# L: parks,area, ...
# P: city, village,...
# R: road, railroad
# S: spot, building, farm
# T: mountain,hill,rock,...
# U: undersea
# V: forest,heath,...

print(data.head())

# def get_coordinates(arr):
#     for city in arr:
#         data.loc[]