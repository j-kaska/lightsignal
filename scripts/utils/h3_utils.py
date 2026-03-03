import h3 as _h3
import importlib.metadata

try:
    _version_str = _h3.__version__
except AttributeError:
    _version_str = importlib.metadata.version('h3')

_H3_VERSION = tuple(int(x) for x in _version_str.split('.')[:2])
_IS_V4 = hasattr(_h3, 'latlng_to_cell')


def latlng_to_cell(lat, lon, resolution):
    if _IS_V4:
        return _h3.latlng_to_cell(lat, lon, resolution)
    else:
        return _h3.geo_to_h3(lat, lon, resolution)


def cell_to_boundary(h3_id):
    if _IS_V4:
        return list(_h3.cell_to_boundary(h3_id))
    else:
        return list(_h3.h3_to_geo_boundary(h3_id))


def cell_to_parent(h3_id, resolution):
    if _IS_V4:
        return _h3.cell_to_parent(h3_id, resolution)
    else:
        return _h3.h3_to_parent(h3_id, resolution)


def polyfill_box(south: float, west: float, north: float, east: float, resolution: int) -> set:
    """
    Returns the set of H3 cell IDs that fill a lat/lng bounding box at the given resolution.
    Works with both h3 v3 and v4.
    """
    if _IS_V4:
        # h3 v4: LatLngPoly takes (lat, lng) tuples, ring must be closed
        poly = _h3.LatLngPoly([
            (north, west), (north, east),
            (south, east), (south, west),
            (north, west),
        ])
        return _h3.h3shape_to_cells(poly, resolution)
    else:
        # h3 v3: polyfill with geo_json_conformant=True expects [lng, lat] order
        geojson = {
            "type": "Polygon",
            "coordinates": [[
                [west, north], [east, north],
                [east, south], [west, south],
                [west, north],
            ]]
        }
        return _h3.polyfill(geojson, resolution, geo_json_conformant=True)


def h3_version():
    return _version_str
