import time
from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent="txn-intelligence-app")
OSM_CACHE = {}

def osm_reverse_geocode(lat, lon):
    key = (round(lat,4), round(lon,4))
    if key in OSM_CACHE:
        return OSM_CACHE[key]

    try:
        loc = geolocator.reverse((lat, lon), exactly_one=True, timeout=10)
        time.sleep(1)

        if not loc:
            return {}

        raw = loc.raw
        address = raw.get("address", {})

        result = {
            "business_name": raw.get("name"),
            "osm_category": (
                address.get("amenity")
                or address.get("shop")
                or address.get("tourism")
                or address.get("office")
            ),
            "address": raw.get("display_name"),
            "place_id": raw.get("place_id")
        }

        OSM_CACHE[key] = result
        return result

    except:
        return {}
