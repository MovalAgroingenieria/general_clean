# -*- coding: utf-8 -*-
# 2023 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class TrialBalanceReportCompute(models.TransientModel):
    """ Here, we just define methods.
    For class fields, go more top at this file.
    """

    _inherit = 'report_trial_balance_qweb'

    def _add_account_group_account_values(self):
        """Compute values for report_trial_balance_qweb_account group in
        child."""
        query_update_account_group = """
DROP AGGREGATE IF EXISTS array_concat_agg(anycompatiblearray);
CREATE AGGREGATE array_concat_agg(anycompatiblearray) (
  SFUNC = array_cat,
  STYPE = anycompatiblearray
);
WITH aggr AS(WITH computed AS (WITH RECURSIVE cte AS (
   SELECT account_group_id, account_group_id AS parent_id,
    ARRAY[account_id]::int[] as child_account_ids
   FROM   report_trial_balance_qweb_account
   WHERE report_id = %s
   GROUP BY report_trial_balance_qweb_account.id

   UNION  ALL
   SELECT c.account_group_id, p.account_group_id, ARRAY[p.account_id]::int[]
   FROM   cte c
   JOIN   report_trial_balance_qweb_account p USING (parent_id)
    WHERE p.report_id = %s
)
SELECT account_group_id,
    array_concat_agg(DISTINCT child_account_ids)::int[] as child_account_ids
FROM   cte
GROUP BY cte.account_group_id, cte.child_account_ids
ORDER BY account_group_id
)
SELECT account_group_id,
    array_concat_agg(DISTINCT child_account_ids)::int[]
        AS child_account_ids from computed
GROUP BY account_group_id)
UPDATE report_trial_balance_qweb_account
SET child_account_ids = aggr.child_account_ids
FROM aggr
WHERE report_trial_balance_qweb_account.account_group_id =
    aggr.account_group_id
    AND report_trial_balance_qweb_account.report_id = %s
"""
        query_update_account_params = (self.id, self.id, self.id,)
        self.env.cr.execute(query_update_account_group,
                            query_update_account_params)
