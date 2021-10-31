# -*- coding: utf-8 -*-
# 2021 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import re
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

    oriented_envelope_ewkt = fields.Char(
        string='EWKT Geometry for oriented envelope',
        compute='_compute_oriented_envelope_ewkt')

    @api.multi
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

    @api.multi
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
