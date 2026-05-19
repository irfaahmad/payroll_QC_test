# Part of MHC. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    l10n_ca_qc_sin = fields.Char(
        string="Social Insurance Number (SIN)",
        groups="hr.group_hr_user",
    )
    l10n_ca_qc_tp1015_claim_code = fields.Selection(
        selection=[
            ('1', 'Claim Code 1 (Basic Personal Amount Only)'),
            ('2', 'Claim Code 2'),
            ('3', 'Claim Code 3'),
            ('4', 'Claim Code 4'),
            ('5', 'Claim Code 5'),
            ('6', 'Claim Code 6'),
            ('7', 'Claim Code 7'),
            ('8', 'Claim Code 8'),
            ('9', 'Claim Code 9'),
            ('10', 'Claim Code 10'),
            ('X', 'Claim Code X (No Withholding)'),
            ('0', 'Claim Code 0 (No Claim Amount)'),
        ],
        string="Federal TD1 Claim Code",
        default='1',
        groups="hr.group_hr_user",
        help="Federal TD1 personal tax credits claim code for this employee. "
             "This employee-level default may be overridden by the value on the "
             "active contract/version (l10n_ca_qc_td1_claim_code).",
    )
    l10n_ca_qc_vacation_accrual_ids = fields.One2many(
        comodel_name='l10n_ca_qc.vacation.accrual',
        inverse_name='employee_id',
        string="Vacation Pay Accrual",
        groups="hr_payroll.group_hr_payroll_user",
    )
    l10n_ca_qc_garnishment_ids = fields.One2many(
        comodel_name='l10n_ca_qc.garnishment',
        inverse_name='employee_id',
        string="Garnishments",
        groups="hr_payroll.group_hr_payroll_user",
    )

