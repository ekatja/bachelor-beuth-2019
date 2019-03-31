# Import required modules
import json

import folium
import numpy as np
import pandas as pd
from bokeh.core.properties import value
from bokeh.embed import components
from bokeh.models import ColumnDataSource
from bokeh.models import NumeralTickFormatter
from bokeh.plotting import figure
from bokeh.resources import INLINE
from flask import Flask, request, redirect, render_template, jsonify

# Import local classes
from . import CustomArcPath
from . import TimeSliderMarker

# Init flask application
app = Flask(__name__)
app.config.from_object(__name__)

# TODO add datasets
# DATASETS IMPORTS
#
# df
# df_population
#
with open('dataset/geo_germany.geojson') as data_file:
    state_geo = json.load(data_file)

df = pd.read_pickle("dataset/students_bundesland_gender_foreigner_ws1998_99_ws2016_17.pkl")
df_population = pd.read_pickle("dataset/bevoelkerung_1998_2016.pkl")
df_un_bl_year = pd.read_pickle("dataset/university_bundesland_year.pkl")
unis = pd.read_pickle('dataset/geocoordinate_university.pkl')
hs_list = pd.read_pickle('dataset/hs_liste.pkl')
study_place = pd.read_pickle('dataset/students_gender_study_place_vs_study_permission_ws2006_07_ws2017_18.pkl')

tooltip_gdf = pd.read_pickle("dataset/tooltip_geojson_fiona.pkl")
tooltip_place_of_study_gdf = pd.read_pickle('dataset/tooltip_place_of_study_geojson_fiona.pkl')


# Constants
MIN_STUDENTS_AMOUNT_ALL_ALL = df['Insgesamt, Insgesamt'].min()
MAX_STUDENTS_AMOUNT_ALL_ALL = df['Insgesamt, Insgesamt'].max()
STATES = np.unique(study_place.Bundesland_Studienort.values)
YEARS_STUDY_PLACE = np.unique(study_place.WS.values)
YEARS = np.unique(df.Semester.values)


@app.route('/map/')
def map(year='1998/99'):
    '''
    Route to the url /map/ and render a page with a students-by-states visualization
    '''
    # Get data for default year
    df_year = df[df.Semester == year]

    # Split students numbers into 6 bins for choropleth color scheme creation
    bins = create_bins(df['Insgesamt, Insgesamt'], 6)

    create_choropleth(geo_data=state_geo, data=df_year, columns=['Bundesland', 'Insgesamt, Insgesamt'],
                      legend='Studentenanzahl',
                      bins=bins,
                      gethtml=False)

    table = get_data_for_studens_states_table(dataset=df_population,
                                              dataset2=df_year, year=year[:4], column='Insgesamt, Insgesamt')

    return render_template('students-state.html',
                           year='Wintersemester' + ' ' + year, years=YEARS, gender='',
                           page_title='Studierende nach Bundesländer', ds="st_bd",
                           states=STATES,
                           table=table)


@app.route('/mapupdate/', methods=['POST'])
def students_state_mapupdate(dataframe='st_bd',
                             year="2016/17",
                             nationality='Insgesamt',
                             gender='Insgesamt'):
    '''
    Endpoint for Ajax students-by-state visualization update
    :return JSON Object with data or redirect to university-by-year visualization
    '''

    # Get data according to selected dataset
    if request.form['dataframe']:
        print("dataframe from form", request.form['dataframe'])
        dataframe = request.form['dataframe']

    if dataframe == 'st_bd':

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

        bins = create_bins(df[column], 6)

        map = create_choropleth(geo_data=state_geo, data=df_year, columns=['Bundesland', str(column)],
                                legend='Studentenanzahl',
                                bins=bins,
                                gethtml=True)

        table = get_data_for_studens_states_table(dataset=df_population,
                                                  dataset2=df_year, year=year[:4], column=column)

        return jsonify({'map': map, 'year': year, 'nationality': nationality, 'gender': gender, 'table': table,
                        'bins': [str(i) for i in bins]})

    else:
        return redirect('/university-foundation-year')


@app.route('/university-foundation-year/')
def timemap(year=1386):
    '''
    Route to the URL /university-foundation-year/ and render a page with university-by-year visualization
    '''
    style_dict = create_unis_dict(unis)
    create_timemap(state_geo, style_dict, False)

    # JS and CSS for Bokeh widget
    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()
    script, div = create_graph(unis_dict=style_dict, year=year)

    return render_template('uni-year.html', page_title='Hochschulen nach Gründungsjahr',
                           ds="university-foundation-year",
                           js=js_resources, css=css_resources,
                           script=script, div=div, dict=style_dict)


@app.route('/update-university-foundation-year/', methods=['POST'])
def university_foundation_year_update():
    '''
    Endpoint for Ajax university-by-year visualization update
    :return JSON Object with data
    '''

    if request.form['dataframe']:
        print("dataframe from form", request.form['dataframe'])
        dataframe = request.form['dataframe']

    if request.form['year']:
        print("year from form", request.form['year'])
        year = request.form['year']

    return jsonify(year=year)


@app.route('/place-of-study/')
def place_of_study(year='2006/2007', state='Berlin', gender='Insgesamt'):
    '''
    Route to URL /place-of-study/ and render place-of-study visualization
    '''
    df_study_place = study_place.loc[(study_place.WS == year) & (study_place.Geschlecht == gender)]
    df_study_place_allgender = study_place.loc[(study_place.WS == year)]

    bins = create_bins(study_place.loc[study_place.Geschlecht == gender][state], 6)

    create_connected_map(data=df_study_place, column=state, legend='Studienort', bins=bins, gethtml=False)

    table, total = get_data_for_place_of_study_table(df_study_place, state)

    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()
    script, div = create_hbar(dataset=df_study_place_allgender, state=state)

    return render_template('place-of-study.html',
                           year='Wintersemester' + ' ' + year,
                           selected_state=state,
                           states=STATES,
                           years=YEARS_STUDY_PLACE,
                           page_title='Studienort vs. Land des Erwerbs der HZB', ds="place-of-study",
                           table=table, total=total,
                           js=js_resources, css=css_resources,
                           script=script, div=div)


@app.route('/study-place-mapupdate/', methods=['POST'])
def study_place_mapupdate(dataframe='place-of-study', year="2017/2018", gender='Insgesamt', state='Berlin'):
    '''
    Endpoint for Ajax place-of-study visualization update
    :return JSON Object with data or redirect to university-by-year visualization
    '''

    if request.form['dataframe']:
        dataframe = request.form['dataframe']

    if request.form['year']:
        year = request.form['year']

    if request.form['gender']:
        gender = request.form['gender']

    if request.form['state']:
        state = request.form['state']

    # TODO try catch
    if dataframe == 'place-of-study':
        column = state
        study_place_year = study_place.loc[(study_place.WS == year) & (study_place.Geschlecht == gender)]

        bins = create_bins(study_place.loc[study_place.Geschlecht == gender][state], 6)

        map = create_connected_map(data=study_place_year, column=column,
                                   legend='Studienort', bins=bins,
                                   gethtml=True)

        table, total = get_data_for_place_of_study_table(study_place_year, state)

        return jsonify(
            {'map': map, 'year': year, 'gender': gender, 'state': state, 'table': table, 'total': int(total),
             'bins': [str(i) for i in bins]})
    else:
        # TODO check url
        print('redirecting to place-of-study')
        return redirect('/place-of-study')


def create_connected_map(data, column, legend, bins, gethtml):
    '''
    Create place-of-study map visualization
    '''

    # Create map of Germany
    m = folium.Map(location=[52, 13], tiles="Openstreetmap", zoom_start=6)

    # Create choropleth map and add it to map of Germany
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

    # Create connection lines between states
    init_index = 0
    for n, feature in enumerate(state_geo['features']):
        if feature['properties']['NAME_1'] == str(column):
            init_index = n
            break

    for feature in state_geo['features']:
        if feature['properties']['NAME_1'] != str(column):
            CustomArcPath(state_geo['features'][init_index]['geometry']['coordinates'],
                          feature['geometry']['coordinates'],
                          weight=1,
                          color='#8D5052'
                          ).add_to(m)

    # Create and add tooltips to each state
    temp = tooltip_place_of_study_gdf.loc[(tooltip_place_of_study_gdf.WS == data.WS.values[0]) & (
            tooltip_place_of_study_gdf.Geschlecht == data.Geschlecht.values[0])]
    folium.GeoJson(temp,
                   style_function=lambda x: {'fillColor': '#00000000', 'color': '#00000000'},
                   highlight_function=lambda x: {'weight': 2, 'color': 'grey'},
                   tooltip=folium.features.GeoJsonTooltip(fields=['Bundesland_Studienort', str(column)],
                                                          aliases=['Bundesland', 'Studierende aus ' + str(column)],
                                                          labels=True,
                                                          sticky=False)).add_to(m)
    if gethtml:
        return m.get_root().render()
    else:
        m.save(outfile='templates/map-place-of-study.html')


def create_choropleth(geo_data, data, columns, legend, bins, gethtml):
    '''
    Create a choropleth map with tooltips.
    '''
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

    # Create and add tooltips to each state
    temp = tooltip_gdf[tooltip_gdf.Semester == data.Semester.values[0]]
    folium.GeoJson(temp,
                   style_function=lambda x: {'fillColor': '#00000000', 'color': '#00000000'},
                   highlight_function=lambda x: {'weight': 3, 'color': 'black'},
                   tooltip=folium.features.GeoJsonTooltip(fields=columns,
                                                          aliases=['Bundesland', 'Studierende'],
                                                          labels=True,
                                                          sticky=True)).add_to(m)

    if gethtml:
        return m.get_root().render()
    else:
        m.save(outfile='templates/map.html')


def create_bins(column, number):
    '''
    Create bins for choropleth map. Round bins range to thousands
    :param column: Dataset column to create bins
    :param number: Number of bins
    :return: Array of numbers
    '''
    temp = column.sort_values().values
    bins = [round(x[-1], -3) if x[-1] // 10000 > 0 else round(x[-1], -2) for x in
            np.array_split(temp[:-1], number - 1)]
    bins.insert(0, 0)
    bins.append(round(temp[-1], -3))

    if bins[number] < column.max():
        bins[number] += 1000

    return bins


def create_unis_dict(data):
    '''
    Prepare data for university-by-state visualization
    :return: Dictionary with the list of universities data for each year
    '''
    unis_dict = {}

    # Create dictionary with university foundation year as key and coordinates, name and typ as values
    for item in data.itertuples():
        if item.Gründungsjahr in unis_dict.keys():
            unis_dict[item.Gründungsjahr].append({'lat': item.lat, 'lon': item.lon,
                                                  'name': item.Hochschulname, 'typ': item.Hochschultyp})
        else:
            unis_dict[item.Gründungsjahr] = [{'lat': item.lat, 'lon': item.lon,
                                              'name': item.Hochschulname, 'typ': item.Hochschultyp}]
    return unis_dict



def create_timemap(geo_data, style_dict, gethtml=False):
    '''
    Create university-by-state map visualization with using custom class TimeSliderMarker
    '''
    m = folium.Map(location=[51, 13], tiles="Openstreetmap", zoom_start=6)
    TimeSliderMarker(
        data=geo_data,
        styledict=style_dict,
    ).add_to(m)

    if gethtml:
        print("no html update")
        return m.get_root().render()
    else:
        print("timemap.html")
        m.save(outfile='templates/timemap.html')


def create_graph(unis_dict, year=None):
    '''
    Create line chart for university-by-state visualization using bokeh library
    '''

    if year is not None:
        x = [year - 1, year]
        y = [0, len(unis_dict.get(year))]

    else:
        x = sorted(unis_dict.keys())
        y = accomulate_unis_data(unis_dict)

    TOOLTIPS = [
        ("Jahr", "$x{0}"),
        ("Anzahl", "$y{0}"),
    ]
    source = ColumnDataSource(data=dict(year=x, quantity=y), name='students')

    plot = figure(plot_height=400, plot_width=600,
                  toolbar_location='below',
                  tools='hover, xwheel_zoom, xpan',
                  tooltips=TOOLTIPS,
                  x_range=(1386, 2017),
                  y_range=(0, 400)
                  )

    plot.line(x='year', y='quantity', source=source, line_width=3)

    # Line chart styling options
    plot.title.align = 'center'
    plot.xaxis.axis_label = "Jahr"
    plot.yaxis.axis_label = "Anzahl"
    plot.axis.axis_label_text_font_style = 'normal'

    # Line chart bokeh components
    script, div = components(plot)
    return script, div


@app.route('/bokeh_data/<int:year>', methods=['GET'])
def get_bokeh_data(year):
    '''
    Endpoint for dynamic bokeh line chart and table updates used for university-by-year visualization
    :return JSON Object with data
    '''

    style_dict = create_unis_dict(unis)
    data = {}

    for i, (k, v) in enumerate(style_dict.items()):
        if k <= year:
            data[k] = style_dict[k]

    x = sorted(data.keys())
    y = accomulate_unis_data(data)

    source = ColumnDataSource(data=dict(year=x, quantity=y))

    table_data = get_data_for_uni_table(hs_list)

    resp = {'source': source.to_json(include_defaults=True), 'table': table_data}
    return jsonify(resp)


def accomulate_unis_data(data):
    '''
    Prepare data for line chart.
    Use university foundation year as key, overall number of universities existing to this year as values
    :return: Data in dictionary format
    '''
    dict = {}
    for k in data.keys():
        dict[k] = len(data.get(k))

    s = []
    for i, item in enumerate(sorted(dict.items())):
        if i == 0:
            s.append(item[1])
        else:
            s.append(s[i - 1] + item[1])
    return s


def get_data_for_uni_table(data):
    '''
    Prepare data for table in overlay used by university-by-year visualization
    :return: Data in dictionary format
    '''

    df = data[['Hochschulname', 'Hochschultyp', 'Gründungsjahr']]
    df = df[:-3]
    df.Hochschulname = 1
    table = pd.pivot_table(df, values='Hochschulname', index='Gründungsjahr', columns=['Hochschultyp'], aggfunc=np.sum)
    table = table.fillna(0)
    table = table.rename(columns={"Fachhochschulen / HAW": "hs", "Hochschulen eigenen Typs": "other",
                                  "Kunst- und Musikhochschulen": "kmh", "Universitäten": "uni"})
    table = table.astype(int)
    table.index = table.index.astype(int)
    dict = table.to_dict('index')

    return dict


def get_data_for_studens_states_table(dataset, dataset2, year, column):
    '''
    Prepare data for table in overlay used by students-by-states visualization
    :param dataset: Dataset with population data
    :param dataset2: Dataset with students data
    :param year: Year
    :param column: Column name from dataset2
    :return: List with population and students numbers by state
    '''

    dataset.Jahr = dataset.Jahr.astype(str)

    table = dataset[dataset.Jahr == year].iloc[:, 1:]
    table = table.reset_index(drop=True)

    data = dict(
        states=[state for state in table.columns],
        population=[int(value * 1000) for value in table.loc[0]],
        students_abs=[value for value in dataset2[column]],
    )
    table_data = list(zip(data['states'], data['population'], data['students_abs']))
    print(table_data)

    return table_data


def get_data_for_place_of_study_table(dataset, state_hzb):
    '''
    Prepare data for table in overlay used by state-of-study visualization
    :param dataset: Dataset with students data
    :param state_hzb: Column name for selected state
    :return: List with number of students and total value
    '''

    table_data = list(zip(dataset['Bundesland_Studienort'], dataset[state_hzb]))
    total = dataset[state_hzb].sum()
    return table_data, total


def create_hbar(dataset, state):
    '''
    Create horizontal stacked bar chart for place-of-study visualization using bokeh library
    '''

    # Create subsets of male and female data
    df_m = dataset.loc[dataset.Geschlecht == 'männlich']
    df_w = dataset.loc[dataset.Geschlecht == 'weiblich']

    # Create list of states
    states = np.flip(df_m.Bundesland_Studienort.values, axis=0)

    gender = ["männlich", 'weiblich']

    # Numbers of male and female students for each state
    counts_m = np.flip(df_m[state].values, axis=0)
    counts_w = np.flip(df_w[state].values, axis=0)

    # Create a dictionary with states and numbers of male and female students
    counts = {'states': states,
              'männlich': counts_m,
              'weiblich': counts_w}

    source = ColumnDataSource(counts, name='place-of-study')

    # Create tooltips for stacked bar chart
    TOOLTIPS = [
        ("Bundesland", "@states"),
        ("Studierende, männlich", "@{männlich}{0,0}"),
        ("Studierende, weiblich", "@weiblich{0,0}")
    ]

    plot = figure(y_range=states, plot_height=500, toolbar_location=None,
                  tooltips=TOOLTIPS,
                  x_range=(0, 62000),
                  sizing_mode="scale_width")

    plot.hbar_stack(gender, y='states', height=0.9,
                    color=['#718dbf', '#F37A7E'],
                    source=source,
                    legend=[value(x) for x in gender])

    # Styling options for stacked bar chart
    plot.ygrid.grid_line_color = None
    plot.xaxis[0].formatter = NumeralTickFormatter(format="0,0")
    plot.xaxis.axis_label = "Anzahl"
    plot.axis.major_label_text_font_size = '14px'
    plot.outline_line_color = None
    plot.legend.orientation = "horizontal"

    script, div = components(plot)
    return script, div


# Update horizontal stacked bar chart
@app.route('/bokeh_data_place_of_study/', methods=['GET'])
def get_bokeh_data_place_of_study():
    '''
    Endpoint for dynamic bokeh chart and table update used by place-of-study visualization
    '''

    if request.args['year']:
        year = request.args['year']

    if request.args['state']:
        state_hzb = request.args['state']

    if request.args['gender']:
        gender = request.args['gender']

    # TODO error handling
    dataset = study_place.loc[(study_place.WS == year)]

    # Data subsets split by gender
    df_m = dataset.loc[dataset.Geschlecht == 'männlich']
    df_w = dataset.loc[dataset.Geschlecht == 'weiblich']
    df = dataset.loc[dataset.Geschlecht == gender]

    states = np.flip(df_m.Bundesland_Studienort.values, axis=0)

    counts_m = np.flip(df_m[state_hzb].values, axis=0)
    counts_w = np.flip(df_w[state_hzb].values, axis=0)
    counts = {'states': states,
              'männlich': counts_m,
              'weiblich': counts_w,
              'counts': counts_m + counts_w}

    source = ColumnDataSource(counts)

    table_data, total = get_data_for_place_of_study_table(df, state_hzb)

    return jsonify({'source': source.to_json(include_defaults=True), 'table': table_data, 'total': str(total)})
