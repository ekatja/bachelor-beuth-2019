# -*- coding: utf-8 -*-

# from __future__ import (absolute_import, division, print_function)

import json

from branca.element import Figure, JavascriptLink

from folium.features import GeoJson

from jinja2 import Template


class TimeSliderMarker(GeoJson):
    """
    Creates a TimeSliderMarker plugin to append into a map with Map.add_child.
    Parameters
    ----------
    data: str
        geojson string
    styledict: dict
        A dictionary where the keys are the geojson feature ids and the values are
        dicts of `{time: style_options_dict}`
    name : string, default None
        The name of the Layer, as it will appear in LayerControls.
    overlay : bool, default False
        Adds the layer as an optional overlay (True) or the base layer (False).
    control : bool, default True
        Whether the Layer will be included in LayerControls.
    show: bool, default True
        Whether the layer will be shown on opening (only for overlays).
    """

    #TODO: Move template to file

    # from jinja2 import Template
    # with open('template.html.jinja2') as file_:
    #     template = Template(file_.read())
    # template.render(name='John')



    _template = Template(u"""
            {% macro script(this, kwargs) %}
            document.addEventListener("DOMContentLoaded", function(event) {
 
                var timestamps = {{ this.timestamps }};
                var styledict = {{ this.styledict }};
                var current_timestamp = timestamps[0];
                
                let markersDict = {};
                let markers;
                
                //console.log(d3.select("#year-slider"));
                // insert time slider
                d3.select("#year-slider").insert("p", ":first-child").append("input")
                    .attr("type", "range")
                    //.attr("width", "100px")
                    .attr("min", 0)
                    .attr("max", timestamps.length - 1)
                    .attr("value", 0)
                    .attr("id", "slider")
                    .attr("step", "1")
                    .style('align', 'center');
                // insert time slider output BEFORE time slider (text on top of slider)
                d3.select("#year-slider").insert("p", ":first-child").append("output")
                    .attr("width", "100")
                    .attr("id", "slider-value")
                    .style('font-size', '18px')
                    .style('text-align', 'center')
                    .style('font-weight', '500%');
                var datestring = current_timestamp.toString();
                d3.select("output#slider-value").text(datestring);
                
                //Create markers 
                create_marker = function(){
                    for (var year in styledict){
                        var markersArr = [];
                        for (var uni in styledict[year]){
                            //Custom popup and markers color
                            let customPopup = styledict[year][uni].name + '</br>'+ 'Gründungsjahr: '+ year;
                            let customColor = styledict[year][uni].typ == 'Universitäten' ? '#d7191c': styledict[year][uni].typ == 'Fachhochschulen / HAW' ? '#fdae61' : styledict[year][uni].typ == 'Kunst- und Musikhochschulen' ? '#5e3c99' : '#008837';
                            markersArr.push(
                                L.circleMarker([styledict[year][uni].lat, styledict[year][uni].lon],
                                            {radius: 5, color: customColor})
                                            .bindPopup(customPopup));
                        }
                        markersDict[year] = markersArr;
                    }
                }
       
                fill_map = function(){
                    map = {{this._parent.get_name()}};
                    markers = markersDict[current_timestamp];
                    markers.forEach(function(element) {
                        element.addTo(map);
                    });  
                    for (var year in markersDict ){
                        if(year > current_timestamp){
                            markers = markersDict[year];
                            markers.forEach(function(element) {
                                element.removeFrom(map);
                            }); 
                        }
                    }
                }
                clear_map = function(){
                    map = {{this._parent.get_name()}};
                    
                    for (var year in markersDict ){
                        if(year > current_timestamp){
                            markers = markersDict[year];
                            markers.forEach(function(element) {
                                element.removeFrom(map);
                            }); 
                        }
                    }
                }
                
                d3.select("#slider").on("input", function() {
                    current_timestamp = timestamps[this.value];
                
                    var datestring = current_timestamp.toString();
                    d3.select("output#slider-value").text(datestring);
                    fill_map();
                    //clear_map();
                });
                
                create_marker();
                fill_map();
                });
            {% endmacro %}
            """)

    def __init__(self, data, styledict, name=None, overlay=True, control=True,
                 show=True):
        super(TimeSliderMarker, self).__init__(data, name=name,
                                               overlay=overlay,
                                               control=control, show=show)
        if not isinstance(styledict, dict):
            raise ValueError('styledict must be a dictionary, got {!r}'.format(styledict))  # noqa


        # Make set of timestamps.
        timestamps = set()
        for key in styledict.keys():
            # print(key)
            timestamps.add(key)
        timestamps = sorted(list(timestamps))

        self.timestamps = json.dumps(timestamps)
        self.styledict = json.dumps(styledict, sort_keys=True, indent=2)

    def render(self, **kwargs):

        super(TimeSliderMarker, self).render(**kwargs)
        figure = self.get_root()

        assert isinstance(figure, Figure), ('You cannot render this Element '
                                            'if it is not in a Figure.')
        figure.header.add_child(JavascriptLink('https://d3js.org/d3.v4.min.js'), name='d3v4')
