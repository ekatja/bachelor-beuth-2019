import json
import folium
import pandas as pd
import xlrd
import requests
import branca
from geojson import Point, Feature
# import geojson
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, jsonify
from folium.plugins import TimeSliderChoropleth
from jinja2 import Template
from branca.colormap import linear

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
    "WS_2002_03": '2002/03',
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

df = pd.read_excel('../../clean_data/students_bundesland_gender_foreigner_ws1998_99_ws2016_17.xlsx')
df_un_bl_year = pd.read_excel('../../clean_data/university_bundesland_year.xlsx')

MIN_STUDENTS_AMOUNT = df['Insgesamt, Insgesamt'].min()
MAX_STUDENTS_AMOUNT = df['Insgesamt, Insgesamt'].max()

# print(st_data)
print(df['Insgesamt, Insgesamt'].min(), df['Insgesamt, Insgesamt'].max())


def create_choropleth(geo_data, data, columns, legend, bins, gethtml):
    m = folium.Map(location=[52, 13], tiles="Openstreetmap", zoom_start=6)

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
    if gethtml:
        print("no html update")
        return m.get_root().render()
    else:
        print("new map.html")
        m.save(outfile='templates/map.html')


# route to the new template and send value from url
@app.route('/map/')
@app.route('/map/<year>')
def map(year='WS_1998_99'):
    df_year = df[df.Semester == year]

    create_choropleth(geo_data=state_geo, data=df_year, columns=['Bundesland', 'Insgesamt, Insgesamt'],
                      legend='Studentenanzahl',
                      bins=[MIN_STUDENTS_AMOUNT, 100000, 200000, 300000, 400000, 500000, 600000,
                            MAX_STUDENTS_AMOUNT + 1],
                      gethtml=False)

    return render_template('index.html', selected_year=year, years=YEARS)


@app.route('/mapupdate/', methods=['POST'])
# @app.route('/mapupdate/<year>', methods=['GET'])
def mapupdate(year="WS_2016_17", nationality='Insgesamt', gender='Insgesamt'):
    print(request.form)
    if request.form['year']:
        print("year from form", request.form['year'])
        year = request.form['year']

    if request.form['nationality']:
        print('nationality from form', request.form['nationality'])
        nationality = request.form['nationality']

    if request.form['gender']:
        print('gender from form', request.form['gender'])
        gender = request.form['gender']

    df_year = df[df.Semester == year]
    column = nationality + ', ' + gender

    print(column)
    print(df_year[column].min(), df_year[column].max())

    map = create_choropleth(geo_data=state_geo, data=df_year, columns=['Bundesland', str(column)],
                            legend='Studentenanzahl',
                            bins=[df_year[column].min(), 100000, 200000, 300000, 400000, 500000, 600000,
                                  MAX_STUDENTS_AMOUNT + 1],
                            gethtml=True)
    return map


@app.route('/newmap/')
def newmap():
    with open('../../geodata/plz-3stellig.geojson') as data_file:
        postal_geo = json.load(data_file)

    m = folium.Map(location=[52, 13], tiles="Openstreetmap", zoom_start=4)

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
@app.route('/timemap/')
def timemap():
    style_dict = create_style_dict(df_un_bl_year)
    create_timemap(state_geo, style_dict, True)

    return render_template('timemap.html')


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

# Create TimeSliderChoroplet map
def create_timemap(geo_data, style_dict, gethtml=True):
    m = folium.Map(location=[52, 13], tiles="Openstreetmap", zoom_start=6)
    g = TimeSliderChoropleth(
        data=geo_data,
        styledict=style_dict,
    )

    year_temp = Template(u"""
                {% macro script(this, kwargs) %}
                    var timestamps = {{ this.timestamps }};
                    var styledict = {{ this.styledict }};
                    var current_timestamp = timestamps[0];
                    // insert time slider
                    d3.select("body").insert("p", ":first-child").append("input")
                        .attr("type", "range")
                        .attr("width", "100px")
                        .attr("min", 0)
                        .attr("max", timestamps.length - 1)
                        .attr("value", 0)
                        .attr("id", "slider")
                        .attr("step", "1")
                        .style('align', 'center');
                    // insert time slider output BEFORE time slider (text on top of slider)
                    d3.select("body").insert("p", ":first-child").append("output")
                        .attr("width", "100")
                        .attr("id", "slider-value")
                        .style('font-size', '18px')
                        .style('text-align', 'center')
                        .style('font-weight', '500%');
                    var datestring = current_timestamp.toString();
                    d3.select("output#slider-value").text(datestring);
                    fill_map = function(){
                        for (var feature_id in styledict){
                            let style = styledict[feature_id]//[current_timestamp];
                            var fillColor = 'white';
                            var opacity = 0;
                            if (current_timestamp in style){
                                fillColor = style[current_timestamp]['color'];
                                opacity = style[current_timestamp]['opacity'];
                                d3.selectAll('#feature-'+feature_id
                                ).attr('fill', fillColor)
                                .style('fill-opacity', opacity);
                            }
                        }
                    }
                    d3.select("#slider").on("input", function() {
                        current_timestamp = timestamps[this.value];

                    var datestring = current_timestamp.toString();
                    d3.select("output#slider-value").text(datestring);
                    fill_map();
                    });
                    {% if this.highlight %}
                        {{this.get_name()}}_onEachFeature = function onEachFeature(feature, layer) {
                            layer.on({
                                mouseout: function(e) {
                                if (current_timestamp in styledict[e.target.feature.id]){
                                    var opacity = styledict[e.target.feature.id][current_timestamp]['opacity'];
                                    d3.selectAll('#feature-'+e.target.feature.id).style('fill-opacity', opacity);
                                }
                            },
                                mouseover: function(e) {
                                if (current_timestamp in styledict[e.target.feature.id]){
                                    d3.selectAll('#feature-'+e.target.feature.id).style('fill-opacity', 1);
                                }
                            },
                                click: function(e) {
                                    {{this._parent.get_name()}}.fitBounds(e.target.getBounds());
                            }
                            });
                        };
                    {% endif %}
                    var {{this.get_name()}} = L.geoJson(
                        {% if this.embed %}{{this.style_data()}}{% else %}"{{this.data}}"{% endif %}
                        {% if this.smooth_factor is not none or this.highlight %}
                            , {
                            {% if this.smooth_factor is not none  %}
                                smoothFactor:{{this.smooth_factor}}
                            {% endif %}
                            {% if this.highlight %}
                                {% if this.smooth_factor is not none  %}
                                ,
                                {% endif %}
                                onEachFeature: {{this.get_name()}}_onEachFeature
                            {% endif %}
                            }
                        {% endif %}
                        ).addTo({{this._parent.get_name()}}
                    );
                {{this.get_name()}}.setStyle(function(feature) {feature.properties.style;});
                    {{ this.get_name() }}.eachLayer(function (layer) {
                        layer._path.id = 'feature-' + layer.feature.id;
                        });
                    d3.selectAll('path')
                    .attr('stroke', 'white')
                    .attr('stroke-width', 0.8)
                    .attr('stroke-dasharray', '5,5')
                    .attr('fill-opacity', 0);
                    fill_map();
                {% endmacro %}
                """)
    g._template = year_temp
    g.add_to(m)

    if gethtml:
        print("no html update")
        return m.get_root().render()
    else:
        print("timemap.html")
        m.save(outfile='templates/timemap.html')
