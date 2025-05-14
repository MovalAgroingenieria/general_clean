# -*- coding: utf-8 -*-

def migrate(cr, version):
    # Change this records name to Tutoriales específicos
    cr.execute("UPDATE user_menu_help_entry SET id='help_entry_9'"
               "WHERE id=help_entry_9")
