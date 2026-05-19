# Part of MHC. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class L10nCaQcVacationAccrual(models.Model):
    _name = 'l10n_ca_qc.vacation.accrual'
    _description = 'Quebec Vacation Pay Accrual'
    _order = 'employee_id, id desc'

    employee_id = fields.Many2one(
        comodel_name='hr.employee',
        string="Employee",
        required=True,
        ondelete='cascade',
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        string="Company",
        required=True,
        default=lambda self: self.env.company,
    )
    accrual_rate = fields.Selection(
        selection=[
            ('0.04', '4% — Less than 3 years of service (2 weeks)'),
            ('0.06', '6% — 3 to 4 years of service (3 weeks)'),
            ('0.08', '8% — 5 or more years of service (4 weeks)'),
        ],
        string="Accrual Rate",
        compute='_compute_accrual_rate',
        store=True,
        readonly=False,
        help="Vacation pay accrual rate per Quebec Labour Standards Act.",
    )
    accrued_amount = fields.Float(
        string="Accrued Amount",
        digits=(16, 2),
        help="Total vacation pay accrued and not yet paid out.",
    )
    taken_amount = fields.Float(
        string="Paid Out Amount",
        digits=(16, 2),
        help="Total vacation pay that has been paid out.",
    )
    balance = fields.Float(
        string="Balance",
        digits=(16, 2),
        compute='_compute_balance',
        store=True,
        help="Remaining vacation pay balance (accrued minus paid out).",
    )
    years_of_service = fields.Float(
        string="Years of Service",
        compute='_compute_years_of_service',
        store=True,
        help="Number of years of service used to determine the accrual rate.",
    )
    last_updated = fields.Date(
        string="Last Updated",
        default=fields.Date.today,
    )

    @api.depends('employee_id')
    def _compute_years_of_service(self):
        today = fields.Date.today()
        for rec in self:
            versions = rec.employee_id.version_ids
            if versions:
                date_start = versions.mapped('date_start')
                # Filter out any False/None values
                valid_dates = [d for d in date_start if d]
                if valid_dates:       
                    hire_date = min(valid_dates)
                    delta = today - hire_date
                    rec.years_of_service = delta.days / 365.25
                else:
                    rec.years_of_service = 0.0
            else:
                rec.years_of_service = 0.0

    @api.depends('years_of_service')
    def _compute_accrual_rate(self):
        for rec in self:
            years = rec.years_of_service
            if years >= 5:
                rec.accrual_rate = '0.08'
            elif years >= 3:
                rec.accrual_rate = '0.06'
            else:
                rec.accrual_rate = '0.04'

    @api.depends('accrued_amount', 'taken_amount')
    def _compute_balance(self):
        for rec in self:
            rec.balance = rec.accrued_amount - rec.taken_amount

    def update_accrual_from_payslip(self, payslip):
        """Update accrued_amount from a confirmed payslip's VAC_ACCRUAL_QC line."""
        self.ensure_one()
        accrual_line = payslip.line_ids.filtered(lambda l: l.code == 'VAC_ACCRUAL_QC')
        if accrual_line:
            self.accrued_amount += sum(accrual_line.mapped('total'))
            self.last_updated = payslip.date_to
