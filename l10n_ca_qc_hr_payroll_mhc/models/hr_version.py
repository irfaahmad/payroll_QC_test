# Part of MHC. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

_PAY_FREQUENCY_SELECTION = [
    ('weekly', 'Weekly (52 periods/year)'),
    ('bi_weekly', 'Bi-Weekly (26 periods/year)'),
    ('semi_monthly', 'Semi-Monthly (24 periods/year)'),
    ('monthly', 'Monthly (12 periods/year)'),
]

_PAY_PERIODS_MAP = {
    'weekly': 52,
    'bi_weekly': 26,
    'semi_monthly': 24,
    'monthly': 12,
}


class HrVersion(models.Model):
    _inherit = 'hr.version'

    l10n_ca_qc_qpp_exempt = fields.Boolean(
        string="QPP Exempt",
        help="Check if this employee is exempt from Quebec Pension Plan contributions.",
    )
    l10n_ca_qc_ei_exempt = fields.Boolean(
        string="EI Exempt",
        help="Check if this employee is exempt from Employment Insurance premiums.",
    )
    l10n_ca_qc_qpip_exempt = fields.Boolean(
        string="QPIP Exempt",
        help="Check if this employee is exempt from Quebec Parental Insurance Plan premiums.",
    )
    l10n_ca_qc_additional_fed_tax = fields.Float(
        string="Additional Federal Tax Deduction",
        help="Additional amount of federal tax to deduct per pay period (from TD1 Section 2).",
    )
    l10n_ca_qc_additional_prov_tax = fields.Float(
        string="Additional Provincial Tax Deduction",
        help="Additional amount of Quebec provincial tax to deduct per pay period (from TP-1015.3).",
    )
    l10n_ca_qc_pay_frequency = fields.Selection(
        selection=_PAY_FREQUENCY_SELECTION,
        string="Pay Frequency",
        default='bi_weekly',
        required=True,
        help="Number of pay periods per year. Determines how annual amounts are prorated per period.",
    )
    l10n_ca_qc_pay_periods = fields.Integer(
        string="Pay Periods per Year",
        compute='_compute_pay_periods',
        store=True,
        help="Computed number of pay periods per year based on the selected pay frequency.",
    )
    l10n_ca_qc_td1_claim_code = fields.Selection(
        selection=[
            ('1', 'Code 1 — Basic personal amount only'),
            ('2', 'Code 2'),
            ('3', 'Code 3'),
            ('4', 'Code 4'),
            ('5', 'Code 5'),
            ('6', 'Code 6'),
            ('7', 'Code 7'),
            ('8', 'Code 8'),
            ('9', 'Code 9'),
            ('10', 'Code 10 — Maximum claim'),
            ('X', 'Code X — No withholding'),
            ('0', 'Code 0 — No credits claimed'),
        ],
        string="Federal TD1 Claim Code",
        default='1',
        help="Federal TD1 personal tax credits return claim code.",
    )
    l10n_ca_qc_tp1015_claim_code = fields.Selection(
        selection=[
            ('A', 'Code A — Basic personal amount only'),
            ('B', 'Code B'),
            ('C', 'Code C'),
            ('D', 'Code D'),
            ('E', 'Code E'),
            ('F', 'Code F'),
            ('G', 'Code G'),
            ('H', 'Code H'),
            ('I', 'Code I'),
            ('J', 'Code J — Maximum claim'),
            ('X', 'Code X — No withholding'),
            ('0', 'Code 0 — No credits claimed'),
        ],
        string="Quebec TP-1015.3 Claim Code",
        default='A',
        help="Quebec TP-1015.3 provincial personal tax credits return claim code.",
    )
    l10n_ca_qc_cnesst_classification = fields.Char(
        string="CNESST Industry Classification",
        help="CNESST industry classification code for workers' compensation rate determination.",
    )
    l10n_ca_qc_cnesst_rate = fields.Float(
        string="CNESST Rate Override (%)",
        digits=(6, 4),
        help="Custom CNESST rate for this employee. Leave 0 to use the default company/industry rate.",
    )

    @api.depends('l10n_ca_qc_pay_frequency')
    def _compute_pay_periods(self):
        for version in self:
            version.l10n_ca_qc_pay_periods = _PAY_PERIODS_MAP.get(
                version.l10n_ca_qc_pay_frequency, 26
            )
