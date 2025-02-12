# -*- coding: utf-8 -*-

def migrate(cr, version):
    # Remove the record from the main table
    cr.execute("""
        DELETE FROM user_menu_help_entry
        WHERE id IN (SELECT res_id FROM ir_model_data
                     WHERE module = 'user_info_help_entries'
                     AND name = 'help_entry_2');
    """)

    # Remove the reference from ir_model_data
    cr.execute("""
        DELETE FROM ir_model_data
        WHERE module = 'user_info_help_entries'
        AND name = 'help_entry_2';
    """)
