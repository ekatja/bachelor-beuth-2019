import json
import folium
from folium import plugins
import pandas as pd
import numpy as np
import geopandas as gpd
from pprint import pprint
import xlrd
import requests
import branca
from geojson import Point, Feature
import fiona.crs
# import geojson
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, jsonify
from . import TimeSliderMarker
# from custom_polyline import CustomPolyLine
from . import CustomArcPath

from jinja2 import Template
from branca.colormap import linear

app = Flask(__name__)
app.config.from_object(__name__)

# read configuration file from the environment variable and get the access key
app.config.from_envvar('APP_CONFIG_FILE', silent=True)
# MAPBOX_ACCESS_KEY = app.config['MAPBOX_ACCESS_KEY']

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

@app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r


with open('../../geodata/geo_germany.geojson') as data_file:
    state_geo = json.load(data_file)

#Import data files
df = pd.read_excel('../../clean_data/students_bundesland_gender_foreigner_ws1998_99_ws2016_17.xlsx')
df_un_bl_year = pd.read_excel('../../clean_data/university_bundesland_year.xlsx')
unis = pd.read_excel('../../data/geocoordinate_university.xlsx')
# Study place vs. place where study permition was issued
study_place = pd.read_excel('../../clean_data/students_gender_study_place_vs_study_permission_ws2006_07_ws2017_18.xlsx')

# dataset for tooltips
tooltip =  pd.read_pickle("../../tooltip_geojson.pkl")
tooltip_place_of_study = pd.read_pickle('../../clean_data/tooltip_place_of_study_geojson.pkl')

#Convert dataframe to geodataframe
tooltip_gdf = gpd.GeoDataFrame(tooltip)
tooltip_gdf.crs = fiona.crs.from_epsg(4326)
tooltip_place_of_study_gdf = gpd.GeoDataFrame(tooltip_place_of_study)
tooltip_place_of_study_gdf.crs = fiona.crs.from_epsg(4326)

#Const
MIN_STUDENTS_AMOUNT_ALL_ALL = df['Insgesamt, Insgesamt'].min()

MAX_STUDENTS_AMOUNT_ALL_ALL = df['Insgesamt, Insgesamt'].max()

STATES = np.unique(study_place.Bundesland_Studienort.values)
YEARS_STUDY_PLACE = np.unique(study_place.WS.values)
YEARS = np.unique(df.Semester.values)


# route to the new template and send value from url
@app.route('/map/')
@app.route('/map/<year>')
def map(year='1998/99'):

    df_year = df[df.Semester == year]

    bins = create_bins(MIN_STUDENTS_AMOUNT_ALL_ALL, MAX_STUDENTS_AMOUNT_ALL_ALL, 7)

    create_choropleth(geo_data=state_geo, data=df_year, columns=['Bundesland', 'Insgesamt, Insgesamt'],
                      legend='Studentenanzahl',
                      bins=bins,
                      gethtml=False)

    return render_template('students_state.html', selected_year=year, years=YEARS, page_title='Studierende nach Bundesländer', ds="st_bd")


@app.route('/mapupdate/', methods=['POST'])
def students_state_mapupdate(dataframe='st_bd', year="2016/17", nationality='Insgesamt', gender='Insgesamt'):

    #TODO: a = [v for v in request.form]

    print("Got request",request.form)

    if request.form['dataframe']:
        print("dataframe from form", request.form['dataframe'])
        dataframe = request.form['dataframe']

    if request.form['year']:
        print("year from form", request.form['year'])
        year = request.form['year']

    if request.form['nationality']:
        print('nationality from form', request.form['nationality'])
        nationality = request.form['nationality']

    if request.form['gender']:
        print('gender from form', request.form['gender'])
        gender = request.form['gender']

    if dataframe == 'st_bd':
        df_year = df[df.Semester == year]
        column = nationality + ', ' + gender
        print(column)
        # Create bins for 7 intervals
        min_val = df[column].min()
        max_val = df[column].max()
        print(min_val, max_val)

        bins = create_bins(min_val, max_val, 7)

        map = create_choropleth(geo_data=state_geo, data=df_year, columns=['Bundesland', str(column)],
                                legend='Studentenanzahl',
                                bins=bins,
                                gethtml=True)
        return map
    else:
        return redirect('/university-foundation-year')


@app.route('/newmap/')
def newmap():
    with open('../../geodata/plz-3stellig.geojson') as data_file:
        postal_geo = json.load(data_file)

    m = folium.Map(location=[51, 13], tiles="Openstreetmap", zoom_start=4)

    style = {'fillOpacity': 0.5, 'weight': 0.3, 'fillColor': '#yellow'}

    folium.GeoJson(
        postal_geo,
        name='geojson',
        style_function=lambda x: style
    ).add_to(m)

    folium.LayerControl().add_to(m)
    m.save(outfile='templates/newmap.html')

    return render_template('newmap.html')


# TimeSliderChoroplet
@app.route('/university-foundation-year/')
def timemap():
    style_dict = create_unis_dict(unis)
    create_timemap(state_geo, style_dict, False)
    return render_template('test_uni_year.html', page_title='Hochschulen nach Gründungsjahr', ds="university-foundation-year")

@app.route('/place-of-study/')
def place_of_study(year='2006/2007', state='Berlin', gender='Insgesamt'):

    df_study_place = study_place.loc[(study_place.WS == year) & (study_place.Geschlecht == gender)]
    bins = create_bins(study_place.loc[study_place.Geschlecht == gender][state].min(), study_place.loc[study_place.Geschlecht == gender][state].max(), 7)

    create_connected_map(data=df_study_place, column=state, legend='Studienort', bins=bins, gethtml=False)

    return render_template('test_place_of_study.html',
                           selected_year=year,
                           selected_state = state,
                           states = STATES,
                           years = YEARS_STUDY_PLACE,
                           page_title='Studienort vs. Land des Erwerbs der Hochschulzugangsberechtigung', ds="place-of-study")

@app.route('/study-place-mapupdate/', methods=['POST'])
def study_place_mapupdate(dataframe='place-of-study', year="2017/2018", gender='Insgesamt', state='Berlin'):

    #TODO: a = [v for v in request.form]

    print("Got request",request.form)

    if request.form['dataframe']:
        print("dataframe from form", request.form['dataframe'])
        dataframe = request.form['dataframe']

    if request.form['year']:
        print("year from form", request.form['year'])
        year = request.form['year']

    if request.form['gender']:
        print('gender from form', request.form['gender'])
        gender = request.form['gender']

    if request.form['state']:
        print('state from form', request.form['state'])
        state = request.form['state']

    if dataframe == 'place-of-study':
        column = state
        study_place_year = study_place.loc[(study_place.WS == year) & (study_place.Geschlecht == gender)]

        bins = create_bins(study_place.loc[study_place.Geschlecht == gender][state].min(),
                           study_place.loc[study_place.Geschlecht == gender][state].max(), 7)

        map = create_connected_map(data=study_place_year, column=column,
                                legend='Studienort', bins=bins,
                                gethtml=True)
        return map
    else:
        return redirect('/place-of-study')


def create_connected_map(data, column, legend, bins, gethtml):

    m = folium.Map(location=[52, 13], tiles="Openstreetmap", zoom_start=6)

    folium.Choropleth(
        geo_data=state_geo,
        name='choropleth',
        data=data,
        columns=['Bundesland_Studienort', str(column)],
        key_on='feature.properties.NAME_1',
        fill_color='OrRd',
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name=legend,
        bins=bins,
        highlight=True
    ).add_to(m)

    init_index = 0
    for n, feature in enumerate(state_geo['features']):
        if feature['properties']['NAME_1'] == str(column):
            init_index = n
            break

    for feature in state_geo['features']:
        # print(n, feature['properties']['NAME_1'])
        if feature['properties']['NAME_1'] != str(column):
            # print(feature['properties']['NAME_1'])
            CustomArcPath(state_geo['features'][init_index]['geometry']['coordinates'],
                          feature['geometry']['coordinates'],
                          weight=1,
                          color='red').add_to(m)

    # Add tooltips to each state
    temp = tooltip_place_of_study_gdf.loc[(tooltip_place_of_study_gdf.WS == data.WS.values[0]) & (tooltip_place_of_study_gdf.Geschlecht == data.Geschlecht.values[0])]
    folium.GeoJson(temp,
                   style_function=lambda x: {'fillColor': '#00000000', 'color': '#00000000'},
                   highlight_function=lambda x: {'weight': 2, 'color': 'grey'},
                   tooltip=folium.features.GeoJsonTooltip(fields=['Bundesland_Studienort', str(column)],
                                                          aliases=['Bundesland', 'Studierende'],
                                                          labels=True,
                                                          sticky=True)).add_to(m)

    folium.LayerControl().add_to(m)

    if gethtml:
        print("no html update")
        return m.get_root().render()
    else:
        print("new map.html")
        m.save(outfile='templates/map-place-of-study.html')


@app.route('/test-arcpath')
def create_test():
    m = folium.Map(location=[52, 13], tiles="Openstreetmap", zoom_start=6)


    for feature in state_geo['features']:
        if feature['properties']['NAME_1'] != 'Berlin':
            CustomArcPath(state_geo['features'][2]['geometry']['coordinates'], feature['geometry']['coordinates']).add_to(m)


    return m.get_root().render()

# Create choropleth
def create_choropleth(geo_data, data, columns, legend, bins, gethtml):

    m = folium.Map(location=[52, 13], tiles="Openstreetmap", zoom_start=6)

    folium.Choropleth(
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
    ).add_to(m)

    #Add tooltips to each state
    print(data)
    temp = tooltip_gdf[tooltip_gdf.Semester == data.Semester.values[0]]
    folium.GeoJson(temp,
                   style_function=lambda x: {'fillColor': '#00000000', 'color': '#00000000'},
                   highlight_function=lambda x: {'weight':3, 'color':'black'},
                   tooltip=folium.features.GeoJsonTooltip(fields=columns,
                                                   aliases=['Bundesland', 'Studierende'],
                                                   labels=True,
                                                   sticky=True)).add_to(m)

    folium.LayerControl().add_to(m)
    if gethtml:
        print("no html update")
        return m.get_root().render()
    else:
        print("new map.html")
        m.save(outfile='templates/map.html')


# Create bins for choropleth and round to thousands
def create_bins(start, end, number):
    #TODO add intelligent round option
    bins = []
    step = (end - start) / number
    bins.append(start)
    for n in range(1, number):
        bins.append(round(start + step * n, -3))
    bins.append(end + 1)
    return bins

# Data preparation for TimeSliderChoroplet map
def create_style_dict(data):
    # create color schema for universities
    min_color = data.Anzahl.min()
    max_color = data.Anzahl.max()
    cmap = linear.PuRd_09.scale(min_color, max_color)

    # Create dictionary for styles
    styledata = {}
    styles = pd.DataFrame()

    for country in state_geo.get('features'):
        temp = data.loc[data.Bundesland == country.get('properties').get('NAME_1')]

        for i, row in temp.iterrows():
            new_df = pd.DataFrame(data={'color': [row['Anzahl']], 'opacity': [0.5], 'year': [row['Gründungsjahr']]})
            styles = styles.append(new_df, ignore_index=True)

        styledata[country.get('id')] = styles

    # Set color for quantity
    for country, data in styledata.items():
        data['color'] = data['color'].apply(cmap)
    # Set year as index
    for key in styledata:
        datetime_index = styledata.get(key).year
        styledata.get(key).set_index(datetime_index, inplace=True)

    # Create dictionary with styles for each bundesland
    styledict = {
        str(country): data.to_dict(orient='index') for
        country, data in styledata.items()
    }
    return styledict


# Create dictionary of universities for each year
def create_unis_dict(data):
    unis_dict = {}
    for item in data.itertuples():
        if item.Gründungsjahr in unis_dict.keys():
            unis_dict[item.Gründungsjahr].append({'lat': item.lat, 'lon': item.lon,
                                                  'name': item.Hochschulname, 'typ': item.Hochschultyp})
        else:
            unis_dict[item.Gründungsjahr] = [{'lat': item.lat, 'lon': item.lon,
                                              'name': item.Hochschulname, 'typ': item.Hochschultyp}]
    return unis_dict


# Create TimeSliderMarker map
def create_timemap(geo_data, style_dict, gethtml=False):
    m = folium.Map(location=[51, 13], tiles="Openstreetmap", zoom_start=6)
    g = TimeSliderMarker(
        data=geo_data,
        styledict=style_dict,
    )
    g.add_to(m)

    #Create legend
    legend_html = '''
    <div style ='position: fixed;
    bottom: 30px;
    right: 27%;
    width: 220px;
    height: 120px;
    background-color: white;
    //border: 1px solid grey;
    z-index: 9999;
    font-size: 12px;
    padding: 10px 5px 5px 10px;
    -webkit-box-shadow: 4px 4px 5px 0px rgba(0,0,0,0.5);
    -moz-box-shadow: 4px 4px 5px 0px rgba(0,0,0,0.5);
    box-shadow: 4px 4px 5px 0px rgba(0,0,0,0.5);'>
    <p><b>Legende</b> </p>
    <i class="far fa-circle" style ='color: #d7191c; margin-right: 3px; -webkit-text-stroke: 1px #d7191c;'></i> Universität </br>
    <i class="far fa-circle" style ='color: #fdae61; margin-right: 3px; -webkit-text-stroke: 1px #fdae61;'></i> Fachhochschulen / HAW</br>
    <i class="far fa-circle" style ='color: #5e3c99; margin-right: 3px; -webkit-text-stroke: 1px #5e3c99;'></i> Kunst- und Musikhochschulen</br>
    <i class="far fa-circle" style ='color: #008837; margin-right: 3px; -webkit-text-stroke: 1px #008837;'></i> Hochschulen eigenen Typs</br></div>
    '''

    m.get_root().html.add_child(folium.Element(legend_html))

    if gethtml:
        print("no html update")
        return m.get_root().render()
    else:
        print("timemap.html")
        m.save(outfile='templates/timemap.html')



@app.route('/base')
def base():
    return render_template('test_uni_year.html')