# Part of MHC. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class L10nCaQcRemittanceReport(models.Model):
    _name = 'l10n_ca_qc.remittance.report'
    _description = 'Quebec Payroll Remittance Report (TPZ-1015.R.14)'
    _order = 'period_end desc'

    name = fields.Char(
        string="Reference",
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: self._default_name(),
    )
    period_start = fields.Date(
        string="Period Start",
        required=True,
    )
    period_end = fields.Date(
        string="Period End",
        required=True,
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        string="Company",
        required=True,
        default=lambda self: self.env.company,
    )
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('computed', 'Computed'),
            ('submitted', 'Submitted'),
        ],
        string="Status",
        default='draft',
        required=True,
        readonly=True,
    )
    # Employee contributions
    total_qpp_ee = fields.Float(string="QPP Employee Contributions", digits=(16, 2), readonly=True)
    total_qpp_er = fields.Float(string="QPP Employer Contributions", digits=(16, 2), readonly=True)
    total_qpp2_ee = fields.Float(string="QPP2 Employee Contributions", digits=(16, 2), readonly=True)
    total_qpp2_er = fields.Float(string="QPP2 Employer Contributions", digits=(16, 2), readonly=True)
    total_qpip_ee = fields.Float(string="QPIP Employee Premiums", digits=(16, 2), readonly=True)
    total_qpip_er = fields.Float(string="QPIP Employer Premiums", digits=(16, 2), readonly=True)
    total_ei_ee = fields.Float(string="EI Employee Premiums", digits=(16, 2), readonly=True)
    total_ei_er = fields.Float(string="EI Employer Premiums", digits=(16, 2), readonly=True)
    total_fed_tax = fields.Float(string="Federal Income Tax Withheld", digits=(16, 2), readonly=True)
    total_prov_tax = fields.Float(string="Provincial Income Tax Withheld", digits=(16, 2), readonly=True)
    total_cnesst = fields.Float(string="CNESST Employer Contribution", digits=(16, 2), readonly=True)
    total_hsf = fields.Float(string="HSF Employer Contribution", digits=(16, 2), readonly=True)
    total_cnt = fields.Float(string="CNT Employer Contribution", digits=(16, 2), readonly=True)
    total_gross = fields.Float(string="Total Gross Payroll", digits=(16, 2), readonly=True)
    payslip_count = fields.Integer(string="Number of Payslips", readonly=True)

    @api.model
    def _default_name(self):
        seq = self.env['ir.sequence'].next_by_code('l10n_ca_qc.remittance.report') or '001'
        return 'REM-%s' % seq

    def action_compute(self):
        for report in self:
            payslips = self.env['hr.payslip'].search([
                ('company_id', '=', report.company_id.id),
                ('date_from', '>=', report.period_start),
                ('date_to', '<=', report.period_end),
                ('state', 'in', ['done', 'paid']),
            ])
            lines = payslips.mapped('line_ids')

            def _sum(codes, absolute=True):
                total = sum(l.total for l in lines if l.code in codes)
                return abs(total) if absolute else total

            report.total_qpp_ee = _sum(['QPP_EE'])
            report.total_qpp_er = _sum(['QPP_ER'])
            report.total_qpp2_ee = _sum(['QPP2_EE'])
            report.total_qpp2_er = _sum(['QPP2_ER'])
            report.total_qpip_ee = _sum(['QPIP_EE'])
            report.total_qpip_er = _sum(['QPIP_ER'])
            report.total_ei_ee = _sum(['EI_EE_QC'])
            report.total_ei_er = _sum(['EI_ER_QC'])
            report.total_fed_tax = _sum(['FED_TAX_QC'])
            report.total_prov_tax = _sum(['PROV_TAX_QC'])
            report.total_cnesst = _sum(['CNESST_ER'])
            report.total_hsf = _sum(['HSF_ER'])
            report.total_cnt = _sum(['CNT_ER'])
            report.total_gross = _sum(['GROSS_QC'], absolute=False)
            report.payslip_count = len(payslips)
            report.state = 'computed'

    def action_submit(self):
        self.write({'state': 'submitted'})

    def action_reset_to_draft(self):
        self.write({'state': 'draft'})
