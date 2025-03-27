# -*- coding: utf-8 -*-
# 2025 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, exceptions, _


class GisTable(models.Model):
    _name = 'gis.table'
    _description = 'GIS Table'

    def _default_field_ids(self):
        return [(0, 0, {
            'name': 'gid',
            'field_type': 'bigint',
            'required': True,
            'readonly': True,
            'is_synced': False,
        }), (0, 0, {
            'name': 'geom',
            'field_type': 'geometry',
            'geometry_type': 'POINT',
            'epsg': '4326',
            'required': False,
            'readonly': True,
            'is_synced': False,
        })]

    name = fields.Char(
        string='Table Name',
        required=True,
    )

    description = fields.Text(
        string='Description',
    )

    related_model_id = fields.Many2one(
        string='Related Odoo Model',
        comodel_name='ir.model',
    )

    relation_field_id = fields.Many2one(
        string='Relation Field (Odoo Model)',
        comodel_name='ir.model.fields',
    )

    relation_gis_field_id = fields.Many2one(
        string='Relation Field (GIS Table)',
        comodel_name='gis.table.field',
    )

    field_ids = fields.One2many(
        string='Fields',
        comodel_name='gis.table.field',
        inverse_name='gis_table_id',
        default=lambda self: self._default_field_ids(),
    )

    readonly = fields.Boolean(
        string='Read Only (DB-level)',
        readonly=True,
        help='If checked, the table cannot be deleted',
    )

    is_synced = fields.Boolean(
        string='Synchronized with DB',
        default=False,
        readonly=True,
    )

    _sql_constraints = [
        ('unique_name', 'UNIQUE (name)',
         'Table Name must be unique.'),
    ]

    def _map_pg_type_to_field_type(self, pg_type):
        mapping = {
            'bigint': 'bigint',
            'integer': 'bigint',
            'numeric': 'numeric',
            'double precision': 'numeric',
            'real': 'numeric',
            'character varying': 'varchar',
            'varchar': 'varchar',
            'character': 'varchar',
            'text': 'text',
            'date': 'date',
            'timestamp without time zone': 'timestamp',
            'timestamp with time zone': 'timestamp',
            'boolean': 'boolean',
            'geometry': 'geometry',
            # Risky, but we are not going to support all possible types
            'USER-DEFINED': 'geometry',
        }
        return mapping.get(pg_type, 'varchar')

    @api.model
    def load_gis_tables_from_db(self):
        cr = self.env.cr
        cr.execute("""
            SELECT f_table_name, f_geometry_column, type, srid
            FROM geometry_columns WHERE srid > 0 AND type IN
            ('POINT', 'LINESTRING', 'POLYGON', 'MULTIPOINT',
             'MULTILINESTRING', 'MULTIPOLYGON');
        """)
        tables = cr.fetchall()
        for table_name, geom_column, geom_type, srid in tables:
            existing = self.search([('name', '=', table_name)])
            if not existing:
                gis_table = self.create({
                    'name': table_name,
                    'description': 'Imported automatically from PostGIS',
                    'is_synced': True,
                })
                cr.execute("""
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns
                    WHERE table_name = %s;
                """, (table_name,))
                columns = cr.fetchall()
                for column_name, data_type, is_nullable in columns:
                    field_type = self._map_pg_type_to_field_type(data_type)
                    readonly = column_name in ('gid', geom_column)
                    vals_field = {
                        'gis_table_id': gis_table.id,
                        'name': column_name,
                        'field_type': field_type,
                        'required': (is_nullable == 'NO'),
                        'readonly': readonly,
                        'is_synced': True,
                    }
                    if column_name == geom_column:
                        vals_field.update({
                            'geometry_type': geom_type,
                            'epsg': srid,
                            'field_type': 'geometry',
                        })
                    self.env['gis.table.field'].create(vals_field)
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    def action_sync_table(self):
        cr = self.env.cr
        for table in self:
            try:
                cr.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables
                        WHERE table_name = %s
                    );
                """, (table.name,))
                exists = cr.fetchone()[0]
                if exists:
                    table.write({'is_synced': True})
                else:
                    create_stmt = 'CREATE TABLE %s ();' % table.name
                    cr.execute(create_stmt)
                    table.write({'is_synced': True})
            except Exception as e:
                raise exceptions.UserError(_(
                    'Failed to sync table: %s') % str(e))

    def action_drop_table(self):
        cr = self.env.cr
        for table in self:
            if table.readonly:
                raise exceptions.UserError(_(
                    'Cannot drop a readonly table.'))
            try:
                cr.execute('DROP SEQUENCE IF EXISTS %s_gid_seq CASCADE;' %
                           table.name)
                cr.execute('DROP INDEX IF EXISTS %s_geom_idx CASCADE;' %
                           table.name)
                cr.execute('DROP TABLE %s CASCADE;' % table.name)
                table.unlink()
            except Exception as e:
                raise exceptions.UserError(_(
                    'Failed to drop table: %s') % str(e))

    def action_push_fields_to_db(self):
        cr = self.env.cr
        for table in self:
            cr.execute("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = %s;
            """, (table.name,))
            db_columns = {row[0]: row for row in cr.fetchall()}
            for field in table.field_ids:
                column_name = field.name
                if column_name not in db_columns:
                    # New field -> ADD COLUMN
                    handled = False
                    if field.name == 'gid':
                        sequence_name = '%s_gid_seq' % table.name
                        try:
                            cr.execute("""
                                CREATE SEQUENCE IF NOT EXISTS public.%s
                                    INCREMENT 1 START 1 MINVALUE 1
                                    MAXVALUE 2147483647 CACHE 1;
                            """ % sequence_name)
                            cr.execute("""
                                ALTER TABLE %s ADD COLUMN gid integer NOT NULL
                                DEFAULT nextval('%s'::regclass);
                            """ % (table.name, sequence_name))
                            cr.execute("""
                                ALTER TABLE %s ADD PRIMARY KEY (gid);
                            """ % table.name)
                            field.write({'is_synced': True})
                            handled = True
                        except Exception as e:
                            raise exceptions.UserError(_(
                                'Failed to create gid field in DB: %s') %
                                str(e))
                    if not handled and field.name == 'geom':
                        column_def = 'geom geometry(%s, %s)' % (
                            field.geometry_type, field.epsg)
                        try:
                            cr.execute('ALTER TABLE %s ADD COLUMN %s;' % (
                                table.name, column_def))
                            index_name = '%s_geom_idx' % table.name
                            cr.execute("""
                                CREATE INDEX IF NOT EXISTS %s
                                ON %s USING GIST (geom);
                            """ % (index_name, table.name))
                            field.write({'is_synced': True})
                            handled = True
                        except Exception as e:
                            raise exceptions.UserError(_(
                                'Failed to create geom field in DB: %s') %
                                str(e))
                    if not handled:
                        column_def = column_name + ' '
                        if field.field_type == 'varchar':
                            column_def += 'VARCHAR'
                        elif field.field_type == 'geometry':
                            column_def += 'geometry(%s, %s)' % (
                                field.geometry_type, field.epsg)
                        else:
                            column_def += field.field_type.upper()
                        if field.required:
                            column_def += ' NOT NULL'
                        try:
                            cr.execute('ALTER TABLE %s ADD COLUMN %s;' % (
                                table.name, column_def))
                            field.write({'is_synced': True})
                        except Exception as e:
                            raise exceptions.UserError(_(
                                'Failed to add field to DB: %s') % str(e))
                else:
                    db_type = db_columns[column_name][1]
                    db_required = db_columns[column_name][2] == 'NO'
                    current_type = table._map_pg_type_to_field_type(db_type)
                    alter_type_needed = current_type != field.field_type
                    alter_required_needed = db_required != field.required
                    if alter_type_needed or alter_required_needed:
                        try:
                            if alter_type_needed and field.field_type != \
                                    'geometry':
                                cr.execute(
                                    'ALTER TABLE %s ALTER COLUMN %s '
                                    'TYPE %s;' % (
                                        table.name,
                                        column_name,
                                        field.field_type.upper(),
                                    ),
                                )
                            if alter_required_needed:
                                cr.execute(
                                    'ALTER TABLE %s ALTER COLUMN %s %s '
                                    'NOT NULL;' % (
                                        table.name,
                                        column_name,
                                        'SET' if field.required else 'DROP',
                                    ),
                                )
                        except Exception as e:
                            raise exceptions.UserError(_(
                                'Failed to alter field in DB: %s') % str(e))

    def action_import_fields_from_db(self):
        cr = self.env.cr
        for table in self:
            cr.execute("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = %s;
            """, (table.name,))
            db_columns = {row[0]: row for row in cr.fetchall()}
            local_fields = {f.name: f for f in table.field_ids}
            for col_name, (column_name, data_type, is_nullable) in \
                    db_columns.items():
                field_type = self._map_pg_type_to_field_type(data_type)
                required = is_nullable == 'NO'
                if col_name in local_fields:
                    field = local_fields[col_name]
                    updates = {}
                    if field.field_type != field_type:
                        updates['field_type'] = field_type
                    if field.required != required:
                        updates['required'] = required
                    if not field.is_synced:
                        updates['is_synced'] = True
                    if updates:
                        field.write(updates)
                else:
                    self.env['gis.table.field'].create({
                        'gis_table_id': table.id,
                        'name': column_name,
                        'field_type': field_type,
                        'required': required,
                        'readonly': column_name in ('gid',),
                        'is_synced': True,
                    })
            for field_name, field in local_fields.items():
                if field_name not in db_columns and field.is_synced:
                    field.write({'is_synced': False})


class GisTableField(models.Model):
    _name = 'gis.table.field'
    _description = 'GIS Table Field'

    gis_table_id = fields.Many2one(
        string='GIS Table',
        comodel_name='gis.table',
        required=True,
        ondelete='cascade',
    )

    name = fields.Char(
        string='Field Name',
        required=True,
    )

    field_type = fields.Selection(
        string='PostgreSQL Field Type',
        selection=[
            ('bigint', 'BigInt'),
            ('numeric', 'Numeric'),
            ('varchar', 'Varchar'),
            ('text', 'Text'),
            ('date', 'Date'),
            ('timestamp', 'Timestamp'),
            ('boolean', 'Boolean'),
            ('geometry', 'Geometry'),
        ],
        required=True,
    )

    required = fields.Boolean(
        string='Required (NOT NULL)',
        default=False,
    )

    readonly = fields.Boolean(
        string='Read Only (DB-level)',
        readonly=True,
        default=False,
    )

    is_synced = fields.Boolean(
        string='Synchronized with DB',
        default=False,
        readonly=True,
    )

    geometry_type = fields.Selection(
        selection=[
            ('POINT', 'Point'),
            ('LINESTRING', 'LineString'),
            ('POLYGON', 'Polygon'),
            ('MULTIPOINT', 'MultiPoint'),
            ('MULTILINESTRING', 'MultiLineString'),
            ('MULTIPOLYGON', 'MultiPolygon'),
        ],
        string='Geometry Type',
    )

    epsg = fields.Char(
        string='EPSG Code',
    )

    def write(self, vals):
        for record in self:
            if record.readonly and record.is_synced:
                raise exceptions.ValidationError(_(
                    'Cannot edit a readonly and synced field.'))
        return super(GisTableField, self).write(vals)

    def unlink(self):
        cr = self.env.cr
        for record in self:
            if record.readonly:
                raise exceptions.ValidationError(_(
                    'Cannot unlink a readonly field.'))
            if record.is_synced:
                try:
                    cr.execute('ALTER TABLE %s DROP COLUMN %s;' % (
                        record.gis_table_id.name,
                        record.name,
                    ))
                except Exception as e:
                    raise exceptions.UserError(_(
                        'Failed to drop field from DB: %s') % str(e))
        return super(GisTableField, self).unlink()
