# Part of MHC. See LICENSE file for full copyright and licensing details.
"""Auto-flip hr.payslip → 'paid' when its payable line is fully reconciled.

Why this is needed
------------------
Odoo's stock ``account.move.payment_state`` only computes for invoice / bill
move types (``out_invoice``, ``in_invoice``, etc.).  Payroll posts a plain
journal entry (``move_type='entry'``), so ``payment_state`` stays
``not_paid`` forever and the standard hr_payroll_account flow never flips
the payslip from ``validated`` to ``paid``.

What this does
--------------
After every reconcile, look at the moves involved.  For any move linked to a
validated ``hr.payslip``, check whether all ``liability_payable`` lines have
zero residual.  If they do, call the payslip's existing
``action_payslip_paid()`` to update state and ``paid_date``.

Why this is safe
----------------
* Only fires on payslips currently in state ``validated``.
* Re-uses the upstream ``action_payslip_paid()`` which already validates
  state, error_count, and writes paid_date.
* Filters to ``account_type == 'liability_payable'`` so other reconciled
  lines on the same move (clearing 2380, CRA payables 2310/.., etc.) do not
  prematurely trigger the transition.  In our chart only 2390 is
  ``liability_payable`` and it carries the per-employee net pay.
"""
from odoo import models


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    def reconcile(self):
        result = super().reconcile()
        self._l10n_ca_sync_payslip_state()
        return result

    def _l10n_ca_sync_payslip_state(self):
        if not self:
            return
        Payslip = self.env['hr.payslip']
        moves = self.mapped('move_id')
        if not moves:
            return
        payslips = Payslip.search([
            ('move_id', 'in', moves.ids),
            ('state', '=', 'validated'),
        ])
        for ps in payslips:
            payable_lines = ps.move_id.line_ids.filtered(
                lambda l: l.account_id.account_type == 'liability_payable'
            )
            if not payable_lines:
                continue
            if all(
                l.company_currency_id.is_zero(l.amount_residual)
                for l in payable_lines
            ):
                ps.action_payslip_paid()
