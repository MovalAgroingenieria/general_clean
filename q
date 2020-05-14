[33mcommit 46a9a4cac78ce81bf3881c5e64305cff81ebd7a3[m[33m ([m[1;36mHEAD -> [m[1;32mjst-new-account_banking_debit_atrm-add_search_in_accounting_notes[m[33m, [m[1;31morigin/jst-new-account_banking_debit_atrm-add_search_in_accounting_notes[m[33m)[m
Author: jsandoval <jsandoval@moval.es>
Date:   Wed Apr 22 10:51:45 2020 +0200

    [NEW] account_banking_debit_atrm: Search accounting notes
     - Add new functionality to search accounting notes by ATRM ref
     - Preprare the module to import data (readonly set to false in ATRM ref) [This change is temporal]
     - Add column ATRM ref to invoice tree view
    
     (*) This commit is based in current migration master branch, however the migration commit has been
         dropped from this branch.

[1mdiff --git a/account_banking_debit_atrm/__manifest__.py b/account_banking_debit_atrm/__manifest__.py[m
[1mindex aa24ef0..a8628df 100644[m
[1m--- a/account_banking_debit_atrm/__manifest__.py[m
[1m+++ b/account_banking_debit_atrm/__manifest__.py[m
[36m@@ -23,6 +23,7 @@[m
         "views/account_invoice_view.xml",[m
         "views/account_payment_line_views.xml",[m
         "views/account_payment_order_views.xml",[m
[32m+[m[32m        "views/account_view.xml",[m
         "views/resources.xml",[m
     ],[m
     "installable": True,[m
[1mdiff --git a/account_banking_debit_atrm/i18n/es.po b/account_banking_debit_atrm/i18n/es.po[m
[1mindex ae83efc..0012c4a 100644[m
[1m--- a/account_banking_debit_atrm/i18n/es.po[m
[1m+++ b/account_banking_debit_atrm/i18n/es.po[m
[36m@@ -1529,7 +1529,7 @@[m [mmsgstr "Opciones ATRM"[m
 #. module: account_banking_debit_atrm[m
 #: model:ir.model.fields,field_description:account_banking_debit_atrm.field_bank_payment_line_atrm_ref[m
 msgid "ATRM reference"[m
[31m-msgstr "Refenrencia ATRM"[m
[32m+[m[32mmsgstr "Referencia ATRM"[m
 [m
 #. module: account_banking_debit_atrm[m
 #: model:ir.actions.report.xml,name:account_banking_debit_atrm.action_atrm_resume_report[m
[1mdiff --git a/account_banking_debit_atrm/models/account_payment_order.py b/account_banking_debit_atrm/models/account_payment_order.py[m
[1mindex b3e4fcc..f9fb954 100644[m
[1m--- a/account_banking_debit_atrm/models/account_payment_order.py[m
[1m+++ b/account_banking_debit_atrm/models/account_payment_order.py[m
[36m@@ -154,18 +154,25 @@[m [mclass AccountConfigSettings(models.TransientModel):[m
             self.agency_min_amount)[m
 [m
 [m
[32m+[m[32mclass AccountMoveLine(models.Model):[m
[32m+[m[32m    _inherit = "account.move.line"[m
[32m+[m
[32m+[m[32m    atrm_ref = fields.Char([m
[32m+[m[32m        readonly=False,[m
[32m+[m[32m        string="ATRM ref")[m
[32m+[m
 class BankPaymentLine(models.Model):[m
     _inherit = 'bank.payment.line'[m
 [m
     atrm_ref = fields.Char([m
         string="ATRM reference",[m
[31m-        readonly=True,[m
[32m+[m[32m        readonly=False,[m
         help="This number indicates the payment reference\[m
             if it has been made by ATRM.")[m
 [m
     atrm_sent = fields.Boolean([m
         string="ATRM done",[m
[31m-        readonly=True,[m
[32m+[m[32m        readonly=False,[m
         help="Indicates whether this payment has already been\[m
             added to an ATRM payment file.")[m
 [m
[36m@@ -976,6 +983,9 @@[m [mclass AccountPaymentOrder(models.Model):[m
                     # Get year[m
                     year = obligation_birthdate[4:][m
 [m
[32m+[m[32m                    # Set line_id[m
[32m+[m[32m                    line.move_line_id = l.move_line_id[m
[32m+[m
             # Get amount voluntary (equal in V, E or B)[m
             # @INFO: Has to be between max. and min. allowed[m
             #        by the agency agreement[m
[36m@@ -1307,6 +1317,11 @@[m [mclass AccountPaymentOrder(models.Model):[m
                 for bline in order.bank_line_ids:[m
                     invoice = self.env['account.invoice'].search([[m
                             ('number', '=', bline.communication)])[m
[32m+[m[32m                    move_lines = self.env['account.move.line'].search([[m
[32m+[m[32m                            ('invoice_id', '=', invoice.id)])[m
[32m+[m[32m                    if move_lines:[m
[32m+[m[32m                        for move_line in move_lines:[m
[32m+[m[32m                            move_line.atrm_ref = False[m
                     invoice.write({[m
                             'in_atrm': False,[m
                             'atrm_ref': False,[m
[1mdiff --git a/account_banking_debit_atrm/views/account_invoice_view.xml b/account_banking_debit_atrm/views/account_invoice_view.xml[m
[1mindex c43b66a..2e05e20 100644[m
[1m--- a/account_banking_debit_atrm/views/account_invoice_view.xml[m
[1m+++ b/account_banking_debit_atrm/views/account_invoice_view.xml[m
[36m@@ -27,6 +27,7 @@[m
             </xpath>[m
             <xpath expr="//field[@name='type']" position="after">[m
                 <field name="in_atrm" string="ATRM"/>[m
[32m+[m[32m                <field name="atrm_ref"/>[m
             </xpath>[m
         </field>[m
     </record>[m
[1mdiff --git a/account_banking_debit_atrm/views/account_view.xml b/account_banking_debit_atrm/views/account_view.xml[m
[1mnew file mode 100644[m
[1mindex 0000000..097514f[m
[1m--- /dev/null[m
[1m+++ b/account_banking_debit_atrm/views/account_view.xml[m
[36m@@ -0,0 +1,15 @@[m
[32m+[m[32m<?xml version="1.0" encoding="utf-8"?>[m
[32m+[m[32m<odoo>[m
[32m+[m
[32m+[m[32m    <record id="view_account_move_line_filter" model="ir.ui.view">[m
[32m+[m[32m        <field name="name">Journal Items (search view)</field>[m
[32m+[m[32m        <field name="model">account.move.line</field>[m
[32m+[m[32m        <field name="inherit_id" ref="account.view_account_move_line_filter"/>[m
[32m+[m[32m        <field name="arch" type="xml">[m
[32m+[m[32m            <xpath expr="//field[@name='tax_ids']" position="after">[m
[32m+[m[32m                <field name="atrm_ref"/>[m
[32m+[m[32m            </xpath>[m
[32m+[m[32m        </field>[m
[32m+[m[32m    </record>[m
[32m+[m
[32m+[m[32m</odoo>[m
\ No newline at end of file[m
