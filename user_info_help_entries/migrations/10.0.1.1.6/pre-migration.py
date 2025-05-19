# -*- coding: utf-8 -*-

def migrate(cr, version):
    # Remove the record from the main table
    cr.execute("""
        DELETE FROM user_menu_help_entry
        WHERE id IN (SELECT res_id FROM ir_model_data
                     WHERE module = 'user_info_help_entries'
                     AND name = 'help_entry_9');
    """)

    # Remove the reference from ir_model_data
    cr.execute("""
        DELETE FROM ir_model_data
        WHERE module = 'user_info_help_entries'
        AND name = 'help_entry_9';
    """)
    
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
        'help_entry_9',
        'user.menu.help.entry',
        False,
        'https://odoo.moval.es/my/document_pages',
        'user_menu_help_entry',
        'help_entry_9',
    ))