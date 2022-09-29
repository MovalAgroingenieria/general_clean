# 2022 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import re
import requests
import io
import base64
from odoo import models, fields, api


class SimplegisModel(models.AbstractModel):
    _name = 'simplegis.model'
    _description = 'Simple-GIS Model'

    # Linked GIS table ("wua_gis_parcel", for example).
    _gis_table = ''

    # "geom" field.
    _geom_field = 'geom'

    # Field for link.
    _link_field = 'name'

    geom_ewkt = fields.Char(
        string='EWKT Geometry',
        compute='_compute_geom_ewkt')

    simplified_geom_ewkt = fields.Char(
        string='EWKT Geometry based on integer values',
        compute='_compute_simplified_geom_ewkt')

    oriented_envelope_ewkt = fields.Char(
        string='EWKT Geometry for oriented envelope',
        compute='_compute_oriented_envelope_ewkt')

    def _compute_geom_ewkt(self):
        geom_ok = self._geom_ok()
        for record in self:
            geom_ewkt = ''
            if geom_ok:
                self.env.cr.execute("""
                    SELECT postgis.st_asewkt(""" + self._geom_field + """)
                    FROM """ + self._gis_table + """
                    WHERE """ + self._link_field + """='""" + record.name + """'""")
                query_results = self.env.cr.dictfetchall()
                if (query_results and
                   query_results[0].get('st_asewkt') is not None):
                    geom_ewkt = query_results[0].get('st_asewkt')
            record.geom_ewkt = geom_ewkt

    def _compute_simplified_geom_ewkt(self):
        for record in self:
            simplified_geom_ewkt = ''
            geom_ewkt = record.geom_ewkt
            if geom_ewkt:
                simplified_geom_ewkt = \
                    re.sub(r'\d+\.\d{1,}', lambda m: str(
                        int(round(float(m.group(0))))), geom_ewkt)
            record.simplified_geom_ewkt = simplified_geom_ewkt

    def _compute_oriented_envelope_ewkt(self):
        geom_ok = self._geom_ok()
        for record in self:
            oriented_envelope_ewkt = ''
            if geom_ok:
                self.env.cr.execute("""
                    SELECT postgis.st_asewkt(postgis.st_orientedenvelope(""" + self._geom_field + """))
                    FROM """ + self._gis_table + """
                    WHERE """ + self._link_field + """='""" + record.name + """'""")
                query_results = self.env.cr.dictfetchall()
                if (query_results and
                   query_results[0].get('st_asewkt') is not None):
                    oriented_envelope_ewkt = query_results[0].get('st_asewkt')
            record.oriented_envelope_ewkt = oriented_envelope_ewkt

    def _geom_ok(self):
        resp = True
        try:
            self.env.cr.execute(
                'SELECT ' + self._link_field + ', ' + self._geom_field + ' ' +
                'FROM ' + self._gis_table + ' LIMIT 1')
        except Exception:
            resp = False
        return resp

    @api.model
    def extract_coordinates(self, geom_ewkt):
        srid = ''
        coordinates = ''
        if geom_ewkt:
            pos_semicolon = geom_ewkt.find(';')
            if pos_semicolon != -1 and pos_semicolon < len(geom_ewkt) - 1:
                coordinates = geom_ewkt[pos_semicolon + 1:]
                srid_temp = geom_ewkt[0:pos_semicolon]
                pos_equal = srid_temp.find('=')
                if pos_equal and pos_equal < len(srid_temp) - 1:
                    srid = srid_temp[pos_equal + 1:]
                if not srid:
                    coordinates = ''
        return srid, coordinates

    @api.model
    def extract_bounding_box(self, geom_ewkt):
        bounding_box = []
        srid, coordinates = self.extract_coordinates(geom_ewkt)
        if coordinates:
            coordinates = coordinates.lower()
            points = ''
            if coordinates.find('multipolygon') != -1:
                points = \
                    re.search(r'\(\(\((.*?)\)\)\)', coordinates).group(1)
            elif coordinates.find('polygon') != -1:
                points = \
                    re.search(r'\(\((.*?)\)\)', coordinates).group(1)
            if points:
                points = points.replace('),(', ', ').replace('), (', ', ')
                points = points.replace(', ', ',')
                list_of_points = points.split(',')
                first_point = True
                for point in list_of_points:
                    coordinates = point.split(' ')
                    if len(coordinates) == 2:
                        x = float(coordinates[0])
                        y = float(coordinates[1])
                        if first_point:
                            first_point = False
                            minx = x
                            maxx = x
                            miny = y
                            maxy = y
                        else:
                            if x < minx:
                                minx = x
                            if x > maxx:
                                maxx = x
                            if y < miny:
                                miny = y
                            if y > maxy:
                                maxy = y
                bounding_box = [minx, miny, maxx, maxy]
        return srid, bounding_box

    @api.model
    def extension_and_schema_postgis_created(self):
        resp = False
        self.env.cr.execute("""
            SELECT EXISTS(SELECT * FROM pg_extension WHERE extname='postgis')
            AND EXISTS(SELECT * FROM information_schema.schemata WHERE
            schema_name='postgis')""")
        if self.env.cr.fetchone()[0]:
            resp = True
        return resp

    @api.model
    def create_gis_table(self, gis_table,
                         geom_type='MULTIPOLYGON', epsg=25830):
        if not self._existing_gis_table(gis_table):
            gis_sequence = gis_table + '_gid_seq'
            gis_pkey = gis_table + '_pkey'
            gis_epsg = str(epsg)
            gis_index = gis_table + '_idx'
            self.env.cr.execute("""
                CREATE SEQUENCE IF NOT EXISTS
                    public.""" + gis_sequence + """
                    INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647
                    CACHE 1;""")
            self.env.cr.execute("""
                CREATE TABLE IF NOT EXISTS
                    public.""" + gis_table + """(gid INTEGER NOT NULL
                    DEFAULT nextval('""" + gis_sequence + """'::regclass),
                    name CHARACTER VARYING(254) NOT NULL
                    COLLATE pg_catalog."default",
                    geom postgis.GEOMETRY
                    (""" + geom_type + """,""" + gis_epsg + """),
                    UNIQUE(name), CHECK (name <> ''),
                    CONSTRAINT """ + gis_pkey + """ PRIMARY KEY (gid));""")
            self.env.cr.execute("""
                CREATE INDEX
                IF NOT EXISTS """ + gis_index + """ ON
                public.""" + gis_table + """ USING gist (geom);""")
            self.env.cr.commit()

    def _existing_gis_table(self, gis_table):
        resp = False
        self.env.cr.execute("""
            SELECT EXISTS(SELECT * FROM information_schema.tables
            WHERE table_name='""" + gis_table + """')""")
        if self.env.cr.fetchone()[0]:
            resp = True
        return resp

    def get_aerial_image(self,
                         image_wms='https://www.ign.es/wms-inspire/pnoa-ma',
                         image_layers='OI.OrthoimageCoverage',
                         image_styles='default',
                         image_width=0,
                         image_height=824,
                         image_format='jpeg',
                         image_zoom=1.2):
        aerial_images = []
        # Provisional
        # print(image_wms)
        # print(image_layers)
        # print(image_styles)
        # print(image_width)
        # print(image_height)
        # print(image_format)
        # print(image_zoom)
        for record in self:
            image = None
            srid, bounding_box = record.extract_bounding_box(
                record.geom_ewkt)
            if srid and bounding_box:
                minx = bounding_box[0]
                miny = bounding_box[1]
                maxx = bounding_box[2]
                maxy = bounding_box[3]
                image_width_meters = maxx - minx
                image_height_meters = maxy - miny
                if (image_width_meters > 0 and image_height_meters > 0 and
                   image_zoom > 0 and image_zoom != 1):
                    new_image_width_meters = \
                        image_width_meters * image_zoom
                    new_image_height_meters = \
                        image_height_meters * image_zoom
                    dif_width_meters = \
                        new_image_width_meters - image_width_meters
                    dif_height_meters = \
                        new_image_height_meters - image_height_meters
                    offset_width_meters = dif_width_meters / 2
                    offset_height_meters = dif_height_meters / 2
                    minx = minx - offset_width_meters
                    miny = miny - offset_height_meters
                    maxx = maxx + offset_width_meters
                    maxy = maxy + offset_height_meters
                minx = int(round(minx))
                miny = int(round(miny))
                maxx = int(round(maxx))
                maxy = int(round(maxy))
                image_width_meters = maxx - minx
                image_height_meters = maxy - miny
                image_height_pixels = image_height
                image_width_pixels = image_width
                if image_width_pixels == 0 and image_height_pixels == 0:
                    image_width_pixels = 100
                    image_height_pixels = 100
                if image_width_pixels == 0 or image_height_pixels == 0:
                    if image_width_pixels == 0:
                        image_width_pixels = int(round((
                            image_width_meters * image_height_pixels) /
                            image_height_meters))
                    else:
                        image_height_pixels = int(round((
                            image_height_meters * image_width_pixels) /
                            image_width_meters))
                url = image_wms + '?service=wms' + \
                    '&version=1.3.0&request=getmap&crs=epsg:' + str(srid) + \
                    '&bbox=' + str(minx) + ',' + str(miny) + ',' + \
                    str(maxx) + ',' + str(maxy) + \
                    '&width=' + str(image_width_pixels) + \
                    '&height=' + str(image_height_pixels) + \
                    '&layers=' + image_layers + \
                    '&styles=' + image_styles + \
                    '&format=image/' + image_format
                request_ok = True
                try:
                    resp = requests.get(url, stream=True)
                except Exception:
                    request_ok = False
                if request_ok and resp.status_code == 200:
                    image_raw = io.BytesIO(resp.raw.read())
                    image = base64.b64encode(image_raw.getvalue())
            aerial_images.append(image)
        if (all(i is None for i in aerial_images)):
            return None
        else:
            if len(aerial_images) == 1:
                aerial_images = aerial_images[0]
        return aerial_images
