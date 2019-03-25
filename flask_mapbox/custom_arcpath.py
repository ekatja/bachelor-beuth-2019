# -*- coding: utf-8 -*-


import json

from branca.element import Figure, JavascriptLink
from folium import Marker
from folium.vector_layers import path_options
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
            var uniIcon = L.divIcon({
                html: '<i class="fas fa-university"></i>',
                iconSize: [20,20],
                className: 'customIcon'});
            try {
                var from_poly = L.polygon({{this.location[0]}}).addTo({{this._parent.get_name()}});
                var from = from_poly.getBounds().getCenter();
                L.marker([from.lng, from.lat], {icon: uniIcon}).addTo({{this._parent.get_name()}});
                }
            catch(err) {
                console.log('location[0] is not a point', err);
                var from = {{this.location[0]}};
            }
            try {
                var to_poly = L.polygon({{this.location[1]}}).addTo({{this._parent.get_name()}});
                var to = to_poly.getBounds().getCenter();
                L.marker([to.lng, to.lat], {icon: uniIcon}).addTo({{this._parent.get_name()}});
                }
            catch(err) {
                console.log('location[1] is not a point', err);
                var to = {{this.location[1]}};
            }
            from_poly.remove();
            to_poly.remove();
                
                {{this.get_name()}} = L.polyline(L.Polyline.Arc(
                  [from.lng, from.lat],
                  [to.lng, to.lat],
                  
                )._latlngs, {{ this.options }})
                .addTo({{this._parent.get_name()}}).snakeIn();
            {% endmacro %}
            """)  # noqa



    def __init__(self, locations_from, locations_to, popup=None, tooltip=None, **kwargs):

        locations = [locations_from, locations_to]

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
            'vertices': kwargs.pop('vertices', 100),
            'offset': kwargs.pop('offset', 10),
            'weight': kwargs.pop('weight', 5),
            'color': kwargs.pop('color', 'red'),
        })
        self.options = json.dumps(options, sort_keys=True, indent=2)

    def render(self, **kwargs):
        super(CustomArcPath, self).render()

        figure = self.get_root()
        assert isinstance(figure, Figure), ('You cannot render this Element '
                                            'if it is not in a Figure.')

        figure.header.add_child(
            # JavascriptLink('https://unpkg.com/leaflet-arc/bin/leaflet-arc.min.js'),  # noqa
            JavascriptLink('/static/js/leaflet-arc.min.js'),
            name='arcpath',
        )
        figure.header.add_child(
            JavascriptLink('/static/js/L.Polyline.SnakeAnim.js'),  # noqa
            name='antpath',
        )
