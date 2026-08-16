# django.contrib.gis (GeoDjango)

- **ID:** `contrib-gis`
- **Category:** contrib
- **Source:** §3.2 Contrib Modules
- **Tags:** `gis`, `geodjango`, `spatial`

## Canonical pattern (Django / HTMX / Hyperscript way)
GeoDjango (django.contrib.gis) provides spatial fields (PointField, PolygonField), distance/lookup queries (distance_lte, dwithin), and spatial DB backends for PostGIS. Use it for any geographic data instead of storing raw lat/lng floats and computing distances in Python.

## Typical MVC default (what AI typically generates)
Typical MVC stacks store latitude/longitude decimal columns and write Haversine SQL by hand, or install a geo search package. AI typically generates raw trigonometry SQL or application-side distance loops over all rows.

## Why Django differs
Django's GIS battery wraps PostGIS so distance queries run as indexed SQL, not O(n) application math. It also handles projections/geometry validation that hand-rolled solutions get wrong.

## Example
from django.contrib.gis.db import models as gis_models
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D

class Store(gis_models.Model):
    location = gis_models.PointField()

nearby = Store.objects.filter(
    location__distance_lte=(Point(lng, lat, srid=4326), D(km=5)))
