import json

from branca.element import CssLink, Element, Figure, JavascriptLink, MacroElement  # noqa

from folium.map import Marker

from jinja2 import Template

def path_options(line=False, radius=False, **kwargs):
    """
    Contains options and constants shared between vector overlays
    (Polygon, Polyline, Circle, CircleMarker, and Rectangle).
    Parameters
    ----------
    stroke: Bool, True
        Whether to draw stroke along the path.
        Set it to false to disable borders on polygons or circles.
    color: str, '#3388ff'
        Stroke color.
    weight: int, 3
        Stroke width in pixels.
    opacity: float, 1.0
        Stroke opacity.
    line_cap: str, 'round' (lineCap)
        A string that defines shape to be used at the end of the stroke.
        https://developer.mozilla.org/en-US/docs/Web/SVG/Attribute/stroke-linecap
    line_join: str, 'round' (lineJoin)
        A string that defines shape to be used at the corners of the stroke.
        https://developer.mozilla.org/en-US/docs/Web/SVG/Attribute/stroke-linejoin
    dash_array: str, None (dashArray)
        A string that defines the stroke dash pattern.
        Doesn't work on Canvas-powered layers in some old browsers.
        https://developer.mozilla.org/en-US/docs/Web/SVG/Attribute/stroke-dasharray
    dash_offset:, str, None (dashOffset)
        A string that defines the distance into the dash pattern to start the dash.
        Doesn't work on Canvas-powered layers in some old browsers.
        https://developer.mozilla.org/en-US/docs/Web/SVG/Attribute/stroke-dashoffset
    fill: Bool, False
        Whether to fill the path with color.
        Set it to false to disable filling on polygons or circles.
    fill_color: str, default to `color` (fillColor)
        Fill color. Defaults to the value of the color option.
    fill_opacity: float, 0.2 (fillOpacity)
        Fill opacity.
    fill_rule: str, 'evenodd' (fillRule)
        A string that defines how the inside of a shape is determined.
        https://developer.mozilla.org/en-US/docs/Web/SVG/Attribute/fill-rule
    bubbling_mouse_events: Bool, True (bubblingMouseEvents)
        When true a mouse event on this path will trigger the same event on the
        map (unless L.DomEvent.stopPropagation is used).
    Note that the presence of `fill_color` will override `fill=False`.
    See https://leafletjs.com/reference-1.4.0.html#path
    """

    extra_options = {}
    if line:
        extra_options = {
            'smoothFactor': kwargs.pop('smooth_factor', 1.0),
            'noClip': kwargs.pop('no_clip', False),
        }
    if radius:
        extra_options.update({'radius': radius})

    color = kwargs.pop('color', '#3388ff')
    fill_color = kwargs.pop('fill_color', False)
    if fill_color:
        fill = True
    elif not fill_color:
        fill_color = color
        fill = kwargs.pop('fill', False)

    default = {
        'stroke': kwargs.pop('stroke', True),
        'color': color,
        'weight': kwargs.pop('weight', 3),
        'opacity': kwargs.pop('opacity', 1.0),
        'lineCap': kwargs.pop('line_cap', 'round'),
        'lineJoin': kwargs.pop('line_join', 'round'),
        'dashArray': kwargs.pop('dash_array', None),
        'dashOffset': kwargs.pop('dash_offset', None),
        'fill': fill,
        'fillColor': fill_color,
        'fillOpacity': kwargs.pop('fill_opacity', 0.2),
        'fillRule': kwargs.pop('fill_rule', 'evenodd'),
        'bubblingMouseEvents': kwargs.pop('bubbling_mouse_events', True),
    }
    default.update(extra_options)
    return default


def _parse_options(line=False, radius=False, **kwargs):
    options = path_options(line=line, radius=radius, **kwargs)
    return json.dumps(options, sort_keys=True, indent=2)


class CustomPolyLine(Marker):
    """
    Class for drawing polyline overlays on a map.
    See :func:`folium.vector_layers.path_options` for the `Path` options.
    Parameters
    ----------
    locations: list of points (latitude, longitude)
        Latitude and Longitude of line (Northing, Easting)
    popup: str or folium.Popup, default None
        Input text or visualization for object displayed when clicking.
    tooltip: str or folium.Tooltip, default None
        Display a text when hovering over the object.
    smooth_factor: float, default 1.0
        How much to simplify the polyline on each zoom level.
        More means better performance and smoother look,
        and less means more accurate representation.
    no_clip: Bool, default False
        Disable polyline clipping.
    See https://leafletjs.com/reference-1.4.0.html#polyline
    """

    _template = Template(u"""
            {% macro script(this, kwargs) %}
                var script = document.createElement('script');
                script.type = 'text/javascript';
                script.src = '//unpkg.com/leaflet-arc/bin/leaflet-arc.min.js';    
                console.log(document.head);
                document.head.appendChild(script);

                var {{this.get_name()}} = L.Polyline.Arc(
                    {{this.location}},
                    {{ this.options }}
                    )
                    .addTo({{this._parent.get_name()}});
            {% endmacro %}
            """)  # noqa

    def __init__(self, locations, popup=None, tooltip=None, **kwargs):
        super(CustomPolyLine, self).__init__(location=locations, popup=popup,
                                       tooltip=tooltip)
        self._name = 'CustomPolyLine'
        self.options = _parse_options(line=True, **kwargs)
