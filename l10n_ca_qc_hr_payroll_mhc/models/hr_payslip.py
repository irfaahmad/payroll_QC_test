# Part of MHC. See LICENSE file for full copyright and licensing details.

from odoo import models


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    def _get_paid_amount(self):
        self.ensure_one()
        if self.struct_id.country_id.code == 'CA':
            total = sum(line.amount for line in self.worked_days_line_ids if line.code in ('WORK100', 'LEAVE90'))
            return total if total > 0 else super()._get_paid_amount()

    def action_payslip_done(self):
        """Extend payslip confirmation to auto-update QC-specific accumulators.

        After the standard payslip confirmation logic runs we:
        1. Add the ``VAC_ACCRUAL_QC`` amount to the employee's vacation accrual balance.
        2. Add the ``GARNISH_QC`` amount deducted to each active garnishment's
           ``total_deducted`` field, distributing proportionally when multiple active
           garnishments exist.
        """
        res = super().action_payslip_done()
        for payslip in self:
            self._update_vacation_accrual(payslip)
            self._update_garnishment_totals(payslip)
        return res

    def _update_vacation_accrual(self, payslip):
        """Credit the vacation accrual record for the payslip's employer accrual amount."""
        accrual_line = payslip.line_ids.filtered(lambda l: l.code == 'VAC_ACCRUAL_QC')
        if not accrual_line:
            return
        accrual_amount = sum(accrual_line.mapped('total'))
        if not accrual_amount:
            return

        accrual_record = self.env['l10n_ca_qc.vacation.accrual'].search(
            [
                ('employee_id', '=', payslip.employee_id.id),
                ('company_id', '=', payslip.company_id.id),
            ], limit=1
        )
        if accrual_record:
            accrual_record.update_accrual_from_payslip(payslip)
        else:
            self.env['l10n_ca_qc.vacation.accrual'].create({
                'employee_id': payslip.employee_id.id,
                'company_id': payslip.company_id.id,
                'accrued_amount': accrual_amount,
                'last_updated': payslip.date_to,
            })

    def _update_garnishment_totals(self, payslip):
        """Update ``total_deducted`` on each active garnishment.

        Replicates the GARNISH_QC salary rule logic so each garnishment receives
        the exact amount it was responsible for computing, using the payslip's
        confirmed line amounts to reconstruct the disposable net at each step.
        """
        garnish_line = payslip.line_ids.filtered(lambda l: l.code == 'GARNISH_QC')
        if not garnish_line:
            return
        total_garnish = abs(sum(garnish_line.mapped('total')))
        if not total_garnish:
            return

        ref_date = payslip.date_from
        active_garnishments = payslip.employee_id.l10n_ca_qc_garnishment_ids.filtered(
            lambda g: g.active
            and g.start_date <= ref_date
            and (not g.end_date or g.end_date >= ref_date)
        ).sorted('priority')

        if not active_garnishments:
            return

        # Reconstruct net_so_far at the time GARNISH_QC was evaluated, mirroring
        # exactly the computation performed in the salary rule.
        line_totals = {l.code: l.total for l in payslip.line_ids}
        net_so_far = (
            line_totals.get('GROSS_QC', 0)
            + line_totals.get('RRSP_QC', 0)
            + line_totals.get('RPP_QC', 0)
            + line_totals.get('UNION_QC', 0)
            + line_totals.get('QPP_EE', 0)
            + line_totals.get('QPP2_EE', 0)
            + line_totals.get('QPIP_EE', 0)
            + line_totals.get('EI_EE_QC', 0)
            + line_totals.get('FED_TAX_QC', 0)
            + line_totals.get('PROV_TAX_QC', 0)
        )

        for garnishment in active_garnishments:
            exempt = garnishment.exempt_amount or 0
            disposable = max(net_so_far - exempt, 0)
            if garnishment.is_percentage:
                portion = disposable * garnishment.percentage
            else:
                portion = garnishment.amount
            portion = min(portion, disposable)

            garnishment.total_deducted += portion
            # Reduce the available net for subsequent (lower-priority) garnishments
            net_so_far -= portion

            if garnishment.balance_remaining > 0:
                garnishment.balance_remaining = max(
                    garnishment.balance_remaining - portion, 0
                )
                if garnishment.balance_remaining == 0:
                    garnishment.active = False
