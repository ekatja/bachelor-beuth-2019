import json
import folium
import pandas as pd
import xlrd
import requests
from geojson import Point, Feature
# import geojson
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash


app = Flask(__name__)
app.config.from_object(__name__)

# read configuration file from the environment variable and get the access key
app.config.from_envvar('APP_CONFIG_FILE', silent=True)
# MAPBOX_ACCESS_KEY = app.config['MAPBOX_ACCESS_KEY']

YEARS = {
    "WS_1998_99": '1998/99',
    "WS_1999_00": '1999/00',
    "WS_2000_01": '2000/01',
    "WS_2001_02": '2001/02',
    "WS_2002_03": '2001/03',
    "WS_2003_04": '2003/04',
    "WS_2004_05": '2004/05',
    "WS_2005_06": '2005/06',
    "WS_2006_07": '2006/07',
    "WS_2007_08": '2007/08',
    "WS_2008_09": '2008/09',
    "WS_2009_10": '2009/10',
    "WS_2010_11": '2010/11',
    "WS_2011_12": '2011/12',
    "WS_2012_13": '2012/13',
    "WS_2013_14": '2013/14',
    "WS_2014_15": '2014/15',
    "WS_2015_16": '2015/16',
    "WS_2016_17": '2016/17'
}
for key in YEARS:
    print(key)

# geo-coordinate points along the route
ROUTE = [
    {"lat": 52.523, "long": 13.413, 'name': 'Berlin', 'admin1code': ''},
    {"lat": 52.401, "long": 13.049, 'name': 'Potsdam'},
    {"lat": 52.122, "long": 11.619, 'name': 'Magdeburg'},
    {"lat": 51.050, "long": 13.739, 'name': 'Dresden'},
    {"lat": 50.986, "long": 11.002, 'name': 'Erfurt'},
    {"lat": 48.133, "long": 11.567, 'name': 'Muenchen'},
    {"lat": 48.783, "long": 9.183, 'name': 'Stuttgart'},
    {"lat": 50.100, "long": 8.233, 'name': 'Wiesbaden'},
    {"lat": 50.000, "long": 8.267, 'name': 'Mainz'},
    {"lat": 49.233, "long": 7.000, 'name': 'Saarbruecken'},
    {"lat": 51.233, "long": 6.783, 'name': 'Duesseldorf'},
    {"lat": 52.383, "long": 9.733, 'name': 'Hannover'},
    {"lat": 53.083, "long": 8.817, 'name': 'Bremen'},
    {"lat": 53.567, "long": 10.033, 'name': 'Hamburg'},
    {"lat": 54.333, "long": 10.133, 'name': 'Kiel'},
    {"lat": 53.628, "long": 11.412, 'name': 'Schwerin'},
]

# This is the template for the API call:
# https://api.mapbox.com/directions/v5/mapbox/driving/{GEO_COORDINATES_LIST}.json?access_token={MAPBOX_ACCESS_TOKEN}&overview=full&geometries=geojson

# Mapbox driving direction API call
# ROUTE_URL = "https://api.mapbox.com/directions/v5/mapbox/driving/{0}.json?access_token={1}&overview=full&geometries=geojson"
#
# # create the API URL with all of our geo-coordinates and the Mapbox access token
# def create_route_url():
#     # Create a string with all the geo coordinates
#     lat_longs = ";".join(["{0},{1}".format(point["long"], point["lat"]) for point in ROUTE])
#     # Create a url with the geo coordinates and access token
#     url = ROUTE_URL.format(lat_longs, MAPBOX_ACCESS_KEY)
#
#     return url
#
# # use requests to run the API request and return the results as a GeoJSON object
# def get_route_data():
#     # Get the route url
#     route_url = create_route_url()
#     # Perform a GET request to the route API
#     result = requests.get(route_url)
#     # Convert the return value to JSON
#     data = result.json()
#
#     # Create a geo json object from the routing data
#     geometry = data["routes"][0]["geometry"]
#     route_data = Feature(geometry = geometry, properties = {})
#
#     return route_data

with open('../../geo_germany.geojson') as data_file:
    state_geo = json.load(data_file)

df = pd.read_excel('../../clean_data/students_bundesland_gender_foreigner_ws1998_99_ws2016_17.xlsx')

m = folium.Map(location=[52, 13], tiles="Openstreetmap", zoom_start=6)

# print(st_data)
# print(st_data['Insgesamt, Insgesamt'].min(), st_data['Insgesamt, Insgesamt'].max())


def create_choropleth(geo_data, data, columns, legend, bins):

    m.choropleth(
        geo_data=geo_data,
        name='choropleth',
        data=data,
        columns=columns,
        key_on='feature.properties.NAME_1',
        fill_color='OrRd',
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name=legend,
        bins=bins,
        highlight=True
    )

    # for point in range(0, len(coords)):
    #     m.add_child(folium.Marker(location=coords[point], popup=folium.Popup('Hi')))

    folium.LayerControl().add_to(m)
    m.save(outfile='templates/map.html')

# route to the new template and send value from url
@app.route('/map/')
@app.route('/map/<year>')
def mapbox_js(year='WS_1998_99'):
    # route_data = get_route_data()
    df_year = df[df.Semester == year]
    print('year:', year)
    print(df_year['Insgesamt, Insgesamt'].min(), df_year['Insgesamt, Insgesamt'].max())

    create_choropleth(geo_data=state_geo, data=df_year, columns=['Bundesland', 'Insgesamt, Insgesamt'],
                      legend='Studentenanzahl',
                      bins=[df_year['Insgesamt, Insgesamt'].min(), 100000, 200000, 300000, 400000,
                            df_year['Insgesamt, Insgesamt'].max() + 1])

    return render_template('index.html', selected_year=year, years = YEARS)