# -*- coding: utf-8 -*-

def migrate(cr, version):
    cr.execute("""
        UPDATE ir_model_data d
        SET name = %s
        WHERE d.module = %s
          AND d.name = %s
          AND NOT EXISTS (
              SELECT 1 FROM ir_model_data
               WHERE module = %s AND name = %s
          )
    """, (
        'help_entry_9',
        'user_info_help_entries',  # tu módulo
        'help_entry_8',
        'user_info_help_entries',
        'help_entry_9',
    ))
    cr.execute("""
        UPDATE ir_model_data d
        SET name = %s
        WHERE d.module = %s
          AND d.name = %s
          AND NOT EXISTS (
              SELECT 1 FROM ir_model_data
               WHERE module = %s AND name = %s
          )
    """, (
        'help_entry_8',
        'user_info_help_entries',
        'help_entry_7',
        'user_info_help_entries',
        'help_entry_8',
    ))
    cr.execute("""
            INSERT INTO user_menu_help_entry (name, url, active)
            SELECT %s, %s, %s
            WHERE NOT EXISTS (
                SELECT 1 FROM user_menu_help_entry WHERE url = %s
            )
        """, (
        'Mis Documentos/Reuniones',
        'https://odoo.moval.es/my/document_pages',
        True,
        'https://odoo.moval.es/my/document_pages',
    ))
    
    cr.execute("""
        INSERT INTO ir_model_data (module, name, model, res_id, noupdate)
        SELECT %s, %s, %s, ume.id, %s
        FROM user_menu_help_entry AS ume
        WHERE ume.url = %s
          AND NOT EXISTS (
            SELECT 1 FROM ir_model_data
             WHERE module = %s AND name = %s
          )
    """, (
        'user_menu_help_entry',
        'help_entry_7',
        'user.menu.help.entry',
        False,
        'https://odoo.moval.es/my/document_pages',
        'user_menu_help_entry',
        'help_entry_7',
    ))
