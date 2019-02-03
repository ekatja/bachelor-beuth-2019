# -*- coding: utf-8 -*-

# from __future__ import (absolute_import, division, print_function)

import json

from branca.element import Figure, JavascriptLink

from folium import Marker
from folium.vector_layers import path_options

from geojson_utils import centroid

from jinja2 import Template

class CustomArcPath(Marker):
    """
    Class for drawing AntPath polyline overlays on a map.

    See :func:`folium.vector_layers.path_options` for the `Path` options.

    Parameters
    ----------
    locations: list of points (latitude, longitude)
        Latitude and Longitude of line (Northing, Easting)
    popup: str or folium.Popup, default None
        Input text or visualization for object displayed when clicking.
     tooltip: str or folium.Tooltip, optional
        Display a text when hovering over the object.
    **kwargs:
        Polyline and AntPath options. See their Github page for the
        available parameters.

    https://github.com/rubenspgcavalcante/leaflet-ant-path/

    """
    _template = Template(u"""
            {% macro script(this, kwargs) %}
            
            try {
                var from_poly = L.polygon({{this.location[0]}}).addTo({{this._parent.get_name()}});
                var from = from_poly.getBounds().getCenter();
                L.marker([from.lng, from.lat]).addTo({{this._parent.get_name()}});
                }
            catch(err) {
                console.log('location[0] is a point', err);
                var from = {{this.location[0]}};
            }
            try {
                var to_poly = L.polygon({{this.location[1]}}).addTo({{this._parent.get_name()}});
                var to = to_poly.getBounds().getCenter();
                L.marker([to.lng, to.lat]).addTo({{this._parent.get_name()}});
                }
            catch(err) {
                console.log('location[1] is a point', err);
                var to = {{this.location[1]}};
            }
            from_poly.remove();
            to_poly.remove();
            
                {{this.get_name()}} = L.Polyline.Arc(
                  [from.lng, from.lat],
                  [to.lng, to.lat],
                  // from, to,
                  {{ this.options }}
                )
                .addTo({{this._parent.get_name()}});
            {% endmacro %}
            """)  # noqa



    def __init__(self, locations_from, locations_to, popup=None, tooltip=None, **kwargs):

        locations = [locations_from, locations_to]
        # print(locations)

        # if isinstance(locations_from, dict):
        #     locations[0] = self.calculate_centroids(locations_from)
        # elif isinstance(locations_from, list):
        #     locations[0] = locations_from
        # else:
        #     raise ValueError("locations_from of unsupported format", type(locations_from))
        #
        # if isinstance(locations_to, dict):
        #     locations[1] = self.calculate_centroids(locations_to)
        # elif isinstance(locations_to, list):
        #     locations[1] = locations_to
        # else:
        #     raise ValueError("locations_to of unsupported format", type(locations_to))


        super(CustomArcPath, self).__init__(
            location=locations,
            popup=popup,
            tooltip=tooltip,
        )

        self._name = 'CustomArcPath'
        # Polyline + AntPath defaults.
        # print(path_options())
        options = path_options(line=True, **kwargs)
        options.update({
            # 'paused': kwargs.pop('paused', False),
            # 'reverse': kwargs.pop('reverse', False),
            # 'hardwareAcceleration': kwargs.pop('hardware_acceleration', False),
            # 'delay': kwargs.pop('delay', 400),
            # 'dashArray': kwargs.pop('dash_array', [10, 20]),
            'vertices': kwargs.pop('vertices', 200),
            'offset': kwargs.pop('offset', 10),
            # 'weight': kwargs.pop('weight', 5),
            # 'opacity': kwargs.pop('opacity', 0.5),
            # 'color': kwargs.pop('color', '#0000FF'),
            # 'pulseColor': kwargs.pop('pulse_color', '#FFFFFF'),
        })
        self.options = json.dumps(options, sort_keys=True, indent=2)

    def render(self, **kwargs):
        super(CustomArcPath, self).render()

        figure = self.get_root()
        assert isinstance(figure, Figure), ('You cannot render this Element '
                                            'if it is not in a Figure.')

        # figure.header.add_child(
        #     JavascriptLink('https://cdn.jsdelivr.net/npm/leaflet-ant-path@1.1.2/dist/leaflet-ant-path.min.js'),  # noqa
        #     name='antpath',
        # )
        figure.header.add_child(
            JavascriptLink('https://unpkg.com/leaflet-arc/bin/leaflet-arc.min.js'),  # noqa
            name='arcpath',
        )
